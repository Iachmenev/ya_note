from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author
        )

    def test_pages_availability(self):
        urls = ('notes:home',
                'users:login',
                'users:logout',
                'users:signup'
                )

        for page in urls:
            with self.subTest(name=page):
                url = reverse(page)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        urls = ('notes:list',
                'notes:add',
                'notes:success',
                )

        for page in urls:
            self.client.force_login(self.reader)
            with self.subTest(name=page):
                url = reverse(page)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_detail_edit_and_delete(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('notes:detail', 'notes:edit', 'notes:delete'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        slug_urls = ('notes:detail', 'notes:edit', 'notes:delete')
        without_slug_urls = ('notes:add', 'notes:list', 'notes:success')
        for name in slug_urls:
            with self.subTest(name=name):
                url = reverse(name, args=(self.note.slug,))
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
        for name in without_slug_urls:
            with self.subTest(name=name):
                url = reverse(name)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
