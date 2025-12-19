from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    avatar_url = models.URLField(blank=True, null=True)
    total_activities = models.PositiveIntegerField(default=0)
    total_duration_minutes = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} profile"


class Team(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    members = models.ManyToManyField(UserProfile, related_name='teams', blank=True)
    leader = models.ForeignKey(UserProfile, null=True, blank=True, on_delete=models.SET_NULL, related_name='led_teams')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Activity(models.Model):
    ACTIVITY_CHOICES = [
        ('run', 'Run'),
        ('cycle', 'Cycle'),
        ('swim', 'Swim'),
        ('walk', 'Walk'),
        ('strength', 'Strength Training'),
        ('yoga', 'Yoga'),
        ('other', 'Other'),
    ]
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=32, choices=ACTIVITY_CHOICES)
    duration_minutes = models.PositiveIntegerField()
    distance_km = models.FloatField(null=True, blank=True)
    calories_burned = models.FloatField(null=True, blank=True)
    intensity = models.CharField(max_length=20, choices=[('low', 'Low'), ('moderate', 'Moderate'), ('high', 'High')], default='moderate')
    notes = models.TextField(blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['user', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.user.user.username} - {self.activity_type} @ {self.timestamp}"


class Workout(models.Model):
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    CATEGORY_CHOICES = [
        ('cardio', 'Cardio'),
        ('strength', 'Strength'),
        ('flexibility', 'Flexibility'),
        ('sports', 'Sports'),
        ('recovery', 'Recovery'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=32, choices=CATEGORY_CHOICES)
    difficulty = models.CharField(max_length=32, choices=DIFFICULTY_CHOICES)
    duration_minutes = models.PositiveIntegerField()
    instructions = models.TextField()
    equipment_needed = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.difficulty})"


class LeaderboardEntry(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='leaderboard_entries')
    score = models.FloatField(default=0)
    rank = models.PositiveIntegerField(null=True, blank=True)
    total_activities = models.PositiveIntegerField(default=0)
    total_duration = models.PositiveIntegerField(default=0)
    period = models.CharField(max_length=20, choices=[('weekly', 'Weekly'), ('monthly', 'Monthly'), ('all_time', 'All Time')], default='all_time')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-score']
        unique_together = [['user', 'period']]

    def __str__(self):
        return f"{self.user.user.username} - {self.score} ({self.period})"
