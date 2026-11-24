from rest_framework import serializers
from .models import Course, Lesson, Subscription
from lms.validators import validate_youtube_url

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ('id', 'title', 'description', 'preview', 'video_link', 'course', 'owner')
        read_only_fields = ('owner',)
        extra_kwargs = {
            'video_link': {'validators': [validate_youtube_url]},
        }

class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ('id', 'title', 'description', 'preview', 'owner', 'lessons', 'lessons_count')
        read_only_fields = ('owner',)

    def get_lessons_count(self, obj):
        return obj.lessons.count()

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ('id', 'title', 'description', 'preview', 'video_link', 'course', 'owner')
        read_only_fields = ('owner',)
        extra_kwargs = {
            'video_link': {'validators': [validate_youtube_url]},
        }


class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ('id', 'title', 'description', 'preview', 'owner',
                  'lessons', 'lessons_count', 'is_subscribed')
        read_only_fields = ('owner',)

    def get_lessons_count(self, obj):
        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return Subscription.objects.filter(user=user, course=obj).exists()
        return False

