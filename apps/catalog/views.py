from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, render

from .models import Product, ProductLine


@login_required
def product_list(request):
    products = Product.objects.filter(is_active=True).select_related("line")
    q = request.GET.get("q", "").strip()
    brand = request.GET.get("marca", "")
    line = request.GET.get("linea", "")
    if q:
        products = products.filter(Q(name__icontains=q) | Q(summary__icontains=q) | Q(features__icontains=q))
    if brand:
        products = products.filter(brand=brand)
    if line:
        products = products.filter(line__slug=line)
    context = {
        "products": products,
        "lines": ProductLine.objects.annotate(n=Count("products", filter=Q(products__is_active=True))).filter(n__gt=0),
        "filters": {"q": q, "marca": brand, "linea": line},
        "brand_counts": {
            "": Product.objects.filter(is_active=True).count(),
            "latina": Product.objects.filter(is_active=True, brand="latina").count(),
            "induless": Product.objects.filter(is_active=True, brand="induless").count(),
        },
    }
    return render(request, "catalog/list.html", context)


@login_required
def product_detail(request, slug):
    product = get_object_or_404(Product.objects.select_related("line"), slug=slug, is_active=True)
    context = {
        "product": product,
        "courses": product.courses.filter(is_published=True).select_related("category"),
        "similar": Product.objects.filter(is_active=True, line=product.line).exclude(pk=product.pk)[:4],
    }
    return render(request, "catalog/detail.html", context)
