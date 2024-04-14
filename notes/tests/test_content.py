from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='note-slug',
            author=cls.author,
        )

    def test_notes_list_for_different_users(self):
        users = (self.author, self.reader)
        for user in users:
            self.client.force_login(user)
            url = reverse('notes:list')
            response = self.client.get(url)
            object_list = response.context['object_list']
            self.assertEqual((self.note in object_list), object_list.count())

    def test_authorized_client_has_form(self):
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        for name, args in urls:
            url = reverse(name, args=args)
            self.client.force_login(self.author)
            response = self.client.get(url)
            self.assertIn('form', response.context)
            self.assertIsInstance(response.context['form'], NoteForm)
