from django.contrib import admin
from .models import BlogPost


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'is_published', 'view_count', 'created_at']
    list_filter = ['is_published', 'created_at']
    search_fields = ['title', 'content', 'meta_keywords']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'

    fieldsets = (
        ('İçerik', {
            'fields': ('title', 'slug', 'content', 'featured_image')
        }),
        ('SEO Ayarları', {
            'fields': ('meta_description', 'meta_keywords')
        }),
        ('Yayın Ayarları', {
            'fields': ('is_published', 'published_at')
        }),
        ('İstatistikler', {
            'fields': ('view_count',),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['view_count']
