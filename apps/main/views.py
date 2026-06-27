from django.http import HttpRequest, HttpResponse, JsonResponse
from django.db import connection
from django.shortcuts import render, redirect
from django.contrib import messages

from .models import Product, Category, Customer
from .forms import ProductForm, InventoryForm


def home(request: HttpRequest) -> HttpResponse:
    context = {
        "product_count": Product.objects.count(),
        "category_count": Category.objects.count(),
        "customer_count": Customer.objects.count(),
    }
    return render(request, "main/home.html", context)


def health_check(request: HttpRequest) -> HttpResponse:
    return HttpResponse("ok")


def db_health_check(request: HttpRequest) -> JsonResponse:
    """
    Extended health check that verifies database connectivity.
    Used during Saturday's Azure SQL connectivity test.
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            row = cursor.fetchone()
            if row and row[0] == 1:
                return JsonResponse(
                    {"status": "ok", "db": "connected", "engine": connection.vendor},
                    status=200,
                )
    except Exception as e:
        return JsonResponse(
            {"status": "error", "db": "disconnected", "detail": str(e)},
            status=503,
        )
    return JsonResponse(
        {"status": "error", "db": "unknown"},
        status=503,
    )


def add_product(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        product_form = ProductForm(request.POST)
        inventory_form = InventoryForm(request.POST)
        if product_form.is_valid() and inventory_form.is_valid():
            product = product_form.save()
            inventory = inventory_form.save(commit=False)
            inventory.product = product
            inventory.save()
            messages.success(request, f"Product '{product.name}' created successfully!")
            return redirect("home")
    else:
        product_form = ProductForm()
        inventory_form = InventoryForm()

    return render(
        request,
        "main/add_product.html",
        {"product_form": product_form, "inventory_form": inventory_form},
    )
