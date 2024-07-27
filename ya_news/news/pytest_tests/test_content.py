import pytest
from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm


@pytest.mark.usefixtures('list_news')
@pytest.mark.django_db
def test_news_count(admin_client,):
    url = reverse('news:home')
    response = admin_client.get(url)
    count_news = response.context['object_list'].count()
    assert count_news <= settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.usefixtures('list_news')
@pytest.mark.django_db
def test_news_order(admin_client):
    url = reverse('news:home')
    response = admin_client.get(url)
    all_dates = [news.date for news in response.context['object_list']]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.usefixtures('list_comment')
@pytest.mark.django_db
def test_comments_order(admin_client, id_news_for_args):
    url = reverse('news:detail', args=id_news_for_args)
    response = admin_client.get(url)
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, id_news_for_args):
    url = reverse('news:detail', args=id_news_for_args)
    response = client.get(url)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_authorized_client_has_form(admin_client, id_news_for_args):
    url = reverse('news:detail', args=id_news_for_args)
    response = admin_client.get(url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
