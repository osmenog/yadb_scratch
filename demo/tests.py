from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase


class SignupViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.superuser = User.objects.create_superuser(username='super', password='secret', email='super@example.com')

    def setUp(self):
        self.client.force_login(self.superuser)

    @patch('demo.views.send_email')
    def test_signup_with_registered_user(self, send_mail_mock):
        # при отправлении пост запроса с полями существующего юзера (юзернейм и емайл),
        # не выдавало ошибку, а отправлялось письмо

        user1 = User.objects.create(username='user1', email='asd@asd.asd')
        resp = self.client.post(
            reverse('signup'),
            data={
                'username': 'user1',
                'email': 'asd@asd.asd'
            }
        )
        self.assertEqual(resp.status_code, 200, msg=resp.data)
        send_mail_mock.assert_called_once()

    @patch('demo.views.send_email')
    def test_signup_with_new_user(self, send_mail_mock):
        # в случае если такого пользователя с юзернеймом и емэйлом нет,
        # то создавался новый и ему также отправялось письмо

        resp = self.client.post(
            reverse('signup'),
            data={
                'username': 'user1',
                'email': 'asd@asd.asd'
            }
        )
        self.assertEqual(resp.status_code, 200)

        users = User.objects.filter(username='user1', email='asd@asd.asd')
        self.assertEqual(users.count(), 1)

        send_mail_mock.assert_called_once()

    def test_username_validation(self):
        resp = self.client.post(
            reverse('signup'),
            data={
                'username': 'me',
                'email': 'asd@asd.asd'
            }
        )
        self.assertEqual(resp.status_code, 400, msg=resp.data)
        self.assertIn('username', resp.data)
        self.assertEqual(resp.data['username'][0], "Имя пользователя 'me' запрещено, используйте другое.")

    def test_email_validation(self):
        resp = self.client.post(
            reverse('signup'),
            data={
                'username': 'asd',
                'email': 'non-valid-email'
            }
        )
        self.assertEqual(resp.status_code, 400, msg=resp.data)
        self.assertIn('email', resp.data)
        self.assertEqual(resp.data['email'][0], "Enter a valid email address.")

