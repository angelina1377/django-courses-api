from django.urls import path

from rest_framework.routers import DefaultRouter

from .views import PaymentViewSet, RegisterAPIView, UserListAPIView

router = DefaultRouter()
router.register(r'payments', PaymentViewSet, basename='payments')

urlpatterns = router.urls + [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('', UserListAPIView.as_view(), name='user-list'),
]

