from django.contrib import admin

# Register your models here.
# thrift_store/admin.py
from django.contrib import admin
from .models import Product

admin.site.register(Product)  # Register the Product model
