from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("shop.urls")),
    path("", include("orders.urls")),
    path("konto/", include("accounts.urls")),
    path("betrieb/", include("backoffice.urls")),
]
