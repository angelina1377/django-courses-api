from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from .models import Subscription, Course


@shared_task
def send_course_update_email(course_id):
    course = Course.objects.get(id=course_id)
    emails = Subscription.objects.filter(course=course).values_list('user__email', flat=True)
    for email in emails:
        send_mail(
            subject=f'Обновление курса {course.title}',
            message='Курс, на который вы подписаны, был обновлён!',
            from_email=None,          # возьмётся из DEFAULT_FROM_EMAIL
            recipient_list=[email],
        )
