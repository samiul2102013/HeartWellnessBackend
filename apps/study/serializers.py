from rest_framework import serializers
from .models import (
    StudyTopic, StudyMaterial, UserMaterialProgress,
    Quiz, Question, QuizAttempt, QuizAnswer
)


# ── Study Material Serializers ────────────────────────────────

class StudyMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyMaterial
        fields = [
            'id', 'topic', 'title', 'description',
            'material_type', 'file', 'video_url', 'content',
            'is_active', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class StudyMaterialListSerializer(serializers.ModelSerializer):
    """Lightweight — for list views, excludes heavy content field."""
    is_completed = serializers.SerializerMethodField()

    class Meta:
        model = StudyMaterial
        fields = [
            'id', 'title', 'description', 'material_type',
            'file', 'video_url', 'is_completed', 'created_at',
        ]

    def get_is_completed(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return UserMaterialProgress.objects.filter(
            user=request.user, material=obj, is_completed=True
        ).exists()


class StudyTopicSerializer(serializers.ModelSerializer):
    materials = StudyMaterialListSerializer(many=True, read_only=True)
    material_count = serializers.IntegerField(read_only=True)
    completed_count = serializers.SerializerMethodField()

    class Meta:
        model = StudyTopic
        fields = [
            'id', 'title', 'description', 'thumbnail',
            'material_count', 'completed_count', 'materials', 'created_at',
        ]

    def get_completed_count(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return 0
        return UserMaterialProgress.objects.filter(
            user=request.user,
            material__topic=obj,
            is_completed=True
        ).count()


class StudyTopicListSerializer(serializers.ModelSerializer):
    """Lightweight — no nested materials, just counts."""
    material_count = serializers.IntegerField(read_only=True)
    completed_count = serializers.SerializerMethodField()

    class Meta:
        model = StudyTopic
        fields = [
            'id', 'title', 'description', 'thumbnail',
            'material_count', 'completed_count', 'created_at',
        ]

    def get_completed_count(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return 0
        return UserMaterialProgress.objects.filter(
            user=request.user,
            material__topic=obj,
            is_completed=True
        ).count()


class MarkMaterialCompleteSerializer(serializers.Serializer):
    material_id = serializers.IntegerField()


# ── Quiz Serializers ──────────────────────────────────────────

class QuestionSerializer(serializers.ModelSerializer):
    """For users taking the quiz — hides correct_option."""
    class Meta:
        model = Question
        fields = ['id', 'text', 'option_a', 'option_b', 'option_c', 'option_d', 'order']


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    question_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Quiz
        fields = [
            'id', 'topic', 'title', 'description',
            'question_count', 'questions', 'created_at',
        ]


class QuizListSerializer(serializers.ModelSerializer):
    question_count = serializers.IntegerField(read_only=True)
    last_score = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'question_count', 'last_score', 'created_at']

    def get_last_score(self, obj):
        request = self.context.get('request')
        if not request:
            return None
        attempt = QuizAttempt.objects.filter(
            user=request.user, quiz=obj
        ).order_by('-completed_at').first()
        if attempt:
            return {
                'score': attempt.score,
                'total': attempt.total_questions,
                'percentage': attempt.score_percentage,
            }
        return None


class QuizAnswerSubmitSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    selected_option = serializers.ChoiceField(choices=['A', 'B', 'C', 'D'])


class QuizSubmitSerializer(serializers.Serializer):
    """User submits all answers at once."""
    quiz_id = serializers.IntegerField()
    answers = QuizAnswerSubmitSerializer(many=True)

    def validate_answers(self, value):
        if len(value) == 0:
            raise serializers.ValidationError("At least one answer is required.")
        return value


class QuizAttemptSerializer(serializers.ModelSerializer):
    score_percentage = serializers.FloatField(read_only=True)
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)

    class Meta:
        model = QuizAttempt
        fields = [
            'id', 'quiz', 'quiz_title', 'score',
            'total_questions', 'score_percentage', 'completed_at',
        ]


class QuizAttemptDetailSerializer(serializers.ModelSerializer):
    """Full attempt with per-answer results."""
    score_percentage = serializers.FloatField(read_only=True)
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)
    answers = serializers.SerializerMethodField()

    class Meta:
        model = QuizAttempt
        fields = [
            'id', 'quiz', 'quiz_title', 'score',
            'total_questions', 'score_percentage', 'completed_at', 'answers',
        ]

    def get_answers(self, obj):
        return [
            {
                'question_id': a.question.id,
                'question_text': a.question.text,
                'selected_option': a.selected_option,
                'correct_option': a.question.correct_option,
                'is_correct': a.is_correct,
            }
            for a in obj.answers.select_related('question').all()
        ]


# ── Admin Serializers ─────────────────────────────────────────

class AdminStudyTopicSerializer(serializers.ModelSerializer):
    material_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = StudyTopic
        fields = ['id', 'title', 'description', 'thumbnail', 'is_active', 'material_count', 'created_at']
        read_only_fields = ['id', 'created_at']


class AdminStudyMaterialSerializer(serializers.ModelSerializer):
    topic_title = serializers.CharField(source='topic.title', read_only=True)

    class Meta:
        model = StudyMaterial
        fields = [
            'id', 'topic', 'topic_title', 'title', 'description',
            'material_type', 'file', 'video_url', 'content',
            'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AdminQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'quiz', 'text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option', 'order']
        read_only_fields = ['id']


class AdminQuizSerializer(serializers.ModelSerializer):
    questions = AdminQuestionSerializer(many=True, read_only=True)
    question_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Quiz
        fields = ['id', 'topic', 'title', 'description', 'is_active', 'question_count', 'questions', 'created_at']
        read_only_fields = ['id', 'created_at']


class AdminQuizAttemptSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)
    score_percentage = serializers.FloatField(read_only=True)

    class Meta:
        model = QuizAttempt
        fields = [
            'id', 'user', 'user_username', 'quiz', 'quiz_title',
            'score', 'total_questions', 'score_percentage', 'completed_at',
        ]