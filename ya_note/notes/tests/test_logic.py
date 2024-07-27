from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestLogic(TestCase):

    NOTE_TEXT = 'Текст записи'
    NOTE_TITLE = 'Заголовок записи'
    NEW_NOTE_TEXT = 'Текст записи исправленный'
    NEW_NOTE_TITLE = 'Заголовок записи исправленный'

    @classmethod
    def setUpTestData(cls):
        cls.current_user = User.objects.create(username='Тест Тестович')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.current_user)
        cls.other_user = User.objects.create(username='Гарри Поттер')
        cls.other_client = Client()
        cls.other_client.force_login(cls.other_user)
        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            author=cls.current_user
        )
        cls.add_url = reverse('notes:add')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.create_form_data = {
            'title': 'Запись при создании',
            'text': 'Текст при создании'
        }
        cls.edit_form_data = {
            'title': cls.NEW_NOTE_TITLE,
            'text': cls.NEW_NOTE_TEXT
        }
        cls.count_notes = Note.objects.count()

    def test_anonymous_user_cant_create_note(self):
        self.client.post(self.add_url, data=self.create_form_data)
        new_notes_list = Note.objects.count()
        self.assertEqual(new_notes_list, self.count_notes)

    def test_auth_user_can_create_note(self):
        self.auth_client.post(self.add_url, data=self.create_form_data)
        new_notes_list = Note.objects.count()
        self.assertEqual(new_notes_list, self.count_notes + 1)

    def test_user_cant_edit_comment_of_another_user(self):
        response = self.other_client.post(
            self.edit_url,
            data=self.edit_form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT)
        self.assertEqual(self.note.title, self.NOTE_TITLE)

    def test_user_can_edit_note(self):
        response = self.auth_client.post(
            self.edit_url,
            data=self.edit_form_data
        )
        self.assertRedirects(response, '/done/')
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)
        self.assertEqual(self.note.title, self.NEW_NOTE_TITLE)

    def test_user_cant_delete_note_of_another_user(self):
        response = self.other_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        new_notes_list = Note.objects.count()
        self.assertEqual(new_notes_list, self.count_notes)

    def test_user_can_delete_note(self):
        response = self.auth_client.delete(self.delete_url)
        self.assertRedirects(response, '/done/')
        new_notes_list = Note.objects.count()
        self.assertEqual(new_notes_list, self.count_notes - 1)

    def test_auto_slug(self):
        self.assertIsNotNone(self.note.slug)

    def test_create_some_notes_with_same_slug(self):
        slug = self.note.slug
        with self.assertRaises(IntegrityError) as context:
            Note.objects.create(
                title='Запись №3',
                text='Текст записи №3',
                author=self.current_user,
                slug=slug
            )
        self.assertTrue('UNIQUE constraint failed' in str(context.exception))
