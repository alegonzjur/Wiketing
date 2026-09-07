from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class TicketingTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Extiende el serializer estándar de simplejwt para devolver también los
    datos básicos del usuario junto a los tokens. Sin esto, el frontend
    tendría que hacer una segunda petición solo para saber quién inició
    sesión (username, nombre) tras el login.
    """

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = {
            "id": self.user.id,
            "username": self.user.username,
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
        }
        return data