from django.urls import path
from . import views

urlpatterns = [
    # User / Mobile
    path('moods/', views.MoodListView.as_view()),
    path('checkins/', views.CheckInCreateView.as_view()),
    path('checkins/history/', views.CheckInHistoryView.as_view()),
    path('checkins/<int:pk>/', views.CheckInDetailView.as_view()),
    path('checkins/dashboard/', views.DashboardStatsView.as_view()),

    # Admin
    path('admin/moods/', views.AdminMoodListCreateView.as_view()),
    path('admin/moods/<int:pk>/', views.AdminMoodDetailView.as_view()),
    path('admin/checkins/', views.AdminCheckInListView.as_view()),
    path('admin/checkins/<int:pk>/', views.AdminCheckInDetailView.as_view()),
    path('admin/dashboard/', views.AdminDashboardView.as_view()),
]