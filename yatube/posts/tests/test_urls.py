from http import HTTPStatus

from posts.models import Group, Post

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase

User = get_user_model()


class TaskURLTests(TestCase):
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
        cls.user = User.objects.create_user(username="HasNoName")

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.author)
        self.users = [
            self.guest_client,
            self.authorized_client,
            self.authorized_client_author,
        ]
        cache.clear()

    def test_urls_uses_correct_template_and_url_for_guest(self):
        """Тест на проверку шаблонов и доступности адресов для \
неавторизованного пользователя."""
        url_names_and_statuscode_guest = {
            "/": ["posts/index.html", HTTPStatus.OK.value],
            "/group/test_slug/": [
                "posts/group_list.html",
                HTTPStatus.OK.value,
            ],
            f"/profile/{self.post.author}/": [
                "posts/profile.html",
                HTTPStatus.OK.value,
            ],
            f'/posts/{f"{TaskURLTests.post.pk}"}/': [
                "posts/post_detail.html",
                HTTPStatus.OK.value,
            ],
        }
        first_element_in_dict = 0
        for (
            address,
            template_and_statuscode,
        ) in url_names_and_statuscode_guest.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(
                    response, template_and_statuscode[first_element_in_dict]
                )
                self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_urls_uses_correct_template_and_url_for_authorized(self):
        """Тест на проверку шаблонов и доступности адресов для \
авторизованного пользователя."""
        url_names_and_statuscode_authorized = {
            "/": ["posts/index.html", HTTPStatus.OK.value],
            "/group/test_slug/": [
                "posts/group_list.html",
                HTTPStatus.OK.value,
            ],
            f"/profile/{self.post.author}/": [
                "posts/profile.html",
                HTTPStatus.OK.value,
            ],
            f'/posts/{f"{TaskURLTests.post.pk}"}/': [
                "posts/post_detail.html",
                HTTPStatus.OK.value,
            ],
            "/create/": ["posts/create_or_edit.html", HTTPStatus.OK.value],
        }
        first_element_in_dict = 0
        for (
            address,
            template_and_statuscode,
        ) in url_names_and_statuscode_authorized.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(
                    response, template_and_statuscode[first_element_in_dict]
                )
                self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_urls_uses_correct_template_and_url_for_author(self):
        """Тест на проверку шаблонов и доступности адресов для \
автора постов."""
        url_names_and_statuscode_author = {
            "/": ["posts/index.html", HTTPStatus.OK.value],
            "/group/test_slug/": [
                "posts/group_list.html",
                HTTPStatus.OK.value,
            ],
            f"/profile/{self.post.author}/": [
                "posts/profile.html",
                HTTPStatus.OK.value,
            ],
            f'/posts/{f"{TaskURLTests.post.pk}"}/': [
                "posts/post_detail.html",
                HTTPStatus.OK.value,
            ],
            "/create/": ["posts/create_or_edit.html", HTTPStatus.OK.value],
            f'/posts/{f"{TaskURLTests.post.pk}"}/edit/': [
                "posts/create_or_edit.html",
                HTTPStatus.OK.value,
            ],
        }
        first_element_in_dict = 0
        for (
            address,
            template_and_statuscode,
        ) in url_names_and_statuscode_author.items():
            with self.subTest(address=address):
                response = self.authorized_client_author.get(address)
                self.assertTemplateUsed(
                    response, template_and_statuscode[first_element_in_dict]
                )
                self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_wrong_adress_url(self):
        """Проверка на запрос к несуществующей странице \
и страница 404 отдает кастомный шаблон."""
        for user in self.users:
            response = user.get("/unexisting_page/")
            self.assertEqual(response.status_code, 404)
            self.assertTemplateUsed(response, "core/404.html")

    def test_guest_redirect(self):
        """Проверка на перенаправление неавторизованного
        пользователя при поптыке создания поста."""
        response = self.guest_client.get("/create/", follow=True)
        self.assertRedirects(response, "/auth/login/?next=/create/")
