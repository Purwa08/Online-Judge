from django.urls import path
from . import views

urlpatterns = [
    path('problems/', views.problem_list, name='problem_list'),
    path('problems/<int:problem_id>/', views.problem_detail, name='problem_detail'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    #path('problems/<int:problem_id>/submit/', views.submit_code, name='submit_code'),
    path('all_submissions/', views.allSubmissionPage, name='all_submissions'),
    path('register/', views.register, name='register'),
    path('login/', views.loginpage, name='login'),
    path('logout/', views.logoutPage, name='logout'),
    #path('problems/', views.problem_list, name='problem_list'),
    # Add more URL patterns as needed
]