from http import HTTPStatus

from pytest_django.asserts import assertFormError, assertRedirects
from django.urls import reverse

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


NEW_COMMENT_TEXT = 'Обновлённый комментарий'
comment_form_data = {
    'text': NEW_COMMENT_TEXT
}


def test_author_can_delete_comment(
        author_client,
        news,
        comment,
):
    expected_comment_count = Comment.objects.count()
    url = reverse('news:delete', args=(comment.id,))
    success_url = reverse('news:detail', args=(news.id,)) + '#comments'

    response = author_client.delete(url)
    expected_comment_count -= 1

    assertRedirects(response, success_url)
    comments_count = Comment.objects.count()
    assert comments_count == expected_comment_count


def test_user_cant_delete_comment_of_another_user(reader_client, comment):
    expected_comment_count = Comment.objects.count()
    url = reverse('news:delete', args=(comment.id,))
    response = reader_client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == expected_comment_count


def test_author_can_edit_comment(
        author_client,
        news,
        comment
):
    url = reverse('news:edit', args=(comment.id,))
    success_url = reverse('news:detail', args=(news.id,)) + '#comments'
    response = author_client.post(url, data=comment_form_data)
    assertRedirects(response, success_url)
    comment.refresh_from_db()
    assert comment.text == NEW_COMMENT_TEXT


def test_user_cant_edit_comment_of_another_user(
        reader_client,
        comment,
):
    old_text = comment.text
    url = reverse('news:edit', args=(comment.id,))
    response = reader_client.post(url, data=comment_form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == old_text


def test_anonymous_user_cant_create_comment(client, news):
    expected_comment_count = Comment.objects.count()
    url = reverse('news:detail', args=(news.id,))
    client.post(url, data=comment_form_data)
    comments_count = Comment.objects.count()
    assert comments_count == expected_comment_count


def test_user_can_create_comment(
        author,
        author_client,
        news,
):
    expected_comment_count = Comment.objects.count()
    url = reverse('news:detail', args=(news.id,))
    success_url = reverse('news:detail', args=(news.id,)) + '#comments'

    response = author_client.post(url, data=comment_form_data)
    expected_comment_count += 1
    assertRedirects(response, success_url)

    comments_count = Comment.objects.count()
    assert comments_count == expected_comment_count
    comment = Comment.objects.get()
    assert comment.text == NEW_COMMENT_TEXT
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, news):
    expected_comment_count = Comment.objects.count()
    url = reverse('news:detail', args=(news.id,))
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == expected_comment_count
