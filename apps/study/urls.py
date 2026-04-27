from django.urls import path
from . import views

urlpatterns = [
    # ── User / Mobile ─────────────────────────────────────────

    # Study Topics
    path('study/topics/', views.StudyTopicListView.as_view()),
    path('study/topics/<int:pk>/', views.StudyTopicDetailView.as_view()),

    # Study Materials
    path('study/materials/<int:pk>/', views.StudyMaterialDetailView.as_view()),
    path('study/materials/complete/', views.MarkMaterialCompleteView.as_view()),

    # Quiz
    path('study/quizzes/', views.QuizListView.as_view()),
    path('study/quizzes/<int:pk>/', views.QuizDetailView.as_view()),
    path('study/quizzes/submit/', views.QuizSubmitView.as_view()),

    # Attempts / History
    path('study/attempts/', views.MyQuizAttemptsView.as_view()),
    path('study/attempts/<int:pk>/', views.QuizAttemptDetailView.as_view()),

    # Progress (profile page)
    path('study/progress/', views.StudyProgressView.as_view()),

    # ── Admin ─────────────────────────────────────────────────

    # Topics
    path('admin/study/topics/', views.AdminStudyTopicListCreateView.as_view()),
    path('admin/study/topics/<int:pk>/', views.AdminStudyTopicDetailView.as_view()),

    # Materials
    path('admin/study/materials/', views.AdminStudyMaterialListCreateView.as_view()),
    path('admin/study/materials/<int:pk>/', views.AdminStudyMaterialDetailView.as_view()),

    # Quizzes
    path('admin/study/quizzes/', views.AdminQuizListCreateView.as_view()),
    path('admin/study/quizzes/<int:pk>/', views.AdminQuizDetailView.as_view()),

    # Questions
    path('admin/study/questions/', views.AdminQuestionListCreateView.as_view()),
    path('admin/study/questions/<int:pk>/', views.AdminQuestionDetailView.as_view()),

    # Quiz Results
    path('admin/study/attempts/', views.AdminQuizAttemptListView.as_view()),
]