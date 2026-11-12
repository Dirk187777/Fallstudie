from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from orders.models import Order

from .forms import RegisterForm


def register(request):
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        # Frühere Gastbestellungen mit derselben E-Mail dem neuen Konto zuordnen
        Order.objects.filter(user__isnull=True, email__iexact=user.email).update(user=user)
        login(request, user)
        return redirect("accounts:account")
    return render(request, "accounts/register.html", {"form": form})


@login_required
def account(request):
    blends = (
        request.user.blends.filter(is_ready_made=False)
        .select_related("base", "flavor")
        .prefetch_related("boosters")
    )
    orders = request.user.orders.prefetch_related("items__blend")
    return render(request, "accounts/account.html", {"blends": blends, "orders": orders})
