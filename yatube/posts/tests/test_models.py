from posts.models import Group, Post

from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()
TEXT_LENGTH = 15


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="Тестовый слаг",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Текстовый пост, который содержит более 15 символов",
            group=cls.group,
        )

    def test_models_have_correct_object_names(self):
        """Тест на корректное отображение поля __str__."""
        group_test = PostModelTest.group
        expected_group = group_test.title
        self.assertEqual(expected_group, str(group_test))
        post_test = PostModelTest.post
        expected_post = post_test.text[:TEXT_LENGTH]
        self.assertEqual(expected_post, str(post_test))

    def test_verbose(self):
        """verbose_name в полях совпадает с ожидаемым."""
        task = PostModelTest.post
        field_verboses = {
            "author": "Автор",
            "group": "Группа",
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    task._meta.get_field(field).verbose_name, expected_value
                )

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        task = PostModelTest.post
        field_help_texts = {
            "text": "Введите текст поста",
            "group": "Выберите группу поста",
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    task._meta.get_field(field).help_text, expected_value
                )
