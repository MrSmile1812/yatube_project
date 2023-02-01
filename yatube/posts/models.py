from django.contrib.auth import get_user_model
from django.core.validators import MaxLengthValidator
from django.db import models

User = get_user_model()
TEXT_LENGTH = 15


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self) -> str:
        return self.title


class Post(models.Model):
    text = models.TextField(
        "Текст поста",
        help_text="Введите текст поста",
        validators=[
            MaxLengthValidator(
                250, "Превышено максимальное " "количество символов"
            )
        ],
    )
    pub_date = models.DateTimeField(
        "Дата публикации",
        auto_now_add=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name="Автор",
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="posts",
        help_text="Выберите группу поста",
        verbose_name="Группа",
    )
    image = models.ImageField("Картинка", upload_to="posts/", blank=True)

    class Meta:
        ordering = ("-pub_date",)
        verbose_name = "Пост"
        verbose_name_plural = "Посты"

    def __str__(self):
        return self.text[:TEXT_LENGTH]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    text = models.TextField(
        "Текст",
        help_text="Введите текст комментария",
    )
    created = models.DateTimeField(
        verbose_name="Дата комментария",
        auto_now_add=True,
    )

    class Meta:
        ordering = ("-created",)
        verbose_name = "Пост"
        verbose_name_plural = "Комментарии"

    def __str__(self):
        return self.text[:TEXT_LENGTH]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="Подписчик",
        related_name="follower",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="Автор",
        related_name="following",
    )

    class Meta:
        unique_together = ("user", "author")
        verbose_name_plural = "Подписки"
