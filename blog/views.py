from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import (TemplateView, ListView, DetailView, CreateView,
                                  UpdateView, DeleteView)
from django.utils import timezone
from blog.models import Post, Comment
from blog.forms import PostForm, CommentForm


# Create your views here.

class AboutView(TemplateView):
  template_name = 'about.html'

class PostListView(ListView):
  model = Post

  def get_queryset(self):
    return Post.objects.filter(published_date__lte = timezone.now()).order_by('-published_date')

class PostDetailView(DetailView):
  model = Post

class CreatePostView(LoginRequiredMixin, CreateView):
  # This mixin should be at the leftmost position in the inheritance list
  login_url = '/login/'
  redirect_field_name = 'blog/post_detail.html'
  form_class = PostForm
  model = Post

class PostUpdateView(LoginRequiredMixin, UpdateView):
  login_url = '/login/'
  redirect_field_name = 'blog/post_detail.html'
  form_class = PostForm
  model = Post

class PostDeleteView(LoginRequiredMixin, DeleteView):
  model = Post
  success_url = reverse_lazy('post_list')

class DraftListView(LoginRequiredMixin, ListView):
  login_url = '/login/'
  redirect_field_name = 'blog/post_list.html'
  model = Post

  def get_queryset(self):
    return Post.objects.filter(published_date__isnull=True).order_by('created_date')



#########################################################################################
#########################################################################################
@login_required
def post_publish(req, pk):
  post = get_object_or_404(Post, pk=pk)
  post.pulbish()
  return redirect('post_detail', pk=pk)



# @login_required
def add_comment_to_post(req,pk):
  post = get_object_or_404(Post, pk=pk)
  print(f'POST: {post}')
  if req.method == 'POST':
    form = CommentForm(req.POST)
    if form.is_valid():
      print(f'FORM IS VALID')
      comment = form.save(commit=False)
      comment.post = post
      comment.save()
      print(f'COMMENT: {comment}')
      return redirect('post_detail', pk=post.pk)
  else:
    print('FORM FOR COMMENT')
    form = CommentForm()
  return render(req, 'blog/comment_form.html', {'form':form})

@login_required
def comment_approve(req, pk):
  comment = get_object_or_404(Comment, pk=pk)
  comment.approve()
  return redirect('post_detail', pk=comment.post.pk)

@login_required
def comment_remove(req, pk):
  comment = get_object_or_404(Comment, pk=pk)
  post_pk = comment.post.pk
  comment.delete() #https://docs.djangoproject.com/en/4.0/topics/db/queries/#topics-db-queries-delete
  return redirect('post_detail', pk=post_pk)
