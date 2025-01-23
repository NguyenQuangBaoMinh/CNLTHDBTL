
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from ckeditor.fields import RichTextField


class User(AbstractUser):
    ROLES = (
        ('ADMIN', 'Administrator'),
        ('FACULTY', 'Faculty'),
        ('ALUMNI', 'Alumni')
    )

    role = models.CharField(max_length=10, choices=ROLES)
    avatar = models.ImageField(upload_to='avatars/', null=True)
    cover_photo = models.ImageField(upload_to='covers/', null=True)
    student_id = models.CharField(max_length=20, null=True)
    is_verified = models.BooleanField(default=False)
    password_change_required = models.BooleanField(default=False)
    password_change_deadline = models.DateTimeField(null=True)



    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def set_password_change_deadline(self):
        self.password_change_required = True
        self.password_change_deadline = timezone.now() + timezone.timedelta(hours=24)
        self.save()

    def check_password_change_deadline(self):
        if self.password_change_required and timezone.now() > self.password_change_deadline:
            self.is_active = False
            self.save()
            return False
        return True


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = RichTextField(null=True)
    graduation_year = models.IntegerField(null=True)
    company = models.CharField(max_length=100, null=True)
    position = models.CharField(max_length=100, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    location = models.CharField(max_length=100, blank=True)
    profileimg = models.ImageField(upload_to='UserProfiles/%Y/%m', default='blank=profile')

    def __str__(self):
        return self.user.username


class Post(models.Model):
    REACTION_CHOICES = (
        ('LIKE', 'Like'),
        ('HEART', 'Heart'),
        ('HAHA', 'Haha')
    )

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = RichTextField()
    image = models.ImageField(upload_to='Posts/%Y/%m', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_comments_locked = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = RichTextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'


class Reaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reactions')
    reaction_type = models.CharField(max_length=5, choices=Post.REACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'post']
        verbose_name = 'Reaction'
        verbose_name_plural = 'Reactions'


class Survey(models.Model):
    title = models.CharField(max_length=200)
    description = RichTextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Survey'
        verbose_name_plural = 'Surveys'


class Question(models.Model):
    QUESTION_TYPES = (
        ('TEXT', 'Text Answer'),
        ('CHOICE', 'Multiple Choice'),
        ('SCALE', 'Rating Scale')
    )

    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPES)
    required = models.BooleanField(default=True)
    order = models.IntegerField()

    class Meta:
        ordering = ['order']
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    choice_text = models.CharField(max_length=200)
    order = models.IntegerField()

    class Meta:
        ordering = ['order']
        verbose_name = 'Choice'
        verbose_name_plural = 'Choices'


class Response(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='responses')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Response'
        verbose_name_plural = 'Responses'


class Answer(models.Model):
    response = models.ForeignKey(Response, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.TextField(null=True, blank=True)
    selected_choice = models.ForeignKey(Choice, on_delete=models.CASCADE, null=True, blank=True)
    rating_value = models.IntegerField(null=True, blank=True)

    class Meta:
        verbose_name = 'Answer'
        verbose_name_plural = 'Answers'


class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    event_date = models.DateTimeField()
    location = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    notification_sent = models.BooleanField(default=False)

    class Meta:
        ordering = ['-event_date']
        verbose_name = 'Event'
        verbose_name_plural = 'Events'