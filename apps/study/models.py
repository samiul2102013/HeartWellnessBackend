from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class StudyTopic(models.Model):
    """Admin-managed topics that group materials and quizzes."""
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    thumbnail = models.ImageField(upload_to='study/thumbnails/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'study_topics'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

   
class StudyMaterial(models.Model):
    class MaterialType(models.TextChoices):
        PDF = 'pdf', 'PDF'
        TEXT = 'text', 'Text'
        VIDEO = 'video', 'Video Link'

    topic = models.ForeignKey(
        StudyTopic, on_delete=models.CASCADE, related_name='materials'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    material_type = models.CharField(
        max_length=10, choices=MaterialType.choices, default=MaterialType.PDF
    )
    file = models.FileField(
        upload_to='study/materials/', null=True, blank=True,
        help_text='Upload PDF or text file'
    )
    video_url = models.URLField(blank=True, default='')
    content = models.TextField(blank=True, default='', help_text='Text content if type is text')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'study_materials'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.topic.title} — {self.title}"


class UserMaterialProgress(models.Model):
    """Tracks which materials a user has read/downloaded."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='material_progress'
    )
    material = models.ForeignKey(
        StudyMaterial, on_delete=models.CASCADE, related_name='user_progress'
    )
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_material_progress'
        unique_together = ['user', 'material']

    def __str__(self):
        return f"{self.user.username} — {self.material.title}"


class Quiz(models.Model):
    topic = models.ForeignKey(
        StudyTopic, on_delete=models.CASCADE, related_name='quizzes'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'quizzes'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Question(models.Model):
    """MCQ question — always 4 options, one correct."""
    quiz = models.ForeignKey(
        Quiz, on_delete=models.CASCADE, related_name='questions'
    )
    text = models.TextField()
    option_a = models.CharField(max_length=300)
    option_b = models.CharField(max_length=300)
    option_c = models.CharField(max_length=300)
    option_d = models.CharField(max_length=300)
    correct_option = models.CharField(
        max_length=1,
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')]
    )
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = 'quiz_questions'
        ordering = ['order']

    def __str__(self):
        return f"{self.quiz.title} — Q{self.order}"


class QuizAttempt(models.Model):
    """A user's completed quiz attempt with score."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='quiz_attempts'
    )
    quiz = models.ForeignKey(
        Quiz, on_delete=models.CASCADE, related_name='attempts'
    )
    score = models.PositiveSmallIntegerField(default=0)
    total_questions = models.PositiveSmallIntegerField(default=0)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'quiz_attempts'
        ordering = ['-completed_at']

    @property
    def score_percentage(self):
        if self.total_questions == 0:
            return 0
        return round((self.score / self.total_questions) * 100, 1)

    def __str__(self):
        return f"{self.user.username} — {self.quiz.title} — {self.score}/{self.total_questions}"


class QuizAnswer(models.Model):
    """Individual answer per question in an attempt."""
    attempt = models.ForeignKey(
        QuizAttempt, on_delete=models.CASCADE, related_name='answers'
    )
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name='answers'
    )
    selected_option = models.CharField(
        max_length=1,
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')]
    )
    is_correct = models.BooleanField(default=False)

    class Meta:
        db_table = 'quiz_answers'
        unique_together = ['attempt', 'question']