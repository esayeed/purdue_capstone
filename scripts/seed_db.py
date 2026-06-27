#!/usr/bin/env python3
"""
Seed Script for Local & Azure Testing
-------------------------------------
Populates the database with sample categories, products, customers,
and orders so the team can immediately see the e-commerce flow.

Usage:
    docker compose exec web python scripts/seed_db.py
    # OR locally:
    python scripts/seed_db.py
"""
import os
import sys
import random
from decimal import Decimal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

from django.db import transaction
from apps.main.models import Category, Product, ProductImage, Inventory, Customer, Order, OrderItem, DeliveryTrack


def seed():
    print("Seeding database with test data...")

    with transaction.atomic():
        # Categories
        categories_data = [
            ("Produce", "Fresh fruits and vegetables"),
            ("Dairy", "Milk, cheese, yogurt, and eggs"),
            ("Meat & Seafood", "Beef, poultry, pork, and fresh fish"),
            ("Beverages", "Juices, sodas, water, and coffee"),
            ("Dry Goods", "Rice, pasta, flour, and canned items"),
        ]
        categories = []
        for name, desc in categories_data:
            cat, _ = Category.objects.get_or_create(name=name, defaults={"description": desc})
            categories.append(cat)
        print(f"  ✓ {len(categories)} categories created")

        # Products
        products_data = [
            ("PRD-001", "Organic Bananas", "Fresh organic bananas, 1 lb bunch", categories[0], Decimal("1.29"), "lb"),
            ("PRD-002", "Red Apples", "Crisp red apples, per lb", categories[0], Decimal("2.49"), "lb"),
            ("PRD-003", "Whole Milk", "1 gallon whole milk", categories[1], Decimal("3.99"), "gallon"),
            ("PRD-004", "Cheddar Cheese", "Sharp cheddar, 1 lb block", categories[1], Decimal("5.49"), "lb"),
            ("PRD-005", "Chicken Breast", "Boneless skinless chicken breast, per lb", categories[2], Decimal("4.99"), "lb"),
            ("PRD-006", "Atlantic Salmon", "Fresh Atlantic salmon fillet, per lb", categories[2], Decimal("12.99"), "lb"),
            ("PRD-007", "Orange Juice", "100% pure orange juice, 64 oz", categories[3], Decimal("4.29"), "bottle"),
            ("PRD-008", "Sparkling Water", "Naturally flavored sparkling water, 12-pack", categories[3], Decimal("7.99"), "case"),
            ("PRD-009", "Basmati Rice", "Premium basmati rice, 5 lb bag", categories[4], Decimal("8.99"), "bag"),
            ("PRD-010", "Olive Oil", "Extra virgin olive oil, 16.9 oz", categories[4], Decimal("9.49"), "bottle"),
        ]
        products = []
        for sku, name, desc, cat, price, uom in products_data:
            prod, _ = Product.objects.get_or_create(
                sku=sku,
                defaults={
                    "name": name,
                    "description": desc,
                    "category": cat,
                    "unit_price": price,
                    "unit_of_measure": uom,
                },
            )
            products.append(prod)
        print(f"  ✓ {len(products)} products created")

        # Inventory
        for prod in products:
            Inventory.objects.get_or_create(
                product=prod,
                defaults={
                    "quantity_on_hand": Decimal(random.randint(50, 500)),
                    "quantity_reserved": Decimal("0.00"),
                    "reorder_level": Decimal(random.randint(10, 30)),
                },
            )
        print(f"  ✓ Inventory records created")

        # Customers
        customers_data = [
            ("alice@example.com", "Alice", "Johnson", "555-0101"),
            ("bob@example.com", "Bob", "Smith", "555-0102"),
            ("carol@example.com", "Carol", "White", "555-0103"),
        ]
        customers = []
        for email, first, last, phone in customers_data:
            cust, _ = Customer.objects.get_or_create(
                email=email,
                defaults={
                    "first_name": first,
                    "last_name": last,
                    "phone": phone,
                    "address_line1": f"{random.randint(100, 9999)} Main St",
                    "city": "Indianapolis",
                    "state": "IN",
                    "zip_code": f"462{random.randint(10, 99)}",
                },
            )
            customers.append(cust)
        print(f"  ✓ {len(customers)} customers created")

        # Orders
        order1, _ = Order.objects.get_or_create(
            order_number="ORD-250626-001",
            defaults={
                "customer": customers[0],
                "status": "confirmed",
                "subtotal": Decimal("12.77"),
                "tax_amount": Decimal("0.89"),
                "shipping_amount": Decimal("5.00"),
                "total_amount": Decimal("18.66"),
                "delivery_instructions": "Leave at front desk",
            },
        )
        OrderItem.objects.get_or_create(
            order=order1,
            product=products[0],
            defaults={"quantity": Decimal("2.00"), "unit_price": products[0].unit_price},
        )
        OrderItem.objects.get_or_create(
            order=order1,
            product=products[2],
            defaults={"quantity": Decimal("1.00"), "unit_price": products[2].unit_price},
        )
        DeliveryTrack.objects.get_or_create(
            order=order1,
            status="confirmed",
            defaults={"location": "Warehouse A", "notes": "Order received and confirmed"},
        )

        order2, _ = Order.objects.get_or_create(
            order_number="ORD-250626-002",
            defaults={
                "customer": customers[1],
                "status": "shipped",
                "subtotal": Decimal("17.98"),
                "tax_amount": Decimal("1.26"),
                "shipping_amount": Decimal("5.00"),
                "total_amount": Decimal("24.24"),
                "delivery_instructions": "Ring doorbell",
            },
        )
        OrderItem.objects.get_or_create(
            order=order2,
            product=products[4],
            defaults={"quantity": Decimal("3.00"), "unit_price": products[4].unit_price},
        )
        DeliveryTrack.objects.get_or_create(
            order=order2,
            status="shipped",
            defaults={"location": "Distribution Center", "notes": "Left warehouse"},
        )
        DeliveryTrack.objects.get_or_create(
            order=order2,
            status="in_transit",
            defaults={"location": "En route to Indianapolis", "notes": "Expected delivery tomorrow"},
        )

        print(f"  ✓ 2 sample orders with delivery tracking created")

    print("\nDatabase seeding complete!")
    print("You can now browse products, view orders, and test the admin panel.")


if __name__ == "__main__":
    seed()
