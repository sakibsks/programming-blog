from django.shortcuts import render,get_object_or_404,redirect
from django.urls import reverse
from django.http import HttpResponseRedirect,HttpResponse
from django.utils import timezone
from blog.models import Post, Comment
from blog.forms import PostForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (TemplateView,
                                  ListView,DetailView,
                                  CreateView,UpdateView,
                                  DeleteView)
from django.urls import reverse_lazy
# Create your views here.

class AboutView(TemplateView):
    template_name = "about.html"

class PostListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'

    def get_queryset(self):
        return Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')

class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'

class CreatePostView(LoginRequiredMixin,CreateView):
    login_url = "/login/"
    redirect_field_name = "blog/post_detail.html"
    form_class = PostForm
    model = Post
    template_name = 'blog/post_form.html'

class PostUpdateView(LoginRequiredMixin,UpdateView):
    login_url = "/login/"
    redirect_field_name = "blog/post_detail.html"
    form_class = PostForm
    model = Post
    template_name = 'blog/post_form.html'

class PostDeleteView(LoginRequiredMixin,DeleteView):
    model = Post
    template_name = 'blog/post_confirm_delete.html'
    success_url = reverse_lazy("blog:post_list")

class DraftListView(LoginRequiredMixin,ListView):
    login_url = "/login/"
    redirect_field_name = "blog/post_list.html"
    template_name = 'blog/post_draft_list.html'
    context_object_name = "draft_list"
    form_class = PostForm
    model = Post

    def get_queryset(self):
        return Post.objects.filter(published_date__isnull=True).order_by('create_date')


###########################################
###########################################

@login_required
def post_publish(request,pk):
    post = get_object_or_404(Post,pk=pk)
    post.publish()
    return redirect("blog:post_detail",pk=pk)

def add_comment_to_post(request,pk):
    post = get_object_or_404(Post,pk=pk)
    if request.method=="POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            return redirect('blog:post_detail',pk=post.pk)
    else:
        form = CommentForm()
    return render(request,"blog/comment_form.html",{'form':form})

@login_required
def comment_approve(request,pk):
    comment = get_object_or_404(Comment,pk=pk)
    comment.approve()
    return redirect("blog:post_detail",pk=comment.post.pk)

@login_required
def comment_remove(request,pk):
    comment = get_object_or_404(Comment,pk=pk)
    post_pk = comment.post.pk
    comment.delete()
    return redirect("blog:post_detail",pk=post_pk)
