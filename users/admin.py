from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Payment


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'phone', 'city')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Личная информация', {'fields': ('phone', 'city', 'avatar')}),
        ('Права', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('email', 'password1', 'password2')}),
    )
    ordering = ('email',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'paid_course', 'amount', 'payment_method', 'payment_date', 'status')
    list_filter = ('payment_method', 'status')
    search_fields = ('user__email',)
