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
    """Blog yazısı detay sayfası - SEO optimize"""
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)

    # Görüntülenme sayısını artır
    post.view_count += 1
    post.save(update_fields=['view_count'])

    context = {
        'post': post,
        'title': post.title,
        'description': post.meta_description or post.content[:155],
        'keywords': post.meta_keywords,
        'canonical': f'/blog/{post.slug}/',
    }

    return render(request, 'blog/blog_detail.html', context)
