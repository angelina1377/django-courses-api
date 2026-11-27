from django.conf import settings
from lms.models import Course, Lesson
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('У пользователя должен быть email')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, verbose_name='Email')
    phone = models.CharField(max_length=35, blank=True, null=True, verbose_name='Телефон')
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name='Город')
    avatar = models.ImageField(upload_to='users/avatars/', blank=True, null=True, verbose_name='Аватарка')

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

class Payment(models.Model):
    CASH = 'cash'
    TRANSFER = 'transfer'
    STRIPE = 'stripe'

    PAYMENT_METHODS = [
        (CASH, 'наличные'),
        (TRANSFER, 'перевод на счет'),
        (STRIPE, 'оплата через Stripe'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name='Пользователь',
    )
    payment_date = models.DateField(auto_now_add=True, verbose_name='Дата оплаты')
    paid_course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name='Оплаченный курс',
    )
    paid_lesson = models.ForeignKey(
        Lesson,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name='Оплаченный урок',
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Сумма оплаты')

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS,
        default=TRANSFER,
        verbose_name='Способ оплаты',
    )

    stripe_product_id = models.CharField(max_length=255, blank=True, null=True, verbose_name='ID продукта Stripe')
    stripe_price_id = models.CharField(max_length=255, blank=True, null=True, verbose_name='ID цены Stripe')
    stripe_session_id = models.CharField(max_length=255, blank=True, null=True, verbose_name='ID сессии Stripe')
    link = models.URLField(max_length=500, blank=True, null=True, verbose_name='Ссылка на оплату')
    status = models.CharField(max_length=50, default='pending', verbose_name='Статус платежа')


    def __str__(self):
        return f'{self.user} — {self.amount} ({self.payment_date})'

    class Meta:
        verbose_name = 'Платёж'
        verbose_name_plural = 'Платежи'
        ordering = ['-payment_date']

