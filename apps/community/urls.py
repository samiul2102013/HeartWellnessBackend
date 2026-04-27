from django.urls import path
from . import views

urlpatterns = [
    # Community group (REST — history load)
    path('community/messages/', views.CommunityMessageHistoryView.as_view()),

    # Direct messages
    path('community/users/', views.UserListForDMView.as_view()),
    path('community/dm/<int:user_id>/', views.DMHistoryView.as_view()),
    path('community/conversations/', views.MyConversationsView.as_view()),

    # Admin
    path('admin/community/messages/', views.AdminCommunityMessageListView.as_view()),
    path('admin/community/messages/<int:pk>/', views.AdminCommunityMessageDeleteView.as_view()),
]