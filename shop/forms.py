from django import forms

from .models import MAX_BOOSTERS, Blend, Ingredient, Line, Size, sizes_for

# Native Inputs nur für Screenreader und Tastatur, die Karte drumherum zeigt die Auswahl
HIDDEN_INPUT = {"class": "peer sr-only"}


class IngredientWidgetMixin:
    """Ausverkaufte Zutaten bleiben sichtbar, sind aber nicht wählbar."""

    def create_option(self, name, value, *args, **kwargs):
        option = super().create_option(name, value, *args, **kwargs)
        instance = getattr(value, "instance", None)
        if instance is not None and instance.is_sold_out:
            option["attrs"]["disabled"] = True
        return option


class IngredientRadioSelect(IngredientWidgetMixin, forms.RadioSelect):
    pass


class IngredientCheckboxSelect(IngredientWidgetMixin, forms.CheckboxSelectMultiple):
    pass


SIZE_LABELS = {
    Size.REGULAR: "Normal · 30 Portionen",
    Size.LARGE: "Groß · 60 Portionen · 10 % gespart",
}

LINE_DESCRIPTIONS = {
    Line.PROTEIN: "Cremig wie ein Milchshake",
    Line.CLEAR: "Protein, erfrischend wie Saft",
    Line.ENERGY: "Ohne Protein, 150 mg Koffein",
    Line.HYDRATION: "Ohne Protein, Elektrolyte",
}


class ConfiguratorForm(forms.Form):
    line = forms.ChoiceField(choices=Line.choices, widget=forms.HiddenInput)
    name = forms.CharField(label="Name deiner Mischung", max_length=100)
    base = forms.ModelChoiceField(
        label="Basis",
        queryset=Ingredient.objects.none(),
        widget=IngredientRadioSelect(attrs=HIDDEN_INPUT),
        empty_label=None,
    )
    flavor = forms.ModelChoiceField(
        label="Geschmack",
        queryset=Ingredient.objects.none(),
        widget=IngredientRadioSelect(attrs=HIDDEN_INPUT),
        empty_label=None,
    )
    sweetness = forms.ChoiceField(
        label="Süße",
        choices=Blend.Sweetness.choices,
        initial=Blend.Sweetness.NORMAL,
        widget=forms.RadioSelect(attrs=HIDDEN_INPUT),
    )
    size = forms.ChoiceField(
        label="Größe",
        choices=Size.choices,
        initial=Size.REGULAR,
        widget=forms.RadioSelect(attrs=HIDDEN_INPUT),
    )
    boosters = forms.ModelMultipleChoiceField(
        label=f"Booster (max. {MAX_BOOSTERS})",
        queryset=Ingredient.objects.none(),
        widget=IngredientCheckboxSelect(attrs=HIDDEN_INPUT),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Die Linie bestimmt, welche Zutaten zur Wahl stehen
        line = self.data.get("line") if self.is_bound else self.initial.get("line")
        self.selected_line = line if line in Line.values else Line.PROTEIN
        self.initial["line"] = self.selected_line
        ingredients = Ingredient.objects.for_line(self.selected_line)
        self.fields["base"].queryset = ingredients.filter(type=Ingredient.Type.BASE)
        self.fields["flavor"].queryset = ingredients.filter(type=Ingredient.Type.FLAVOR)
        self.fields["boosters"].queryset = ingredients.filter(type=Ingredient.Type.BOOSTER)
        self.fields["size"].choices = [(s, SIZE_LABELS[s]) for s in sizes_for(self.selected_line)]
        # Start mit Basis und Geschmack vorausgewählt, damit Dose und Preis nicht leer sind
        if not self.is_bound:
            self.initial.setdefault("base", self.fields["base"].queryset.available().first())
            self.initial.setdefault("flavor", self.fields["flavor"].queryset.available().first())

    def selected_size(self):
        data = getattr(self, "cleaned_data", {}) if self.is_bound else self.initial
        return data.get("size") or Size.REGULAR

    def has_size_choice(self):
        return len(self.fields["size"].choices) > 1

    def line_choices(self):
        return [(value, label, LINE_DESCRIPTIONS[value]) for value, label in Line.choices]

    def clean(self):
        cleaned_data = super().clean()
        # Als Formularfehler statt Feldfehler, damit die Booster für die Vorschau erhalten bleiben
        if len(cleaned_data.get("boosters", [])) > MAX_BOOSTERS:
            raise forms.ValidationError(f"Bitte höchstens {MAX_BOOSTERS} Booster wählen.")
        sold_out = [i.name for i in self.selected_ingredients() if i.is_sold_out]
        if sold_out:
            raise forms.ValidationError(f"Leider ausverkauft: {', '.join(sold_out)}.")
        return cleaned_data

    def selected_ingredients(self):
        """Gewählte Zutaten, auch wenn das Formular noch unvollständig ist."""
        data = getattr(self, "cleaned_data", {}) if self.is_bound else self.initial
        selected = [data.get("base"), data.get("flavor"), *data.get("boosters", [])]
        return [i for i in selected if i]

    def save(self, user=None):
        data = self.cleaned_data
        blend = Blend.objects.create(
            name=data["name"],
            base=data["base"],
            flavor=data["flavor"],
            sweetness=data["sweetness"],
            user=user if user and user.is_authenticated else None,
        )
        blend.boosters.set(data["boosters"])
        return blend

    @staticmethod
    def initial_from(blend):
        """Startwerte, um einen fertigen Mix im Konfigurator anzupassen."""
        return {
            "line": blend.line,
            "name": f"{blend.name} (angepasst)",
            "base": blend.base,
            "flavor": blend.flavor,
            "sweetness": blend.sweetness,
            "boosters": list(blend.boosters.all()),
        }
