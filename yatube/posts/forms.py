from posts.models import Comment, Post

from django import forms


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("group", "text", "image")

        labels = {"text": "Текст", "group": "Группа"}

        help_texts = {
            "text": "Текст нового поста",
            "group": "Группа, к которой будет относиться пост",
        }

        widgets = {
            "group": forms.Select(attrs={"class": "form-control"}),
            "text": forms.Textarea(attrs={"class": "form-control"}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("text",)
        labels = {"text": "Текст комментария"}
        help_texts = {"text": "Текст нового комментария"}
