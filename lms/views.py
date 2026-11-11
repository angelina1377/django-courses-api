from rest_framework import viewsets, generics

from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """Полный CRUD для курса: список, одна запись, создание, изменение, удаление."""
    serializer_class = CourseSerializer
    queryset = Course.objects.all()


class LessonListCreateAPIView(generics.ListCreateAPIView):
    """Список уроков и создание урока."""
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()


class LessonRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Получение одного урока, изменение, удаление."""
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()

