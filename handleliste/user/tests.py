from django.test import TestCase, Client
from django.urls import reverse
import json
from django.contrib.auth import get_user_model

User = get_user_model()
# Create your tests here.


class TestUserViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('user:login')
        self.register_url = reverse('user:register')

    def test_login_GET(self):
        response = self.client.get(self.login_url)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/login.html')

    def test_register_GET(self):
        response = self.client.get(self.register_url)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/register.html')

    def test_login_not_registered_POST(self):
        response = self.client.post(
            self.login_url,
            {
                'username': 'sjokolade',
                'password': 'pudding25t34'
            }
        )
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/login.html')

    def test_login_registered_POST(self):
        User.objects.create_user(
            username='matte4test',
            password='alallaroiq243'
        )
        response = self.client.post(
            self.login_url,
            {
                'username': 'matte4test',
                'password': 'alallaroiq243'
            }
        )
        self.assertEquals(response.status_code, 302)
        # self.assertEquals()
