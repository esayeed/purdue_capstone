# Database Design — Purdue Capstone E-Commerce Platform

> **Purpose:** Define the complete schema for the Azure SQL Database that powers the food distributor e-commerce platform.  
> **Database:** Microsoft SQL Server (Azure SQL Database)  
> **ORM:** Django (`mssql-django` backend)  
> **Date:** June 26, 2026

---

## 1. Design Principles

1. **Normalize to 3NF** — Reduce data duplication without over-engineering.
2. **Foreign keys with `on_delete=CASCADE` or `PROTECT`** — Prevent orphaned records where business logic requires it.
3. **Indexed search fields** — Product names, SKUs, and customer emails must be fast to query.
4. **Audit timestamps** — Every table has `created_at` and `updated_at` for traceability.
5. **Django-friendly naming** — Table names follow Django's default convention (`appname_modelname`).

---

## 2. Entity Relationship Diagram (Text)

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│    Customer     │       │    Product      │       │    Category     │
│   (accounts)    │       │   (catalog)     │       │   (taxonomy)    │
└────────┬────────┘       └────────┬────────┘       └─────────────────┘
         │                         │
         │                         │ belongs_to
         │                         ▼
         │                  ┌─────────────────┐
         │                  │  ProductImage   │
         │                  │  (assets)       │
         │                  └─────────────────┘
         │
         ▼
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│     Order       │◄──────│   OrderItem     │       │    Inventory    │
│   (transactions)│       │   (line items)  │       │   (stock levels)│
└────────┬────────┘       └─────────────────┘       └─────────────────┘
         │
         │ has_many
         ▼
┌─────────────────┐       ┌─────────────────┐
│  DeliveryTrack  │       │  OrderStatusLog │
│  (logistics)    │       │  (audit trail)  │
└─────────────────┘       └─────────────────┘
```

---

## 3. Table Specifications

### 3.1 `main_customer`
Stores registered customer accounts.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | `bigint` | PK, identity | Django default |
| `email` | `nvarchar(254)` | UNIQUE, NOT NULL | Login identifier |
| `first_name` | `nvarchar(100)` | NOT NULL | |
| `last_name` | `nvarchar(100)` | NOT NULL | |
| `phone` | `nvarchar(20)` | | Optional contact |
| `address_line1` | `nvarchar(255)` | | Shipping address |
| `address_line2` | `nvarchar(255)` | | Apartment, suite |
| `city` | `nvarchar(100)` | | |
| `state` | `nvarchar(50)` | | |
| `zip_code` | `nvarchar(20)` | | |
| `is_active` | `bit` | DEFAULT 1 | Soft-delete flag |
| `created_at` | `datetimeoffset` | DEFAULT SYSUTCDATETIME() | |
| `updated_at` | `datetimeoffset` | DEFAULT SYSUTCDATETIME() | |

**Indexes:**
- `IX_main_customer_email` (email)
- `IX_main_customer_created_at` (created_at)

---

### 3.2 `main_category`
Product taxonomy (e.g., Produce, Dairy, Meat, Beverages).

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | `bigint` | PK, identity | |
| `name` | `nvarchar(100)` | UNIQUE, NOT NULL | |
| `description` | `nvarchar(500)` | | |
| `created_at` | `datetimeoffset` | DEFAULT SYSUTCDATETIME() | |

---

### 3.3 `main_product`
The food products available for ordering.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | `bigint` | PK, identity | |
| `sku` | `nvarchar(50)` | UNIQUE, NOT NULL | Stock keeping unit |
| `name` | `nvarchar(200)` | NOT NULL | |
| `description` | `nvarchar(2000)` | | |
| `category_id` | `bigint` | FK → `main_category(id)` | |
| `unit_price` | `decimal(10,2)` | NOT NULL | Price per unit |
| `unit_of_measure` | `nvarchar(50)` | NOT NULL | lb, case, gallon, etc. |
| `is_active` | `bit` | DEFAULT 1 | |
| `created_at` | `datetimeoffset` | DEFAULT SYSUTCDATETIME() | |
| `updated_at` | `datetimeoffset` | DEFAULT SYSUTCDATETIME() | |

**Indexes:**
- `IX_main_product_sku` (sku)
- `IX_main_product_name` (name)
- `IX_main_product_category_id` (category_id)

---

### 3.4 `main_productimage`
Multiple images per product (stored in Blob Storage; this table stores metadata).

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | `bigint` | PK, identity | |
| `product_id` | `bigint` | FK → `main_product(id)`, CASCADE | |
| `image_url` | `nvarchar(500)` | NOT NULL | Blob Storage URL |
| `alt_text` | `nvarchar(255)` | | Accessibility |
| `is_primary` | `bit` | DEFAULT 0 | Thumbnail flag |
| `uploaded_at` | `datetimeoffset` | DEFAULT SYSUTCDATETIME() | |

---

### 3.5 `main_inventory`
Real-time stock levels for each product.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | `bigint` | PK, identity | |
| `product_id` | `bigint` | FK → `main_product(id)`, UNIQUE | One row per product |
| `quantity_on_hand` | `decimal(12,2)` | DEFAULT 0 | |
| `quantity_reserved` | `decimal(12,2)` | DEFAULT 0 | Committed to orders |
| `quantity_available` | `decimal(12,2)` | GENERATED | `on_hand - reserved` |
| `reorder_level` | `decimal(12,2)` | DEFAULT 0 | Low-stock alert threshold |
| `last_updated` | `datetimeoffset` | DEFAULT SYSUTCDATETIME() | |

**Business Rule:** When an order is placed, `quantity_reserved` increases. When the order ships, `quantity_reserved` decreases and `quantity_on_hand` decreases.

---

### 3.6 `main_order`
The parent order record.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | `bigint` | PK, identity | |
| `order_number` | `nvarchar(20)` | UNIQUE, NOT NULL | Human-readable (e.g., ORD-250701-0001) |
| `customer_id` | `bigint` | FK → `main_customer(id)` | |
| `status` | `nvarchar(20)` | DEFAULT 'pending' | pending, confirmed, shipped, delivered, cancelled |
| `subtotal` | `decimal(12,2)` | NOT NULL | Sum of line items |
| `tax_amount` | `decimal(12,2)` | DEFAULT 0 | |
| `shipping_amount` | `decimal(12,2)` | DEFAULT 0 | |
| `total_amount` | `decimal(12,2)` | NOT NULL | subtotal + tax + shipping |
| `delivery_instructions` | `nvarchar(1000)` | | Special instructions |
| `placed_at` | `datetimeoffset` | DEFAULT SYSUTCDATETIME() | |
| `updated_at` | `datetimeoffset` | DEFAULT SYSUTCDATETIME() | |

**Indexes:**
- `IX_main_order_order_number` (order_number)
- `IX_main_order_customer_id` (customer_id)
- `IX_main_order_status` (status)

---

### 3.7 `main_orderitem`
Individual line items within an order.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | `bigint` | PK, identity | |
| `order_id` | `bigint` | FK → `main_order(id)`, CASCADE | |
| `product_id` | `bigint` | FK → `main_product(id)` | |
| `quantity` | `decimal(10,2)` | NOT NULL | |
| `unit_price` | `decimal(10,2)` | NOT NULL | Snapshot at order time |
| `line_total` | `decimal(12,2)` | GENERATED | `quantity * unit_price` |
| `created_at` | `datetimeoffset` | DEFAULT SYSUTCDATETIME() | |

---

### 3.8 `main_deliverytrack`
Logistics tracking entries per order.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | `bigint` | PK, identity | |
| `order_id` | `bigint` | FK → `main_order(id)`, CASCADE | |
| `status` | `nvarchar(50)` | NOT NULL | picked, packed, in_transit, out_for_delivery, delivered |
| `location` | `nvarchar(255)` | | Current hub or GPS |
| `notes` | `nvarchar(1000)` | | |
| `recorded_at` | `datetimeoffset` | DEFAULT SYSUTCDATETIME() | |

**Indexes:**
- `IX_main_deliverytrack_order_id` (order_id)

---

### 3.9 `main_orderstatuslog`
Audit trail of every status change on an order.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | `bigint` | PK, identity | |
| `order_id` | `bigint` | FK → `main_order(id)`, CASCADE | |
| `old_status` | `nvarchar(20)` | | |
| `new_status` | `nvarchar(20)` | NOT NULL | |
| `changed_by` | `nvarchar(100)` | | User or system |
| `changed_at` | `datetimeoffset` | DEFAULT SYSUTCDATETIME() | |

---

## 4. Django Models (Ready to Implement)

Place these in `apps/main/models.py`:

```python
from django.db import models
from django.core.validators import MinValueValidator
import uuid


class Customer(models.Model):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True)
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=50, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "main_customer"
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "main_category"

    def __str__(self):
        return self.name


class Product(models.Model):
    sku = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    unit_of_measure = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "main_product"
        indexes = [
            models.Index(fields=["sku"]),
            models.Index(fields=["name"]),
            models.Index(fields=["category"]),
        ]

    def __str__(self):
        return f"{self.sku} — {self.name}"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image_url = models.URLField(max_length=500)
    alt_text = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "main_productimage"


class Inventory(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name="inventory")
    quantity_on_hand = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    quantity_reserved = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    reorder_level = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "main_inventory"

    @property
    def quantity_available(self):
        return self.quantity_on_hand - self.quantity_reserved

    def __str__(self):
        return f"{self.product.sku} — Available: {self.quantity_available}"


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    order_number = models.CharField(max_length=20, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="orders")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    delivery_instructions = models.TextField(blank=True)
    placed_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "main_order"
        indexes = [
            models.Index(fields=["order_number"]),
            models.Index(fields=["customer"]),
            models.Index(fields=["status"]),
        ]

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"ORD-{self.placed_at.strftime('%y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        self.total_amount = (self.subtotal or 0) + (self.tax_amount or 0) + (self.shipping_amount or 0)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "main_orderitem"

    @property
    def line_total(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f"{self.order.order_number} — {self.product.sku} x {self.quantity}"


class DeliveryTrack(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="delivery_updates")
    status = models.CharField(max_length=50)
    location = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "main_deliverytrack"
        indexes = [models.Index(fields=["order"])]


class OrderStatusLog(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="status_logs")
    old_status = models.CharField(max_length=20, blank=True)
    new_status = models.CharField(max_length=20)
    changed_by = models.CharField(max_length=100, blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "main_orderstatuslog"
```

---

## 5. Migration Strategy

### Local (PostgreSQL)
```bash
docker compose up -d db
python manage.py makemigrations main
python manage.py migrate
python manage.py createsuperuser
```

### Azure (SQL Server)
```bash
# 1. Set environment to Azure (see .env.azure)
# 2. Install ODBC driver locally (for testing connectivity)
# 3. Run migrations
python manage.py migrate
```

### Seeding Test Data
A seed script (`scripts/seed_db.py`) will be provided to populate:
- 5 categories
- 20 products with images
- 3 customers
- 2 sample orders with delivery tracking

---

*Design created: June 26, 2026*  
*Sources: Unit 2 Project Scope Statement, Django ORM best practices, Azure SQL Database documentation*
