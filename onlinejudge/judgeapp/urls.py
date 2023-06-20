from django.urls import path

from . import views
from .views import problem_list, problem_detail, success, leaderboard


urlpatterns = [
    path('problems/', problem_list, name='problem_list'),
    path('problems/<int:problem_id>/', problem_detail, name='problem_detail'),
    path('success/', success, name='success'),
    path('leaderboard/', leaderboard, name='leaderboard'),
    #path('register/', views.register, name='register'),
    #path('problems/', views.problem_list, name='problem_list'),
    # Add more URL patterns as needed
]