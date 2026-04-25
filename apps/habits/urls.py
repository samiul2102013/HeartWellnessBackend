from django.urls import path
from . import views

urlpatterns = [
    # User / Mobile
    path('categories/', views.CategoryListView.as_view()),
    path('habits/', views.HabitListCreateView.as_view()),
    path('habits/<int:pk>/', views.HabitDetailView.as_view()),

    # Admin
    path('admin/categories/', views.AdminCategoryListCreateView.as_view()),
    path('admin/categories/<int:pk>/', views.AdminCategoryDetailView.as_view()),
    path('admin/habits/', views.AdminHabitListView.as_view()),
]