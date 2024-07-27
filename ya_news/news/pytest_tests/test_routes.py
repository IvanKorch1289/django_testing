from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    'url, args',
    (
        ('news:home', None),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
        ('news:detail', pytest.lazy_fixture('id_news_for_args'))
    ),
)
def test_main_pages_availability_for_auth_client(admin_client, url, args):
    url = reverse(url, args=args)
    response = admin_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url, args',
    (
        ('news:home', None),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
        ('news:detail', pytest.lazy_fixture('id_news_for_args'))
    ),
)
def test_main_pages_availability_for_anon_client(client, url, args):
    url = reverse(url, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'param_client, expected_status',
    (
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'url',
    ('news:edit', 'news:delete'),
)
def test_news_actions_pages_availability(
    param_client,
    expected_status,
    url,
    comment
):
    url = reverse(url, args=(comment.pk,))
    response = param_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url',
    ('news:edit', 'news:delete'),
)
def test_redirects(client, url, comment):
    login_url = reverse('users:login')
    url = reverse(url, args=(comment.pk,))
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
