from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


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

        cls.URL_NOTE_DETAIL = ('notes:detail', (cls.user_creator_note.slug,))
        cls.URL_NOTE_EDIT = ('notes:edit', (cls.user_creator_note.slug,))
        cls.URL_NOTE_DELETE = ('notes:delete', (cls.user_creator_note.slug,))
        cls.URL_NOTE_ADD = ('notes:add', None)
        cls.URL_NOTE_LIST = ('notes:list', None)
        cls.URL_NOTE_SUCCESS = ('notes:success', None)
        cls.URL_USERS_LOGIN = 'users:login'

    def test_users_access_note(self):
        urls = (
            self.URL_NOTE_DETAIL,
            self.URL_NOTE_EDIT,
            self.URL_NOTE_DELETE,
        )
        users_http_statues = (
            (self.user_creator, HTTPStatus.OK),
            (self.user_authorized, HTTPStatus.NOT_FOUND)
        )

        for user, user_http_status in users_http_statues:
            self.client.force_login(user)

            for name, args in urls:
                with self.subTest(name=name, args=args):
                    url = reverse(name, args=args)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, user_http_status)

    def test_user_pages_availabile(self):
        urls = (
            self.URL_NOTE_LIST,
            self.URL_NOTE_ADD,
            self.URL_NOTE_SUCCESS,
        )
        for name, args in urls:
            with self.subTest(name=name, args=args):
                url = reverse(name, args=args)
                self.client.force_login(self.user_authorized)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_anonymous_pages_availabile(self):
        urls = (
            'notes:home',
            self.URL_USERS_LOGIN,
            'users:logout',
            'users:signup'
        )

        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_anonymous_login_redirect(self):
        urls = (
            self.URL_NOTE_LIST,
            self.URL_NOTE_ADD,
            self.URL_NOTE_SUCCESS,
            self.URL_NOTE_DETAIL,
            self.URL_NOTE_EDIT,
            self.URL_NOTE_DELETE,
        )
        login_url = reverse(self.URL_USERS_LOGIN)

        for name, args in urls:
            with self.subTest(name=name, args=args):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
