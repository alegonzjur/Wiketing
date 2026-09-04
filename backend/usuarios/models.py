from django.contrib.auth.models import AbstractUser


class Usuario(AbstractUser):
    """
    Usuario propio desde el día uno.

    Hoy no añade campos sobre AbstractUser: el objetivo de definirlo ya es
    puramente evitar el problema de Django de no poder migrar
    AUTH_USER_MODEL a mitad de proyecto sin rehacer migraciones.

    Cuando llegue el multi-usuario (Fase futura), el campo `rol`
    (admin / agente / solicitante) se añade aquí sin tocar el resto
    del modelo de datos.
    """
    pass
