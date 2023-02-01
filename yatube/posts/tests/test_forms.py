import shutil
import tempfile
from http import HTTPStatus

from posts.forms import PostForm
from posts.models import Group, Post

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
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
        cls.form = PostForm()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_create_post(self):
        """Тест на создание нового поста."""
        form_data = {
            "text": "Тестовый текст 2",
            "author": self.author,
            "group": self.group.id,
        }
        posts_count = Post.objects.count()
        response = self.authorized_client.post(
            reverse("posts:post_create"),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse(
                "posts:profile", kwargs={"username": self.author.username}
            ),
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        last_object = Post.objects.latest("id")
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(last_object.text, "Тестовый текст 2")

    def test_edit_post(self):
        """Тест на редактирование поста."""
        posts_count = Post.objects.count()
        form_data = {
            "text": "Измененный тестовый текст",
            "group": self.group.id,
        }
        response = self.authorized_client.post(
            reverse(
                "posts:post_edit",
                kwargs={"post_id": PostCreateFormTests.post.pk},
            ),
            data=form_data,
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(
            response,
            reverse(
                "posts:post_detail",
                kwargs={"post_id": PostCreateFormTests.post.pk},
            ),
        )
        edit_object = Post.objects.get(id=PostCreateFormTests.post.pk)
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(edit_object.text, "Измененный тестовый текст")
        self.assertEqual(edit_object.author.username, self.author.username)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPictureCreateFormTests(TestCase):
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
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_create_post_with_image(self):
        """Тест на создание поста с картинкой через PostForm."""
        posts_count = Post.objects.count()
        small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )
        uploaded = SimpleUploadedFile(
            name="small.gif", content=small_gif, content_type="image/gif"
        )
        form_data = {
            "text": "Тестовый текст",
            "group": self.group.id,
            "image": uploaded,
        }
        response = self.authorized_client.post(
            reverse("posts:post_create"),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse(
                "posts:profile", kwargs={"username": self.author.username}
            ),
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text="Тестовый текст",
                group=self.group.id,
                image="posts/small.gif",
            ).exists()
        )
