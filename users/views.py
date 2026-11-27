import stripe
from django_filters.rest_framework import DjangoFilterBackend, FilterSet
from rest_framework import filters, generics, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django.conf import settings
from django.shortcuts import get_object_or_404

from lms.services import create_stripe_product, create_stripe_price, create_stripe_session

from .models import Payment, User
from .serializers import PaymentSerializer, UserSerializer, UserRegisterSerializer, UserPublicSerializer

stripe.api_key = settings.STRIPE_API_KEY


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

    def perform_create(self, serializer):
        payment = serializer.save(user=self.request.user)
        course = payment.paid_course

        if course is None:
            # Оплата урока или ручная запись без курса — Stripe не трогаем
            return

        product_id = create_stripe_product(course)
        price_id = create_stripe_price(course, product_id)
        session_id, link = create_stripe_session(price_id)

        payment.stripe_product_id = product_id
        payment.stripe_price_id = price_id
        payment.stripe_session_id = session_id
        payment.link = link
        payment.payment_method = Payment.STRIPE
        payment.save()


class PaymentStatusAPIView(APIView):
    """Проверка статуса платежа по сессии в Stripe (доп. задание)."""

    def get(self, request, pk):
        payment = get_object_or_404(Payment, id=pk)

        if not payment.stripe_session_id:
            return Response({'detail': 'Платёж не связан со Stripe'}, status=400)

        session = stripe.checkout.Session.retrieve(payment.stripe_session_id)
        payment.status = session.payment_status  # 'paid' или 'unpaid'
        payment.save()

        return Response({
            'payment_id': payment.id,
            'status': payment.status,
            'link': payment.link,
        })


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



