from rest_framework import generics

from .models import User
from .serializers import UserSerializer


class UserProfileUpdateAPIView(generics.RetrieveUpdateAPIView):
    """Просмотр и редактирование профиля любого пользователя."""
    serializer_class = UserSerializer
    queryset = User.objects.all()

