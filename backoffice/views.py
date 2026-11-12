from django.contrib.auth.decorators import user_passes_test
from django.db.models import Count
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from orders.models import Order
from shop.models import Ingredient

staff_required = user_passes_test(lambda user: user.is_staff, login_url="accounts:login")


@staff_required
def order_list(request):
    # Meta.ordering greift bei Abfragen mit Count nicht, deshalb explizit sortieren
    orders = Order.objects.annotate(item_count=Count("items")).order_by("-created_at")
    status = request.GET.get("status")
    if status in Order.Status.values:
        orders = orders.filter(status=status)
    counts = dict(Order.objects.values_list("status").annotate(Count("id")))
    tabs = [(value, label, counts.get(value, 0)) for value, label in Order.Status.choices]
    context = {
        "orders": orders,
        "tabs": tabs,
        "active_status": status,
        "total_count": sum(counts.values()),
        "low_stock": Ingredient.objects.low_stock(),
    }
    return render(request, "backoffice/order_list.html", context)


@staff_required
def stock_list(request):
    ingredients = Ingredient.objects.all()
    sections = [
        (label, [i for i in ingredients if i.type == value]) for value, label in Ingredient.Type.choices
    ]
    return render(request, "backoffice/stock_list.html", {"sections": sections})


@staff_required
def order_detail(request, order_id):
    order = get_object_or_404(
        Order.objects.prefetch_related("items__blend__base", "items__blend__flavor", "items__blend__boosters"),
        pk=order_id,
    )
    return render(request, "backoffice/order_detail.html", {"order": order})


@staff_required
@require_POST
def order_set_status(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    status = request.POST.get("status")
    if status not in Order.Status.values:
        return HttpResponseBadRequest("Unbekannter Status")
    order.status = status
    order.save(update_fields=["status"])
    if request.headers.get("HX-Request"):
        return render(request, "backoffice/_status.html", {"order": order})
    return redirect("backoffice:order_detail", order_id=order.pk)
