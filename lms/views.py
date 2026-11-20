from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated

from users.permissions import IsModer, IsOwner
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """Полный CRUD для курса с разграничением прав."""
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='moderators').exists():
            return Course.objects.all()          # модератор видит всё
        return Course.objects.filter(owner=user)  # обычный — только своё

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        if self.action == 'create':
            # создание доступно любому авторизованному, КРОМЕ модератора
            self.permission_classes = [IsAuthenticated, ~IsModer]
        elif self.action in ['update', 'partial_update', 'destroy']:
            # редактирование и удаление: модератор ИЛИ владелец
            self.permission_classes = [IsAuthenticated, IsModer | IsOwner]
        return [permission() for permission in self.permission_classes]


class LessonListCreateAPIView(generics.ListCreateAPIView):
    """Список уроков и создание урока."""
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='moderators').exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = [IsAuthenticated, ~IsModer]
        return [permission() for permission in self.permission_classes]


class LessonRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Получение одного урока, изменение, удаление."""
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsModer | IsOwner]
    queryset = Lesson.objects.all()


