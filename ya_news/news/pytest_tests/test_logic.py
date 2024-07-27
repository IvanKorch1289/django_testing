import pytest

from django.urls import reverse

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
    client,
    id_news_for_args,
    form_data
):
    object_counts = Comment.objects.count()
    url = reverse('news:detail', args=id_news_for_args)
    client.post(url, data=form_data)
    assert Comment.objects.count() == object_counts


@pytest.mark.django_db
def test_user_can_create_note(admin_client, id_news_for_args, form_data):
    object_counts = Comment.objects.count()
    url = reverse('news:detail', args=id_news_for_args)
    admin_client.post(url, data=form_data)
    assert Comment.objects.count() == object_counts + 1
    new_comment = Comment.objects.last()
    assert new_comment.text == form_data['text']


@pytest.mark.django_db
def test_user_cant_use_bad_words(admin_client, id_news_for_args):
    url = reverse('news:detail', args=id_news_for_args)
    for word in BAD_WORDS:
        response = admin_client.post(url, data={'text': f'Текст {word}'})
        form_error = response.context_data['form'].errors['text']
        assert WARNING in form_error


@pytest.mark.django_db
def test_author_can_edit_note(author_client, comment, form_data):
    url = reverse('news:edit', args=(comment.pk,))
    author_client.post(url, data=form_data)
    comment.refresh_from_db()
    assert comment.text == form_data['text']


@pytest.mark.django_db
def test_author_can_delete_note(author_client, comment):
    count_comments = Comment.objects.count()
    url = reverse('news:delete', args=(comment.pk,))
    author_client.delete(url)
    assert Comment.objects.count() == count_comments - 1


@pytest.mark.django_db
def test_not_author_cant_edit_note(not_author_client, comment, form_data):
    url = reverse('news:edit', args=(comment.pk,))
    not_author_client.post(url, data=form_data)
    comment.refresh_from_db()
    comment_db = Comment.objects.get(pk=comment.pk)
    assert comment.text == comment_db.text


@pytest.mark.django_db
def test_not_author_cant_delete_note(not_author_client, comment):
    count_comments = Comment.objects.count()
    url = reverse('news:delete', args=(comment.pk,))
    not_author_client.delete(url)
    comment.refresh_from_db()
    assert Comment.objects.count() == count_comments
