from django_filters.rest_framework import DjangoFilterBackend, FilterSet
from rest_framework import filters, generics, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import Payment, User
from .serializers import PaymentSerializer, UserSerializer, UserRegisterSerializer, UserPublicSerializer


class PaymentFilter(FilterSet):
    class Meta:
        model = Payment
        fields = {
            'paid_course': ['exact'],
            'paid_lesson': ['exact'],
            'payment_method': ['exact'],
        }


class PaymentViewSet(viewsets.ModelViewSet):
    """CRUD платежей + фильтрация и сортировка по дате оплаты."""
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = PaymentFilter
    ordering_fields = ['payment_date']
    ordering = ['-payment_date']


class UserProfileUpdateAPIView(generics.RetrieveUpdateAPIView):
    """Просмотр и редактирование профиля пользователя."""
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.request.user.pk == self.kwargs['pk']:
            return UserSerializer  # свой профиль — полный
        return UserPublicSerializer  # чужой — публичный


class RegisterAPIView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]  # регистрация открыта всем


class UserListAPIView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


