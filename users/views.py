from django_filters.rest_framework import DjangoFilterBackend, FilterSet
from rest_framework import filters, generics, viewsets

from .models import Payment, User
from .serializers import PaymentSerializer, UserSerializer


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
    serializer_class = UserSerializer
    queryset = User.objects.all()


