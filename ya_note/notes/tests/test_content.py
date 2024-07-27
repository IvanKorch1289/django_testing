from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):

    HOME_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Иван Корч')
        cls.reader = User.objects.create(username='Тест Тестович')
        cls.note = Note.objects.create(
            title='Запись 1',
            author=cls.author,
            text='Текст записи',
            slug='note_1tre')

    def test_note_on_main(self):
        self.client.force_login(self.author)
        response = self.client.get(self.HOME_URL)
        object_list = response.context['object_list']
        notes_id = [note.id for note in object_list]
        self.assertIn(self.note.id, notes_id)

    def test_author_note(self):
        self.client.force_login(self.author)
        response = self.client.get(self.HOME_URL)
        object_list = response.context['object_list']
        authors = [note.author for note in object_list]
        self.assertNotIn(self.reader, authors)

    def test_authorized_client_has_form(self):
        self.client.force_login(self.author)
        url = reverse('notes:add')
        response = self.client.get(url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
