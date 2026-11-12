from django.contrib import admin

from .models import Blend, BlendIngredient, Ingredient


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ["name", "type", "price", "caffeine_mg", "portion_grams", "stock", "min_stock"]
    list_filter = ["type", "for_protein", "for_clear", "for_energy", "for_hydration"]
    list_editable = ["stock", "min_stock"]
    search_fields = ["name"]


class BlendIngredientInline(admin.TabularInline):
    model = BlendIngredient
    extra = 0
    max_num = 3


@admin.register(Blend)
class BlendAdmin(admin.ModelAdmin):
    list_display = ["name", "base", "flavor", "is_ready_made", "user"]
    search_fields = ["name"]
    list_filter = ["is_ready_made"]
    inlines = [BlendIngredientInline]
