from . import views
from django.contrib import admin
from django.urls import path,include
from django.contrib.auth import views as auth_views
from core import views as user_views

from django.conf import settings
from django.conf.urls.static import static




urlpatterns = [

path('', views.login, name='login'),
path('register/', views.register_user, name='register'),
path('logout/', views.logout, name='logout'),
path('feed/',views.feed,name='feed'),
path('follow/<username>/', views.follow, name='follow'),
path('unfollow/<username>/', views.unfollow, name='unfollow'),
path('profile/<username>/', views.profile,name='profile'),
path('post/<username>/', views.post,name='post'),
path('comment/<username>/<post_id>/', views.comment,name = 'comment'),
path('welcome/',views.welcome,name='welcome'),
path('search/', user_views.search, name='search'),

]
