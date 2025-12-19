from rest_framework import serializers
from .models import UserProfile, Team, Activity, LeaderboardEntry, Workout
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')
        read_only_fields = ('id',)


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = UserProfile
        fields = ('id', 'user', 'username', 'email', 'bio', 'avatar_url', 'total_activities', 'total_duration_minutes', 'created_at', 'updated_at')
        read_only_fields = ('id', 'total_activities', 'total_duration_minutes', 'created_at', 'updated_at')


class TeamMemberSerializer(serializers.ModelSerializer):
    """Lightweight serializer for team members within a team response."""
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = UserProfile
        fields = ('id', 'username')


class TeamSerializer(serializers.ModelSerializer):
    members = TeamMemberSerializer(many=True, read_only=True)
    leader_name = serializers.CharField(source='leader.user.username', read_only=True)

    class Meta:
        model = Team
        fields = ('id', 'name', 'description', 'members', 'leader', 'leader_name', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class ActivitySerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.user.username', read_only=True)

    class Meta:
        model = Activity
        fields = ('id', 'user', 'username', 'activity_type', 'duration_minutes', 'distance_km', 'calories_burned', 'intensity', 'notes', 'timestamp', 'created_at')
        read_only_fields = ('id', 'created_at')


class WorkoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workout
        fields = ('id', 'title', 'description', 'category', 'difficulty', 'duration_minutes', 'instructions', 'equipment_needed', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class LeaderboardSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    username = serializers.CharField(source='user.user.username', read_only=True)

    class Meta:
        model = LeaderboardEntry
        fields = ('id', 'user', 'username', 'score', 'rank', 'total_activities', 'total_duration', 'period', 'updated_at')
        read_only_fields = ('id', 'updated_at')
