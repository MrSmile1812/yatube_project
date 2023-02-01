from posts.forms import CommentForm, PostForm
from posts.models import Follow, Group, Post, User

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

POST_IN_PAGE = 10


def paginate_posts(queryset, page_number):
    paginator = Paginator(queryset, POST_IN_PAGE)
    page_obj = paginator.get_page(page_number)
    return page_obj


@cache_page(20, key_prefix="index_page")
def index(request):
    template = "posts/index.html"
    page_number = request.GET.get("page")
    context = {
        "page_obj": paginate_posts(
            Post.objects.select_related("author", "group").all(), page_number
        )
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = "posts/group_list.html"
    page_number = request.GET.get("page")
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related("author").all()
    context = {
        "group": group,
        "posts": posts,
        "page_obj": paginate_posts(posts, page_number),
    }
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    page_number = request.GET.get("page")
    template = "posts/profile.html"
    post_list = author.posts.select_related("author").all()
    count = post_list.count()
    following = (
        request.user.is_authenticated
        and Follow.objects.filter(user=request.user, author=author).exists()
    )
    context = {
        "author": author,
        "post_list": post_list,
        "count": count,
        "following": following,
        "page_obj": paginate_posts(post_list, page_number),
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = "posts/post_detail.html"
    post = get_object_or_404(Post, pk=post_id)
    is_edit = post.author == request.user
    post_list = post.author.posts.all()
    count = post_list.count()
    form = CommentForm(request.POST or None)
    comments = post.comments.select_related("author").all()
    context = {
        "post": post,
        "count": count,
        "is_edit": is_edit,
        "form": form,
        "comments": comments,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    if not request.method == "POST":
        form = PostForm()
        return render(request, "posts/create_or_edit.html", {"form": form})
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if not form.is_valid():
        return render(request, "posts/create_or_edit.html", {"form": form})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect("posts:profile", username=request.user.username)


@login_required
def post_edit(request, post_id):
    template = "posts/create_or_edit.html"
    post = get_object_or_404(Post, pk=post_id)
    is_edit = True
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    if post.author != request.user:
        return redirect("posts:post_detail", post.id)
    if form.is_valid():
        form.save()
        return redirect("posts:post_detail", post.id)
    context = {
        "form": form,
        "post": post,
        "is_edit": is_edit,
    }
    return render(request, template, context=context)


@login_required
def add_comment(request, post_id):
    template = "posts:post_detail"
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect(template, post_id=post_id)


@login_required
def follow_index(request):
    follower = Follow.objects.filter(user=request.user).values_list(
        "author_id",
        flat=True,
    )
    post = Post.objects.filter(author_id__in=follower).select_related("group")
    page_number = request.GET.get("page")
    context = {
        "posts": post,
        "page_obj": paginate_posts(post, page_number),
    }
    return render(request, "posts/follow.html", context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    if user != author:
        Follow.objects.get_or_create(user=user, author=author)
    return redirect("posts:profile", username=author)


@login_required
def profile_unfollow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=user, author=author).delete()
    return redirect("posts:profile", username=author)


def page_not_found(request, exception):
    return render(request, "core/404.html", {"path": request.path}, status=404)


def permission_denied(request):
    return render(request, "core/403.html", status=403)
