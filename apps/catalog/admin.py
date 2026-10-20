from django.contrib import admin

from .models import Product, ProductLine


@admin.register(ProductLine)
class ProductLineAdmin(admin.ModelAdmin):
    list_display = ("name", "icon", "order")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "brand", "line", "is_active", "order")
    list_filter = ("brand", "line", "is_active")
    search_fields = ("name", "summary")
    prepopulated_fields = {"slug": ("name",)}
