from io import StringIO

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .forms import ConfiguratorForm
from .models import Blend, Ingredient, Line, Size


class ConfiguratorTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("load_demo_data", stdout=StringIO())
        cls.whey = Ingredient.objects.get(name="Whey")
        cls.schoko = Ingredient.objects.get(name="Schoko")
        cls.boosters = list(
            Ingredient.objects.for_line(Line.PROTEIN).filter(type=Ingredient.Type.BOOSTER)
        )

    def data(self, boosters=()):
        return {
            "line": "protein",
            "name": "Mein Mix",
            "base": self.whey.pk,
            "flavor": self.schoko.pk,
            "sweetness": "normal",
            "size": "regular",
            "boosters": [b.pk for b in boosters],
        }

    def test_max_three_boosters(self):
        self.assertTrue(ConfiguratorForm(self.data(self.boosters[:3])).is_valid())
        self.assertFalse(ConfiguratorForm(self.data(self.boosters[:4])).is_valid())

    def test_summary_shows_price_and_caffeine_hint(self):
        caffeine = Ingredient.objects.get(name="Koffein")
        response = self.client.post(reverse("shop:configurator_summary"), self.data([caffeine]))
        # (Whey 1,20 + Schoko 0,20 + Koffein 0,25) × 30 Portionen
        self.assertContains(response, "49,50</span> €")
        self.assertContains(response, "Enthält 80 mg Koffein")

    def test_submit_saves_blend_and_adds_to_cart(self):
        response = self.client.post(reverse("shop:configurator"), self.data(self.boosters[:2]))
        self.assertRedirects(response, reverse("orders:cart"))
        blend = Blend.objects.get(name="Mein Mix")
        self.assertFalse(blend.is_ready_made)
        self.assertEqual(blend.boosters.count(), 2)
        self.assertContains(self.client.get(reverse("orders:cart")), "Mein Mix")

    def test_prefill_from_ready_made(self):
        mix = Blend.objects.get(name="Energy Pump", flavor__name="Mango-Maracuja")
        response = self.client.get(reverse("shop:configurator"), {"mix": mix.pk})
        self.assertContains(response, "Energy Pump (angepasst)")

    def test_detail_page_for_ready_made_and_own_blends_only(self):
        mix = Blend.objects.get(name="Energy Pump", flavor__name="Mango-Maracuja")
        response = self.client.get(reverse("shop:blend_detail", args=[mix.pk]))
        self.assertContains(response, "Beta-Alanin")
        self.assertContains(response, "€/kg")
        foreign = Blend.objects.create(name="Fremd", base=self.whey, flavor=self.schoko)
        self.assertEqual(self.client.get(reverse("shop:blend_detail", args=[foreign.pk])).status_code, 404)

    def test_choices_depend_on_line(self):
        energy = ConfiguratorForm(initial={"line": "energy"})
        boosters = [b.name for b in energy.fields["boosters"].queryset]
        self.assertIn("Beta-Alanin", boosters)
        # Energy-Basis enthält schon Koffein, deshalb kein Koffein-Booster
        self.assertNotIn("Koffein", boosters)
        clear_flavors = [f.name for f in ConfiguratorForm(initial={"line": "clear"}).fields["flavor"].queryset]
        self.assertIn("Zitrone", clear_flavors)
        self.assertNotIn("Schoko", clear_flavors)

    def test_creamy_flavor_is_rejected_for_clear_protein(self):
        clear = Ingredient.objects.get(name="Clear Whey Isolat")
        form = ConfiguratorForm({**self.data(), "line": "clear", "base": clear.pk})
        self.assertFalse(form.is_valid())
        self.assertIn("flavor", form.errors)

    def test_base_price_uses_portion_size_of_base(self):
        hydro = Blend.objects.get(name="Hydro Sport", flavor__name="Wassermelone")
        # 30 Portionen à 7 g = 210 g
        self.assertEqual(hydro.summary["can_grams"], 210)
        self.assertEqual(hydro.line, Line.HYDRATION)
        response = self.client.get(reverse("shop:configurator"), {"mix": hydro.pk})
        self.assertContains(response, "Preis pro Dose (210 g, 30 Portionen)")

    def test_ready_made_protein_has_no_boosters_and_all_flavors(self):
        whey = Blend.objects.filter(name="Whey Protein", is_ready_made=True)
        self.assertEqual(whey.count(), 10)
        self.assertFalse(whey.filter(boosters__isnull=False).exists())
        response = self.client.get(reverse("shop:home"))
        self.assertContains(response, "10 Sorten")

    def test_detail_offers_flavors_and_large_size(self):
        mix = Blend.objects.get(name="Whey Protein", flavor__name="Schoko")
        response = self.client.get(reverse("shop:blend_detail", args=[mix.pk]), {"groesse": "large"})
        self.assertContains(response, "Pistazie")
        self.assertContains(response, "1,8 kg")
        # 2 × 42,00 € − 10 %
        self.assertContains(response, "75,60 €")

    def test_large_size_only_for_protein_lines(self):
        mix = Blend.objects.get(name="Energy Pump", flavor__name="Mango-Maracuja")
        self.assertEqual(mix.sizes(), [Size.REGULAR])
        self.client.post(reverse("orders:cart_add", args=[mix.pk]), {"size": "large"})
        self.assertEqual(self.client.session["cart"], {f"{mix.pk}:regular": 1})

    def test_configurator_large_size_goes_to_cart(self):
        self.client.post(reverse("shop:configurator"), {**self.data(), "size": "large"})
        blend = Blend.objects.get(name="Mein Mix")
        self.assertEqual(self.client.session["cart"], {f"{blend.pk}:large": 1})

    def test_energy_and_hydration_products_in_tiers_with_all_flavors(self):
        for name in ["Energy Classic", "Energy Vital", "Energy Pump", "Hydro Basic", "Hydro Sport", "Hydro Immun"]:
            self.assertEqual(Blend.objects.filter(name=name, is_ready_made=True).count(), 9, name)
        price = lambda name: Blend.objects.filter(name=name, flavor__name="Zitrone").get().price()
        self.assertLess(price("Energy Classic"), price("Energy Vital"))
        self.assertLess(price("Energy Vital"), price("Energy Pump"))
        self.assertLess(price("Hydro Basic"), price("Hydro Sport"))

    def test_sold_out_ingredient_is_disabled_and_rejected(self):
        kokos = Ingredient.objects.get(name="Kokos")
        response = self.client.get(reverse("shop:configurator"))
        self.assertRegex(response.content.decode(), rf'name="flavor" value="{kokos.pk}"[^>]* disabled')
        form = ConfiguratorForm({**self.data(), "flavor": kokos.pk})
        self.assertFalse(form.is_valid())
        self.assertIn("ausverkauft", str(form.errors))

    def test_sold_out_product_cannot_be_added(self):
        mix = Blend.objects.get(name="Casein Protein", flavor__name="Kokos")
        response = self.client.post(reverse("orders:cart_add", args=[mix.pk]))
        self.assertRedirects(response, reverse("shop:blend_detail", args=[mix.pk]))
        self.assertNotIn("cart", self.client.session)
