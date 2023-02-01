from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CreationForm


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy("posts:index")
    template_name = "users/signup.html"


@login_required
class PasswordChange(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy("posts:password_change_done.html")
    template_name = "users/password_change_form.html"


class PasswordReset(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy("posts:password_reset_done.html")
    template_name = "users/password_reset_form.html"


class PasswordResetConfirm(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy("posts:password_reset_complete.html")
    template_name = "users/password_reset_confirm.html"
