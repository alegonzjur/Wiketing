from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from django.conf import settings
from django.http import HttpResponse
from django.urls import re_path
from categorias.views import CategoriaViewSet
from tickets.views import TicketViewSet, ComentarioViewSet, DashboardResumenView
from usuarios.views import TicketingTokenObtainPairView, UsuarioActualView

router = DefaultRouter()
router.register("categorias", CategoriaViewSet, basename="categoria")
router.register("tickets", TicketViewSet, basename="ticket")
router.register("comentarios", ComentarioViewSet, basename="comentario")

def spa(request):
    html = (settings.FRONTEND_DIST / "index.html").read_text(encoding="utf-8")
    r = HttpResponse(html)
    r["Cache-Control"] = "no-cache"
    return r

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),

    # Autenticación JWT — la usará React (Fase 4).
    path("api/token/", TicketingTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/usuarios/me/", UsuarioActualView.as_view(), name="usuario_actual"),
    path("api/dashboard/resumen/", DashboardResumenView.as_view(), name="dashboard_resumen"),

    # Login/logout de sesión — puente de desarrollo para la API navegable
    # (útil para probar/depurar desde el navegador con tu superusuario).
    # No lo usa el frontend, que va siempre por JWT.
    path("api-auth/", include("rest_framework.urls")),
    re_path(r"^(?!api/|admin/|api-auth/|static/|assets/).*$", spa),
]

