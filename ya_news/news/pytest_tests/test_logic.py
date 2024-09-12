from http import HTTPStatus

from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


NEW_COMMENT_TEXT = 'Обновлённый комментарий'
comment_form_data = {
    'text': NEW_COMMENT_TEXT
}


def test_author_can_delete_comment(
        author_client,
        get_comment_delete_url,
        get_url_to_comment_section
):
    response = author_client.delete(get_comment_delete_url)
    assertRedirects(response, get_url_to_comment_section)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_cant_delete_comment_of_another_user(
        reader_client,
        get_comment_delete_url
):
    response = reader_client.delete(get_comment_delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


def test_author_can_edit_comment(
        author_client,
        comment,
        get_comment_edit_url,
        get_url_to_comment_section
):
    response = author_client.post(get_comment_edit_url, data=comment_form_data)
    assertRedirects(response, get_url_to_comment_section)
    comment.refresh_from_db()
    assert comment.text == NEW_COMMENT_TEXT


def test_user_cant_edit_comment_of_another_user(
        reader_client,
        comment,
        get_comment_edit_url,
):
    old_text = comment.text
    response = reader_client.post(get_comment_edit_url, data=comment_form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == old_text


def test_anonymous_user_cant_create_comment(client, get_news_detail_url):
    client.post(get_news_detail_url, data=comment_form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_can_create_comment(
        author,
        author_client,
        news,
        get_news_detail_url,
        get_url_to_comment_section
):
    response = author_client.post(get_news_detail_url, data=comment_form_data)
    assertRedirects(response, get_url_to_comment_section)
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == NEW_COMMENT_TEXT
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, get_news_detail_url):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(get_news_detail_url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0
