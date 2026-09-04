from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from categorias.views import CategoriaViewSet
from tickets.views import TicketViewSet, ComentarioViewSet

router = DefaultRouter()
router.register("categorias", CategoriaViewSet, basename="categoria")
router.register("tickets", TicketViewSet, basename="ticket")
router.register("comentarios", ComentarioViewSet, basename="comentario")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    # Login/logout de sesión para la API navegable — puente hasta el
    # login JWT propio del frontend (Fase 3).
    path("api-auth/", include("rest_framework.urls")),
]