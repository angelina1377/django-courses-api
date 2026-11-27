from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django.shortcuts import get_object_or_404

from users.permissions import IsModer, IsOwner, IsNotModer
from .models import Course, Lesson, Subscription
from .paginators import StandardPagination
from .serializers import CourseSerializer, LessonSerializer

from datetime import timedelta
from django.utils import timezone
from .tasks import send_course_update_email

class CourseViewSet(viewsets.ModelViewSet):
    """Полный CRUD для курса с разграничением прав."""
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='moderators').exists():
            return Course.objects.all()
        return Course.objects.filter(owner=user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = [IsAuthenticated, IsNotModer]
        elif self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated, IsModer | IsOwner]
        return [permission() for permission in self.permission_classes]

    def perform_update(self, serializer):
        # 1. Получаем объект ДО сохранения, чтобы взять старое время обновления
        instance = self.get_object()
        old_updated_at = instance.updated_at

        # 2. Сохраняем изменения (теперь instance.updated_at станет "сейчас")
        updated_instance = serializer.save()

        # 3. Проверяем условие: если старого времени не было ИЛИ прошло > 4 часов
        if old_updated_at is None or (timezone.now() - old_updated_at) >= timedelta(hours=4):
            send_course_update_email.delay(updated_instance.id)


class LessonListCreateAPIView(generics.ListCreateAPIView):
    """Список уроков и создание урока."""
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='moderators').exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsNotModer()]
        return [IsAuthenticated()]


class LessonRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Получение одного урока, изменение, удаление."""
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsModer | IsOwner]
    queryset = Lesson.objects.all()


class SubscriptionAPIView(APIView):

    def post(self, *args, **kwargs):
        user = self.request.user
        course_id = self.request.data.get('course')
        course_item = get_object_or_404(Course, id=course_id)

        subs_item = Subscription.objects.filter(user=user, course=course_item)

        if subs_item.exists():
            subs_item.delete()
            message = 'подписка удалена'
        else:
            Subscription.objects.create(user=user, course=course_item)
            message = 'подписка добавлена'

        return Response({"message": message})
