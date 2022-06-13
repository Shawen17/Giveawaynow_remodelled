"""Giveaway URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from  django.conf import settings
from django.conf.urls.static import static
from blog import views
from django.conf.urls import url
from django.views.static import serve

app_name='blog'

urlpatterns = [
    path('',views.all_blogs, name='all_blogs'),
    path('test/',views.test,name='test'),
    path('<int:blog_id>/view',views.detail, name='detail'),
    path('<int:blog_id>/',views.post_comment,name='post_comment'),
    path('all',views.list_blog,name='list_blog'),
    path ('category/<str:category>',views.category,name='category'),
]
