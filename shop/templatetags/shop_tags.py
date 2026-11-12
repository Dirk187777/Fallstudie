from django import template
from django.utils.formats import number_format

from shop.models import Ingredient, Line, Size, summarize

register = template.Library()

# Sichtfenster der Dose im SVG (siehe shop/_can.html)
WINDOW_TOP, WINDOW_HEIGHT = 156, 44
CAN_SUBTITLE = {
    Line.PROTEIN: "CUSTOM PROTEIN BLEND",
    Line.CLEAR: "CLEAR PROTEIN",
    Line.ENERGY: "ENERGY DRINK",
    Line.HYDRATION: "HYDRATION DRINK",
}
# Die Basis ist der Hauptanteil und bekommt eine dickere Schicht
LAYER_WEIGHT = {Ingredient.Type.BASE: 3, Ingredient.Type.FLAVOR: 1, Ingredient.Type.BOOSTER: 1}


@register.filter
def weight(grams):
    """900 -> "900 g", 1800 -> "1,8 kg"."""
    if grams >= 1000:
        return f"{number_format(grams / 1000, 1 if grams % 1000 else 0)} kg"
    return f"{grams} g"


@register.inclusion_tag("shop/_can.html")
def can(ingredients, name="", css_class="", size=Size.REGULAR):
    """Produktbild einer Dose: Etikett in Geschmacksfarbe, Zutaten als Schichten im Sichtfenster."""
    ingredients = list(ingredients)
    by_type = {i.type: i for i in ingredients}
    flavor = by_type.get(Ingredient.Type.FLAVOR)
    base = by_type.get(Ingredient.Type.BASE)

    layers = []
    total = sum(LAYER_WEIGHT[i.type] for i in ingredients)
    y = WINDOW_TOP + WINDOW_HEIGHT
    for ingredient in ingredients:  # von unten nach oben: Basis, Geschmack, Booster
        height = WINDOW_HEIGHT * LAYER_WEIGHT[ingredient.type] / total
        y -= height
        layers.append({
            "key": ingredient.pk,
            "y": round(y, 2),
            "height": round(height, 2),
            "color": ingredient.color,
        })

    summary = summarize(ingredients, size)
    return {
        "name": name or "Dein Mix",
        "base": base.name if base else "",
        "subtitle": CAN_SUBTITLE[base.line if base else Line.PROTEIN],
        "portions": summary["portions"],
        "can_grams": summary["can_grams"],
        "label_color": flavor.color if flavor else "#e7e5e4",
        "layers": layers,
        "css_class": css_class,
    }
