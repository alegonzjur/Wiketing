"""
Punto de entrada de producción (Windows): arranca Django con Waitress.

Gunicorn no funciona en Windows, así que el servicio de NSSM ejecuta este fichero:

    python run.py

Escucha SOLO en 127.0.0.1: el único que puede llegar hasta aquí es Nginx, que
está en la misma máquina y es quien termina el HTTPS.

Variables de entorno opcionales:
    WAITRESS_HOST   (por defecto 127.0.0.1)
    WAITRESS_PORT   (por defecto 8001)
"""
import os

from waitress import serve

from config.wsgi import application

HOST = os.environ.get("WAITRESS_HOST", "127.0.0.1")
PORT = int(os.environ.get("WAITRESS_PORT", "8001"))

if __name__ == "__main__":
    serve(
        application,
        host=HOST,
        port=PORT,
        # Nginx habla con Waitress por HTTP plano y avisa del HTTPS original con
        # la cabecera X-Forwarded-Proto. Waitress, por defecto, DESCARTA esa
        # cabecera: sin las tres líneas siguientes, Django cree que la petición
        # es http y el login del admin falla con "Origin checking failed".
        # Solo se confía en el proxy local (127.0.0.1) y solo en esa cabecera.
        trusted_proxy="127.0.0.1",
        trusted_proxy_headers={"x-forwarded-proto"},
        clear_untrusted_proxy_headers=True,
    )