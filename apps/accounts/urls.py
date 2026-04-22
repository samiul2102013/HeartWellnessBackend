from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # Auth
    path('auth/register/', views.RegisterView.as_view()),
    path('auth/login/', views.LoginView.as_view()),
    path('auth/token/refresh/', TokenRefreshView.as_view()),

    # User
    path('users/profile/', views.ProfileView.as_view()),
    path('users/change-password/', views.ChangePasswordView.as_view()),

    # Admin
    path('admin/users/', views.AdminUserListView.as_view()),
    path('admin/users/<int:pk>/', views.AdminUserDetailView.as_view()),
]