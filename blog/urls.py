from django.urls import path, re_path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.BlogListView.as_view(), name='list'),
    # Unicode slug support for Turkish characters
    re_path(r'^(?P<slug>[\w-]+)/$', views.blog_detail, name='detail'),
]
