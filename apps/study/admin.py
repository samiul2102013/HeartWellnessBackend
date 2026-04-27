from django.contrib import admin
from .models import StudyTopic, StudyMaterial, Quiz, Question, QuizAttempt


@admin.register(StudyTopic)
class StudyTopicAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'created_at']
    list_editable = ['is_active']


@admin.register(StudyMaterial)
class StudyMaterialAdmin(admin.ModelAdmin):
    list_display = ['title', 'topic', 'material_type', 'is_active', 'created_at']
    list_filter = ['material_type', 'topic', 'is_active']
    search_fields = ['title']


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'topic', 'is_active', 'created_at']
    inlines = [QuestionInline]


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'quiz', 'score', 'total_questions', 'completed_at']
    list_filter = ['quiz']
    search_fields = ['user__username'] 