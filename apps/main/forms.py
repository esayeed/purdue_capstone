from django import forms
from .models import Product, Inventory, Category


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["sku", "name", "description", "category", "unit_price", "unit_of_measure", "is_active"]
        widgets = {
            "sku": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g., PROD-001"}),
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Product name"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Short description"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "unit_price": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "unit_of_measure": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g., lb, case, each"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class InventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ["quantity_on_hand", "reorder_level"]
        widgets = {
            "quantity_on_hand": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "reorder_level": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
        }
