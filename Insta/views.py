from django.shortcuts import render
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse, reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from Insta.forms import *
from Insta.models import *
from annoying.decorators import ajax_request
from django.http import HttpResponseRedirect

# Create your views here.
class PostListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'home.html'
    login_url = 'login'
    '''
    # overwrite the get_queryset to only return posts created by users followed by current user.
    def get_queryset(self):
        current_user = self.request.user
        following = set()
        for conn in UserConnection.objects.filter(creator=current_user).select_related('following'):
        # select_related menas only fetch column 'following'
        # for conn in current_user.get_connections().select_related('following'):
            following.add(conn.following)
        return Post.objects.filter(author__in=following)
    '''


class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post
    template_name = 'post_detail.html'
    login_url = 'login'
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        liked = Like.objects.filter(post=self.kwargs.get('pk'), user=self.request.user).first()
        if liked:
            data['liked'] = 1
        else:
            data['liked'] = 0
        return data


class ExploreView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'explore.html'
    login_url = 'login'

    def get_queryset(self):
        return Post.objects.all().order_by('created')[:20]


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'post_create.html'
    fields = ['title', 'image']
    login_url = 'login'
    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.author = self.request.user
        obj.save()
        return HttpResponseRedirect(reverse_lazy("home"))


class PostUpdateView(UpdateView):
    model = Post
    template_name = 'post_update.html'
    fields = ['title']


class PostDeleteView(DeleteView):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy("home")

'''
reverse vs reverse_lazy
Reverse_lazy is, as the name implies, a lazy implementation of the reverse URL resolver.
Unlike the traditional reverse function, reverse_lazy won't execute until the value is needed.
It is useful because it prevent 'Reverse Not Found' exceptions when working with URLs that may not be immediately known.
Examples of reverse_lazy usage:
You want to provide a reversed URL as the url attribute of a Generic Class Based View (the same as we did in our example).
You want to provide a URL as a default value for a parameter in functions signature.
You want to provide a URL to a decorator like @login_required(login_url) decorator.
'''

class SignUpView(CreateView):
    template_name = 'signup.html'
    success_url = reverse_lazy('login')
    form_class = CustomUserCreationForm


class SignUp(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'

class UserProfile(LoginRequiredMixin, DetailView):
    model = InstaUser
    template_name = 'profile_detail.html'
    login_url = 'login'

class EditProfile(LoginRequiredMixin, UpdateView):
    model = InstaUser
    template_name = 'profile_update.html'
    fields = ['profile_pic', 'username']
    login_url = 'login'

'''
Why use function view over class view?
'''
@ajax_request
def toggleFollow(request):
    current_user = InstaUser.objects.get(pk=request.user.pk)
    follow_user_pk = request.POST.get('follow_user_pk')
    follow_user = InstaUser.objects.get(pk=follow_user_pk)

    try:
        if current_user != follow_user:
            if request.POST.get('type') == 'follow':
                connection = UserConnection(creator=current_user, following=follow_user) # Create new connection, both creator and following must be an object
                connection.save()
            elif request.POST.get('type') == 'unfollow':
                UserConnection.objects.filter(creator=current_user, following=follow_user).delete()
            result = 1
        else:
            result = 0
    except Exception as e:
        print(e)
        result = 0

    return {
        'result': result,
        'type': request.POST.get('type'),
        'follow_user_pk': follow_user_pk
    }


@ajax_request
def addLike(request):
    # current_user = InstaUser.objects.get(pk=request.user.pk)
    post_pk = request.POST.get('post_pk')
    post = Post.objects.get(pk=post_pk)
    try:
        like = Like(post=post, user=request.user)
        # like = Like(post=post, user=current_user)
        like.save()
        result = 1
    except Exception as e:
        like = Like.objects.get(post=post, user=request.user)
        # like = Like.objects.get(post=post, user=current_user)
        like.delete()
        result = 0

    return {
        'result': result,
        'post_pk': post_pk
    }


@ajax_request
def addComment(request):
    comment_text = request.POST.get('comment_text')
    post_pk = request.POST.get('post_pk')
    post = Post.objects.get(pk=post_pk)
    commenter_info = {}

    try:
        comment = Comment(comment=comment_text, user=request.user, post=post)
        comment.save()

        username = request.user.username

        commenter_info = {
            'username': username,
            'comment_text': comment_text
        }

        result = 1
    except Exception as e:
        print(e)
        result = 0

    return {
        'result': result,
        'post_pk': post_pk,
        'commenter_info': commenter_info
    }