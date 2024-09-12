from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):
    NOTE_SLUG = 'testslug'
    NOTE_CREATE_DATA = {
        'title': 'Название заметки',
        'text': 'Текст',
        'slug': 'qwerty'
    }
    NOTE_EDIT_DATA = {
        'title': 'Название',
        'text': 'ТекстТекстТекст',
        'slug': NOTE_SLUG + '12345'
    }
    WARNING_NOT_UNIQUE_SLUG = NOTE_SLUG + WARNING

    @classmethod
    def setUpTestData(cls):
        cls.user_creator = User.objects.create(username='Создатель Заметок')
        cls.author_client = Client()
        cls.author_client.force_login(cls.user_creator)

        cls.user_authorized = User.objects.create(
            username='Авторизованный юзер'
        )
        cls.non_author_client = Client()
        cls.non_author_client.force_login(cls.user_authorized)

        cls.user_creator_note = Note.objects.create(
            title='Название заметки',
            text='Текст',
            slug=cls.NOTE_SLUG,
            author=cls.user_creator
        )

        cls.login_url = reverse('users:login')
        cls.success_url = reverse('notes:success')

        cls.url_note_create = reverse('notes:add')
        cls.url_note_edit = reverse('notes:edit',
                                    args=(cls.user_creator_note.slug,))
        cls.url_note_delete = reverse('notes:delete',
                                      args=(cls.user_creator_note.slug,))

    def test_anonymous_cant_create_note(self):
        url = self.url_note_create
        response = self.client.post(
            url,
            self.NOTE_CREATE_DATA
        )

        redirect_url = f'{self.login_url}?next={url}'
        self.assertRedirects(response, redirect_url)

        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)

    def test_anonymous_cant_edit_note(self):
        url = self.url_note_edit
        response = self.client.post(
            url,
            self.NOTE_EDIT_DATA
        )
        redirect_url = f'{self.login_url}?next={url}'
        self.assertRedirects(response, redirect_url)

        self.user_creator_note.refresh_from_db()
        self.assertNotEqual(self.user_creator_note.slug,
                            self.NOTE_EDIT_DATA['slug'])

    def test_anonymous_cant_delete_note(self):
        url = self.url_note_delete
        response = self.client.delete(url)

        redirect_url = f'{self.login_url}?next={url}'
        self.assertRedirects(response, redirect_url)

        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)

    def test_non_author_cant_edit_note(self):
        response = self.non_author_client.post(
            self.url_note_edit,
            self.NOTE_EDIT_DATA
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        self.user_creator_note.refresh_from_db()
        self.assertNotEqual(self.user_creator_note.slug,
                            self.NOTE_EDIT_DATA['slug'])

    def test_non_author_cant_delete_note(self):
        response = self.non_author_client.delete(self.url_note_delete)

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)

    def test_user_can_create_note(self):
        response = self.author_client.post(
            self.url_note_create,
            self.NOTE_CREATE_DATA
        )
        self.assertRedirects(response, self.success_url)

        note_count = Note.objects.count()
        self.assertEqual(note_count, 2)

    def test_user_can_edit_note(self):
        response = self.author_client.post(
            self.url_note_edit,
            self.NOTE_EDIT_DATA
        )
        self.assertRedirects(response, self.success_url)

        self.user_creator_note.refresh_from_db()
        self.assertEqual(self.user_creator_note.slug,
                         self.NOTE_EDIT_DATA['slug'])

    def test_user_can_delete_note(self):
        response = self.author_client.delete(self.url_note_delete)
        self.assertRedirects(response, self.success_url)

        note_count = Note.objects.count()
        self.assertEqual(note_count, 0)

    def test_user_cant_create_note_with_not_unique_slug(self):
        response = self.author_client.post(
            self.url_note_create,
            {'title': 'Название заметки',
             'text': 'Текст',
             'slug': self.NOTE_SLUG}
        )
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=self.WARNING_NOT_UNIQUE_SLUG
        )

        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)

    def test_empty_slug(self):
        no_slug_create_data = self.NOTE_CREATE_DATA
        no_slug_create_data.pop('slug')
        response = self.author_client.post(
            self.url_note_create,
            no_slug_create_data
        )
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), 2)
        new_note = Note.objects.last()
        expected_slug = slugify(no_slug_create_data['title'])

        self.assertEqual(new_note.slug, expected_slug)
