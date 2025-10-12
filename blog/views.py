from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.views.generic import ListView
from .models import BlogPost


class BlogListView(ListView):
    """Blog yazıları listesi"""
    model = BlogPost
    template_name = 'blog/blog_list.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        return BlogPost.objects.filter(is_published=True).order_by('-created_at')


def blog_detail(request, slug):
    """Blog yazısı detay sayfası"""
    # Test slug receiving
    return HttpResponse(f"<h1>Blog Detail</h1><p>Received slug: {slug}</p>")
