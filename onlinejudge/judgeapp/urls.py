from django.urls import path

from . import views
from .views import problem_list, problem_detail, success, leaderboard


urlpatterns = [
    path('problems/', views.problem_list, name='problem_list'),
    path('problems/<int:problem_id>/', views.problem_detail, name='problem_detail'),
    path('success/', views.success, name='success'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('problems/<int:problem_id>/submit/', views.submit_code, name='submit_code')

    #path('register/', views.register, name='register'),
    #path('problems/', views.problem_list, name='problem_list'),
    # Add more URL patterns as needed
]