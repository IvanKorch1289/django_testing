from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.test.client import Client

from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст'
    )
    return news


@pytest.fixture
def comment(news, author):
    comment = Comment.objects.create(
        text='!!!!!!!',
        author=author,
        news=news
    )
    return comment


@pytest.fixture
def list_comment(news, author):
    for index in range(2):
        comment = Comment.objects.create(
            text=f'комментарий {index}',
            author=author,
            news=news
        )
        comment.created = datetime.now() + timedelta(days=index)


@pytest.fixture
def id_news_for_args(news):
    return (news.pk,)


@pytest.fixture
def id_comment_for_args(news):
    return (comment.pk,)


@pytest.fixture
def list_news():
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)


@pytest.fixture
def form_data():
    return {'text': 'Новый текст'}
