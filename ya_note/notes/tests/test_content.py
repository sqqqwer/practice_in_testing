from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user_creator = User.objects.create(username='Создатель Заметок')
        cls.user_authorized = User.objects.create(
            username='Авторизованный юзер'
        )

        cls.user_creator_note = Note.objects.create(text='Текст',
                                                    slug='testslug',
                                                    author=cls.user_creator)

    def test_note_non_author_visibility(self):
        users_note_count = (
            (self.user_creator, 1),
            (self.user_authorized, 0)
        )
        url = reverse('notes:list')
        for user, note_count in users_note_count:
            with self.subTest(user=user):
                self.client.force_login(user)
                response = self.client.get(url)

                context_object = response.context['object_list']
                self.assertEqual(context_object.count(), note_count)

    def test_pages_contains_form(self):
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.user_creator_note.slug,))
        )
        self.client.force_login(self.user_creator)
        for name, args in urls:
            with self.subTest(name=name, args=args):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
