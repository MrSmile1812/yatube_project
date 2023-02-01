import tempfile
from http import HTTPStatus

from posts.forms import PostForm
from posts.models import Comment, Group, Post

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username="Автор поста")
        cls.group = Group.objects.create(
            title="Тестовый заголовок",
            description="Тестовое описание",
            slug="test_slug",
        )
        cls.post = Post.objects.create(
            text="Тестовый текст",
            author=cls.author,
            group=cls.group,
        )
        cls.comment = Comment.objects.create(
            author=cls.author,
            text="Тестовый текст комментария",
        )
        cls.form = PostForm()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_create_comment(self):
        """Тест на создание комментария на странице поста."""
        comments_count = Comment.objects.count()

        form_data = {
            "text": "Тестовый текст комментария",
            "author": self.author,
        }
        response = self.authorized_client.get(
            reverse(
                "posts:add_comment",
                kwargs={"post_id": PostCreateFormTests.post.pk},
            ),
            data=form_data,
            follow=True,
        )
        self.assertEqual(Comment.objects.count(), comments_count)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_user_create_comment(self):
        """Тест, что комментарий может сделать только/
        авторизованный пользователь."""
        comments_count = Comment.objects.count()
        form_data = {
            "text": "Тестовый текст комментария",
            "author": self.guest_client,
        }
        response = self.guest_client.post(
            reverse(
                "posts:add_comment",
                kwargs={"post_id": PostCreateFormTests.post.pk},
            ),
            data=form_data,
            follow=True,
        )
        self.assertEqual(Comment.objects.count(), comments_count)
        self.assertRedirects(response, "/auth/login/?next=/posts/1/comment/")

        response = self.authorized_client.post(
            reverse(
                "posts:add_comment",
                kwargs={"post_id": PostCreateFormTests.post.pk},
            ),
            data=form_data,
            follow=True,
        )
        self.assertEqual(Comment.objects.count(), comments_count + 1)
