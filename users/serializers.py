from rest_framework import serializers
from .models import User, Payment, Course, Lesson



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'phone', 'city', 'avatar')

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

class CourseBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ('id', 'title')


class LessonBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ('id', 'title')


class PaymentHistorySerializer(serializers.ModelSerializer):
    paid_course = CourseBriefSerializer(read_only=True)
    paid_lesson = LessonBriefSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = ('paid_course', 'paid_lesson', 'amount', 'payment_method', 'payment_date')


class UserSerializer(serializers.ModelSerializer):
    payments = PaymentHistorySerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'phone', 'city', 'avatar', 'payments')
