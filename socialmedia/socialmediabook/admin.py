from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import mark_safe
from ckeditor_uploader.widgets import CKEditorUploadingWidget

from .models import (
    User, Post, Comment, Reaction, Survey, Question,
    Choice, Response, Answer, Event, UserProfile
)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_verified', 'date_joined')
    list_filter = ('role', 'is_verified', 'is_active')
    search_fields = ('username', 'email', 'student_id')
    ordering = ('-date_joined',)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('author', 'content', 'created_at', 'is_comments_locked')
    list_filter = ('is_comments_locked', 'created_at')
    search_fields = ('content', 'author__username')
    ordering = ('-created_at',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'content', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'author__username')

@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active', 'start_date', 'end_date')
    search_fields = ('title', 'description')

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('survey', 'question_text', 'question_type', 'required', 'order')
    list_filter = ('question_type', 'required')
    search_fields = ('question_text',)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_date', 'location', 'notification_sent')
    list_filter = ('event_date', 'notification_sent')
    search_fields = ('title', 'description', 'location')
    ordering = ('-event_date',)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'graduation_year', 'company', 'position', 'location')
    search_fields = ('user__username', 'company', 'position')
    list_filter = ('graduation_year',)

# Đăng ký các models còn lại
admin.site.register(Reaction)
admin.site.register(Choice)
admin.site.register(Response)
admin.site.register(Answer)
