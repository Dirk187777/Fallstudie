from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from orders import cart

from .forms import ConfiguratorForm
from .models import Blend, Line, Size, summarize


def home(request):
    ready_made = (
        Blend.objects.filter(is_ready_made=True)
        .select_related("base", "flavor")
        .prefetch_related("boosters")
        .order_by("pk")
    )
    # Fertige Mixe mit gleichem Namen sind Sorten eines Produkts, z. B. "Whey Protein"
    variants = {}
    for blend in ready_made:
        variants.setdefault(blend.name, []).append(blend)
    products = [
        {
            "blend": group[0],
            "variant_count": len(group),
            "sold_out": all(b.is_sold_out for b in group),
            "flavor_colors": [b.flavor.color for b in group[:5]],
            "cheapest": min((b.summary for b in group), key=lambda s: s["price"]),
        }
        for group in variants.values()
    ]
    sections = [
        {"line": value, "label": label, "products": [p for p in products if p["blend"].line == value]}
        for value, label in Line.choices
    ]
    hero = [section["products"][0]["blend"] for section in sections if section["products"]][:3]
    return render(request, "shop/home.html", {"sections": sections, "hero": hero})


def blend_detail(request, blend_id):
    blend = get_object_or_404(
        Blend.objects.visible_to(request.user).select_related("base", "flavor"), pk=blend_id
    )
    size = request.GET.get("groesse", Size.REGULAR)
    if size not in blend.sizes():
        size = Size.REGULAR
    variants = []
    if blend.is_ready_made:
        variants = (
            Blend.objects.filter(is_ready_made=True, name=blend.name)
            .select_related("base", "flavor")
            .prefetch_related("boosters")
            .order_by("pk")
        )
    sizes = [(s, blend.summary_for(s)) for s in blend.sizes()]
    context = {
        "blend": blend,
        "size": size,
        "sizes": sizes,
        "summary": blend.summary_for(size),
        "variants": variants,
    }
    return render(request, "shop/blend_detail.html", context)


def configurator(request):
    if request.method == "POST":
        form = ConfiguratorForm(request.POST)
        if form.is_valid():
            blend = form.save(user=request.user)
            cart.add(request.session, blend.pk, form.cleaned_data["size"])
            return redirect("orders:cart")
    else:
        initial = {"line": request.GET.get("linie")}
        mix_id = request.GET.get("mix", "")
        if mix_id.isdigit():
            template = get_object_or_404(Blend, pk=mix_id, is_ready_made=True)
            initial = ConfiguratorForm.initial_from(template)
        form = ConfiguratorForm(initial=initial)
    return render(request, "shop/configurator.html", _context(form))


@require_POST
def configurator_summary(request):
    """HTMX: berechnet Preis und Nährwerte bei jeder Änderung neu."""
    form = ConfiguratorForm(request.POST)
    form.is_valid()
    return render(request, "shop/_summary.html", {**_context(form), "oob": True})


def _context(form):
    ingredients = form.selected_ingredients()
    return {
        "form": form,
        "ingredients": ingredients,
        "blend_name": form["name"].value(),
        "summary": summarize(ingredients, form.selected_size()),
    }
