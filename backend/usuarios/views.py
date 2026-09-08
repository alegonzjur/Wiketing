from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import TicketingTokenObtainPairSerializer


class TicketingTokenObtainPairView(TokenObtainPairView):
    serializer_class = TicketingTokenObtainPairSerializer


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class UsuarioActualView(APIView):
    """
    Devuelve los datos del usuario autenticado. Necesario para poder
    repoblar el estado de React tras recargar la página (F5): el endpoint
    de refresh de JWT solo devuelve un access token nuevo, no quién es
    el usuario.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        u = request.user
        return Response({
            "id": u.id,
            "username": u.username,
            "first_name": u.first_name,
            "last_name": u.last_name,
        })
