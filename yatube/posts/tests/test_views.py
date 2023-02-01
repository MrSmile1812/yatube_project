from django import forms
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Follow, Group, Post

User = get_user_model()
first_post_on_page = 0
AMOUNT_OF_POSTS = 13
POSTS_ON_PAGE = 10


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )
        cls.uploaded = SimpleUploadedFile(
            name="small.gif", content=cls.small_gif, content_type="image/gif"
        )
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
            image=cls.uploaded,
        )
        cls.user = User.objects.create_user(username="HasNoName")

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.author)
        cache.clear()

    def test_pages_uses_correct_template(self):
        """Проверка, что view-функция использвует правельные html шаблоны."""
        templates_pages_names = {
            reverse("posts:index"): "posts/index.html",
            reverse(
                "posts:group_list", kwargs={"slug": "test_slug"}
            ): "posts/group_list.html",
            reverse(
                "posts:profile", kwargs={"username": "Автор поста"}
            ): "posts/profile.html",
            reverse(
                "posts:post_detail",
                kwargs={"post_id": f"{(PostPagesTests.post.pk)}"},
            ): "posts/post_detail.html",
            reverse("posts:post_create"): "posts/create_or_edit.html",
            reverse(
                "posts:post_edit",
                kwargs={"post_id": f"{PostPagesTests.post.pk}"},
            ): "posts/create_or_edit.html",
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client_author.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_detail_show_correct_context(self):
        """Проверка, что post_detail сформирован с правильным контекстом."""
        response = self.authorized_client_author.get(
            reverse(
                "posts:post_detail",
                kwargs={"post_id": f"{PostPagesTests.post.pk}"},
            )
        )
        self.assertEqual(response.context.get("post").text, "Тестовый текст")
        self.assertEqual(
            response.context.get("post").group.title, "Тестовый заголовок"
        )

    def test_post_create_show_correct_context(self):
        """Проверка, что post_create сформирован с правильным контекстом."""
        response = self.authorized_client_author.get(
            reverse("posts:post_create")
        )
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get("form").fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context(self):
        """Проверка, что post_edit сформирован с правильным контекстом."""
        response = self.authorized_client_author.get(
            reverse(
                "posts:post_edit",
                kwargs={"post_id": f"{PostPagesTests.post.pk}"},
            )
        )
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get("form").fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_show_correct_context(self):
        """Проверка, что post сформирован с правильным контекстом."""
        response = self.authorized_client_author.get(reverse("posts:index"))
        first_object = response.context["page_obj"][first_post_on_page]
        post_author_0 = first_object.author.username
        post_text_0 = first_object.text
        post_group_0 = first_object.group.title
        post_image_0 = first_object.image
        self.assertEqual(post_author_0, "Автор поста")
        self.assertEqual(post_text_0, "Тестовый текст")
        self.assertEqual(post_group_0, "Тестовый заголовок")
        self.assertEqual(post_image_0, self.post.image)

    def test_group_list_show_correct_context(self):
        """Проверка, что group_list сформирован с правильным контекстом."""
        response = self.authorized_client_author.get(
            reverse("posts:group_list", kwargs={"slug": "test_slug"})
        )
        first_object = response.context["page_obj"][first_post_on_page]
        post_author_0 = first_object.author.username
        post_text_0 = first_object.text
        post_group_0 = first_object.group.title
        post_image_0 = first_object.image
        self.assertEqual(post_author_0, "Автор поста")
        self.assertEqual(post_text_0, "Тестовый текст")
        self.assertEqual(post_group_0, "Тестовый заголовок")
        self.assertEqual(post_image_0, self.post.image)

    def test_profile_show_correct_context(self):
        """Проверка, что profile сформирован с правильным контекстом."""
        response = self.authorized_client_author.get(
            reverse("posts:profile", kwargs={"username": "Автор поста"})
        )
        first_object = response.context["page_obj"][first_post_on_page]
        post_author_0 = first_object.author.username
        post_text_0 = first_object.text
        post_group_0 = first_object.group.title
        post_image_0 = first_object.image
        self.assertEqual(post_author_0, "Автор поста")
        self.assertEqual(post_text_0, "Тестовый текст")
        self.assertEqual(post_group_0, "Тестовый заголовок")
        self.assertEqual(post_image_0, self.post.image)

    def test_post_detail_show_correct_context(self):
        """Проверка, что post_detail сформирован с правильным контекстом."""
        object = Post.objects.get(id=PostPagesTests.post.pk)
        post_author_0 = object.author.username
        post_text_0 = object.text
        post_group_0 = object.group.title
        post_image_0 = object.image
        self.assertEqual(post_author_0, "Автор поста")
        self.assertEqual(post_text_0, "Тестовый текст")
        self.assertEqual(post_group_0, "Тестовый заголовок")
        self.assertEqual(post_image_0, self.post.image)

    def test_cache_index(self):
        """Проверка хранения и очищения кэша для index."""
        response = self.authorized_client_author.get(reverse("posts:index"))
        posts = response.content
        Post.objects.create(
            text="Тестовый текст",
            author=self.author,
        )
        response_old = self.authorized_client_author.get(
            reverse("posts:index")
        )
        old_posts = response_old.content
        self.assertEqual(old_posts, posts)
        cache.clear()
        response_new = self.authorized_client_author.get(
            reverse("posts:index")
        )
        new_posts = response_new.content
        self.assertNotEqual(old_posts, new_posts)

    def test_follow_page(self):
        """Проверка на подписку и отписку авторизованным пользователем./
        И что новый пост не появился у того, кто на него не подписан."""
        response = self.authorized_client.get(reverse("posts:follow_index"))
        self.assertEqual(len(response.context["page_obj"]), 0)
        Follow.objects.get_or_create(user=self.user, author=self.post.author)
        response = self.authorized_client.get(reverse("posts:follow_index"))
        self.assertEqual(len(response.context["page_obj"]), 1)
        self.assertIn(self.post, response.context["page_obj"])

        guest_2 = User.objects.create(username="NoName")
        self.authorized_client.force_login(guest_2)
        response = self.authorized_client.get(reverse("posts:follow_index"))
        self.assertNotIn(self.post, response.context["page_obj"])

        Follow.objects.all().delete()
        response = self.authorized_client.get(reverse("posts:follow_index"))
        self.assertEqual(len(response.context["page_obj"]), 0)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username="Автор поста 1")
        cls.group = Group.objects.create(
            title="Тестовый заголовок",
            description="Тестовое описание",
            slug="test_slug",
        )
        cls.user = User.objects.create_user(username="HasNoName")

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        list_of_posts = [
            (
                Post(
                    text=f"Тестовый текст {i}",
                    group=self.group,
                    author=self.user,
                )
            )
            for i in range(AMOUNT_OF_POSTS)
        ]
        Post.objects.bulk_create(list_of_posts)

    def test_paginator_on_first_page(self):
        """Проверка: количество постов на первой странице равно 10."""
        url_pages = [
            reverse("posts:index"),
            reverse("posts:group_list", kwargs={"slug": self.group.slug}),
            reverse("posts:profile", kwargs={"username": self.user.username}),
        ]
        for key_posts in url_pages:
            with self.subTest(key_posts=key_posts):
                self.assertEqual(
                    len(
                        self.authorized_client.get(key_posts).context.get(
                            "page_obj"
                        )
                    ),
                    POSTS_ON_PAGE,
                )
                self.assertEqual(
                    len(
                        self.authorized_client.get(
                            key_posts + "?page=2"
                        ).context.get("page_obj")
                    ),
                    (AMOUNT_OF_POSTS - POSTS_ON_PAGE),
                )

    def test_paginator_on_second_page(self):
        """Проверка: количество постов на второй странице равно 3."""
        url_pages = [
            reverse("posts:index"),
            reverse("posts:group_list", kwargs={"slug": self.group.slug}),
            reverse("posts:profile", kwargs={"username": self.user.username}),
        ]
        for key_posts in url_pages:
            with self.subTest(key_posts=key_posts):
                self.assertEqual(
                    len(
                        self.authorized_client.get(
                            key_posts + "?page=2"
                        ).context.get("page_obj")
                    ),
                    (AMOUNT_OF_POSTS - POSTS_ON_PAGE),
                )
