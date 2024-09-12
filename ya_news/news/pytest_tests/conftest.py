from datetime import timedelta

import pytest
from django.conf import settings
from django.test.client import Client
from django.utils import timezone
from django.urls import reverse

from news.models import Comment, News


@pytest.fixture(autouse=True)
def enable_db_access(db):
    pass


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Лев Толстой')


@pytest.fixture
def reader(django_user_model):
    return django_user_model.objects.create(username='Читатель простой')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader):
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст'
    )
    return news


@pytest.fixture
def ten_news():
    today = timezone.now()
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
def get_news_id(news):
    return (news.id,)


@pytest.fixture
def get_news_detail_url(get_news_id):
    return reverse('news:detail', args=get_news_id)


@pytest.fixture
def comment(news, author):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )
    return comment


@pytest.fixture
def ten_comments(news, author):
    # Запоминаем текущее время:
    now = timezone.now()
    # Создаём комментарии в цикле.
    for index in range(10):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()


@pytest.fixture
def get_comment_id(comment):
    return (comment.id,)


@pytest.fixture
def get_comment_edit_url(get_comment_id):
    return reverse('news:edit', args=get_comment_id)


@pytest.fixture
def get_comment_delete_url(get_comment_id):
    return reverse('news:delete', args=get_comment_id)


@pytest.fixture
def get_url_to_comment_section(get_news_detail_url):
    return get_news_detail_url + '#comments'
