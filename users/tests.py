from django.test import TestCase
from django.urls import reverse
from django.test.utils import override_settings

from messenger.models import User
from users.forms import UserRegisterForm


class ViewsTest(TestCase):

    def setUp(self) -> None:
        self.valid_credentials = {
            'username': 'test_user',
            'email': 'test@test.ru',
            'password1': 'secret_password',
            'password2': 'secret_password'
        }
        self.invalid_credentials = {
            'username': 'test_user',
            'email': 'testtest',
            'password1': 'secret_password',
            'password2': 'secret'
        }

    @override_settings(DEBUG=False)
    def test_registration_form_valid(self):
        form = UserRegisterForm(self.valid_credentials)
        self.assertTrue(form.is_valid())

    @override_settings(DEBUG=False)
    def test_registration_form_invalid(self):
        self.client.post(reverse('register'), self.valid_credentials, follow=True)
        form = UserRegisterForm(self.invalid_credentials)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 3)
        self.assertEqual(len(User.objects.filter(username='test_user')), 1)

    @override_settings(DEBUG=False)
    def test_registration_page(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')

    @override_settings(DEBUG=False)
    def test_registration_page(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')

    @override_settings(DEBUG=False)
    def test_registration_create_user(self):
        response = self.client.post(reverse('register'), self.valid_credentials, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')
        self.assertTrue(User.objects.get(username='test_user'))

    @override_settings(DEBUG=False)
    def test_registration_create_invalid_user_failed(self):
        response = self.client.post(reverse('register'), self.invalid_credentials, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')
        self.assertRaises(User.DoesNotExist, User.objects.get, username='test_user')

    def test_login(self):
        self.test_registration_create_user()
        response = self.client.post(reverse('login'), {
            'username': 'test_user',
            'password': 'secret_password',
        }, follow=True)
        self.assertTrue(response.context['user'].is_active)
        self.assertRedirects(response, reverse('main'), status_code=302, target_status_code=200)
