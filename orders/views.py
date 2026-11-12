from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from shop.models import Blend, Size

from . import cart
from .forms import CheckoutForm
from .stock import OutOfStock
from .models import Order

LAST_ORDER_KEY = "last_order_id"


def cart_detail(request):
    items = cart.items(request.session)
    return render(request, "orders/cart.html", {"items": items, "total": cart.total(items)})


@require_POST
def cart_add(request, blend_id):
    blend = get_object_or_404(Blend.objects.visible_to(request.user), pk=blend_id)
    size = request.POST.get("size", Size.REGULAR)
    if size not in blend.sizes():
        size = Size.REGULAR
    if blend.is_sold_out:
        messages.error(request, f"{blend.name} ({blend.flavor}) ist leider ausverkauft.")
        return redirect("shop:blend_detail", blend_id=blend.pk)
    cart.add(request.session, blend.pk, size)
    return redirect("orders:cart")


@require_POST
def cart_update(request, blend_id, size):
    try:
        quantity = int(request.POST.get("quantity", ""))
    except ValueError:
        return redirect("orders:cart")
    cart.set_quantity(request.session, blend_id, size, quantity)
    return redirect("orders:cart")


@require_POST
def cart_remove(request, blend_id, size):
    cart.remove(request.session, blend_id, size)
    return redirect("orders:cart")


def checkout(request):
    items = cart.items(request.session)
    if not items:
        return redirect("orders:cart")
    form = CheckoutForm(request.POST or None, initial=CheckoutForm.initial_for(request.user))
    if form.is_valid():
        try:
            order = form.save(items, user=request.user)
        except OutOfStock as error:
            form.add_error(None, f"Leider nicht mehr genug auf Lager: {error}. Bitte passe deinen Warenkorb an.")
        else:
            cart.clear(request.session)
            request.session[LAST_ORDER_KEY] = order.pk
            return redirect("orders:confirmation", order_id=order.pk)
    context = {"form": form, "items": items, "total": cart.total(items)}
    return render(request, "orders/checkout.html", context)


def confirmation(request, order_id):
    # Nur die eigene, gerade abgeschickte Bestellung anzeigen
    if request.session.get(LAST_ORDER_KEY) != order_id:
        return redirect("shop:home")
    order = get_object_or_404(Order.objects.prefetch_related("items__blend"), pk=order_id)
    return render(request, "orders/confirmation.html", {"order": order})
