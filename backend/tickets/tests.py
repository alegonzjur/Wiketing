from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from categorias.models import Categoria
from .models import Ticket

Usuario = get_user_model()
EN_ESPERA = Ticket.Estado.EN_ESPERA


class EstadoEnEsperaTests(TestCase):
    """El estado "en_espera" detiene el reloj: su tiempo no cuenta para la
    resolución (ver tickets/signals.py)."""

    @classmethod
    def setUpTestData(cls):
        cls.usuario = Usuario.objects.create_user(username="tester", password="x")
        cls.categoria = Categoria.objects.create(nombre="General")

    def crear(self, **kwargs):
        datos = dict(titulo="T", categoria=self.categoria, creado_por=self.usuario)
        datos.update(kwargs)
        return Ticket.objects.create(**datos)

    def cambiar_estado(self, ticket, estado, instante):
        """Guarda un cambio de estado como si ocurriera en `instante`."""
        ticket.refresh_from_db()
        ticket.estado = estado
        with patch("django.utils.timezone.now", return_value=instante):
            ticket.save()
        ticket.refresh_from_db()

    def test_entrar_en_espera_abre_el_periodo(self):
        t = self.crear()
        ahora = timezone.now()
        self.cambiar_estado(t, EN_ESPERA, ahora)
        self.assertEqual(t.espera_desde, ahora)
        self.assertEqual(t.tiempo_en_espera, timedelta(0))

    def test_salir_de_espera_acumula_y_cierra(self):
        t = self.crear()
        inicio = timezone.now()
        self.cambiar_estado(t, EN_ESPERA, inicio)
        self.cambiar_estado(t, Ticket.Estado.EN_PROGRESO, inicio + timedelta(hours=5))
        self.assertIsNone(t.espera_desde)
        self.assertEqual(t.tiempo_en_espera, timedelta(hours=5))

    def test_varios_periodos_se_suman(self):
        t = self.crear()
        base = timezone.now()
        self.cambiar_estado(t, EN_ESPERA, base)
        self.cambiar_estado(t, Ticket.Estado.EN_PROGRESO, base + timedelta(hours=2))
        self.cambiar_estado(t, EN_ESPERA, base + timedelta(hours=10))
        self.cambiar_estado(t, Ticket.Estado.ABIERTO, base + timedelta(hours=13))
        self.assertEqual(t.tiempo_en_espera, timedelta(hours=5))

    def test_pasar_de_espera_a_resuelto_cierra_el_periodo(self):
        t = self.crear()
        base = timezone.now()
        self.cambiar_estado(t, EN_ESPERA, base)
        self.cambiar_estado(t, Ticket.Estado.RESUELTO, base + timedelta(hours=4))
        self.assertIsNone(t.espera_desde)
        self.assertEqual(t.tiempo_en_espera, timedelta(hours=4))

    def test_guardar_sin_cambiar_estado_no_altera_la_espera(self):
        t = self.crear()
        base = timezone.now()
        self.cambiar_estado(t, EN_ESPERA, base)
        t.titulo = "otro título"
        with patch("django.utils.timezone.now", return_value=base + timedelta(hours=3)):
            t.save()
        t.refresh_from_db()
        self.assertEqual(t.espera_desde, base)
        self.assertEqual(t.tiempo_en_espera, timedelta(0))

    def test_crear_ya_en_espera(self):
        t = self.crear(estado=EN_ESPERA)
        self.assertIsNotNone(t.espera_desde)

    def test_total_incluye_el_periodo_en_curso(self):
        t = self.crear()
        base = timezone.now()
        self.cambiar_estado(t, EN_ESPERA, base)
        with patch("django.utils.timezone.now", return_value=base + timedelta(hours=7)):
            self.assertEqual(t.tiempo_en_espera_total, timedelta(hours=7))

    def test_cambio_a_espera_queda_en_el_historial(self):
        t = self.crear()
        self.cambiar_estado(t, EN_ESPERA, timezone.now())
        h = t.historial.get()
        self.assertEqual((h.campo_modificado, h.valor_nuevo), ("estado", "en_espera"))

    def test_dashboard_no_cuenta_la_espera_y_muestra_el_estado(self):
        ahora = timezone.now()
        t = self.crear()
        # 10 h desde la creación hasta resolver, de las que 4 h en espera.
        Ticket.objects.filter(pk=t.pk).update(fecha_creacion=ahora - timedelta(hours=10))
        self.cambiar_estado(t, EN_ESPERA, ahora - timedelta(hours=8))
        self.cambiar_estado(t, Ticket.Estado.EN_PROGRESO, ahora - timedelta(hours=4))
        t.refresh_from_db()
        t.estado = Ticket.Estado.RESUELTO
        t.fecha_resolucion = ahora
        t.save()
        self.crear(estado=EN_ESPERA)

        cliente = APIClient()
        cliente.force_authenticate(self.usuario)
        r = cliente.get("/api/dashboard/resumen/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["por_estado"]["en_espera"], 1)
        self.assertEqual(r.data["tiempo_medio_resolucion_horas"], 6.0)

    def test_la_api_cambia_a_espera_y_no_deja_falsear_el_acumulado(self):
        t = self.crear()
        cliente = APIClient()
        cliente.force_authenticate(self.usuario)
        r = cliente.patch(
            f"/api/tickets/{t.pk}/",
            {"estado": "en_espera", "tiempo_en_espera": "99:00:00"},
            format="json",
        )
        self.assertEqual(r.status_code, 200)
        t.refresh_from_db()
        self.assertEqual(t.estado, EN_ESPERA)
        self.assertEqual(t.tiempo_en_espera, timedelta(0))
        detalle = cliente.get(f"/api/tickets/{t.pk}/").data
        self.assertIsNotNone(detalle["espera_desde"])
        self.assertIn("tiempo_en_espera_horas", detalle)