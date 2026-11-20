from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from lms.models import Course, Lesson, Subscription
from users.models import User


class LessonTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create(email='test@mail.ru')
        self.user.set_password('qwerty123')
        self.user.save()

        self.other_user = User.objects.create(email='stranger@mail.ru')
        self.other_user.set_password('qwerty123')
        self.other_user.save()

        self.course = Course.objects.create(title='Django', owner=self.user)
        self.lesson = Lesson.objects.create(
            title='Урок 1',
            video_link='https://youtube.com/watch?v=demo1',
            course=self.course,
            owner=self.user,
        )

    def test_lesson_list(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('lms:lesson-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_lesson_create(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'title': 'Новый урок',
            'video_link': 'https://youtube.com/watch?v=new',
            'course': self.course.id,
        }
        response = self.client.post(reverse('lms:lesson-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 2)

    def test_lesson_create_forbidden_url(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'title': 'Плохой урок',
            'video_link': 'https://stepik.org/lesson',
            'course': self.course.id,
        }
        response = self.client.post(reverse('lms:lesson-list'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_lesson_retrieve(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('lms:lesson-detail', args=[self.lesson.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Урок 1')

    def test_lesson_update(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            reverse('lms:lesson-detail', args=[self.lesson.id]),
            {'title': 'Обновлённый урок'},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_lesson_delete(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(reverse('lms:lesson-detail', args=[self.lesson.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.count(), 0)

    def test_lesson_delete_no_permission(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(reverse('lms:lesson-detail', args=[self.lesson.id]))
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])


class SubscriptionTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create(email='sub@mail.ru')
        self.user.set_password('qwerty123')
        self.user.save()
        self.course = Course.objects.create(title='Курс', owner=self.user)

    def test_subscribe_toggle(self):
        self.client.force_authenticate(user=self.user)

        # подписка добавляется
        response = self.client.post(reverse('lms:subscription-toggle'), {'course': self.course.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'подписка добавлена')
        self.assertTrue(Subscription.objects.filter(user=self.user, course=self.course).exists())

        # повторная — удаляется
        response = self.client.post(reverse('lms:subscription-toggle'), {'course': self.course.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'подписка удалена')
        self.assertFalse(Subscription.objects.filter(user=self.user, course=self.course).exists())

    def test_course_contains_is_subscribed(self):
        self.client.force_authenticate(user=self.user)
        self.client.post(reverse('lms:subscription-toggle'), {'course': self.course.id})
        response = self.client.get(reverse('lms:course-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results'] if 'results' in response.data else response.data
        self.assertTrue(results[0]['is_subscribed'])

# Create your tests here.
