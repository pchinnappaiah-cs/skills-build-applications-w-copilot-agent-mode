from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta

from .models import UserProfile, Team, Activity, LeaderboardEntry, Workout
from .serializers import (
    UserProfileSerializer,
    TeamSerializer,
    ActivitySerializer,
    WorkoutSerializer,
    LeaderboardSerializer,
)


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [AllowAny]

    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Get user statistics including total activities and duration."""
        profile = self.get_object()
        activities = Activity.objects.filter(user=profile)
        total_activities = activities.count()
        total_duration = activities.aggregate(Sum('duration_minutes'))['duration_minutes__sum'] or 0
        total_calories = activities.aggregate(Sum('calories_burned'))['calories_burned__sum'] or 0

        return Response({
            'total_activities': total_activities,
            'total_duration_minutes': total_duration,
            'total_calories': total_calories,
            'teams': profile.teams.count(),
        })

    @action(detail=True, methods=['get'])
    def activities(self, request, pk=None):
        """Get all activities for a user."""
        profile = self.get_object()
        activities = Activity.objects.filter(user=profile).order_by('-timestamp')
        serializer = ActivitySerializer(activities, many=True)
        return Response(serializer.data)


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [AllowAny]

    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        """Add a member to the team."""
        team = self.get_object()
        user_id = request.data.get('user_id')
        try:
            profile = UserProfile.objects.get(id=user_id)
            team.members.add(profile)
            return Response({'status': 'member added'})
        except UserProfile.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def remove_member(self, request, pk=None):
        """Remove a member from the team."""
        team = self.get_object()
        user_id = request.data.get('user_id')
        try:
            profile = UserProfile.objects.get(id=user_id)
            team.members.remove(profile)
            return Response({'status': 'member removed'})
        except UserProfile.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'])
    def leaderboard(self, request, pk=None):
        """Get team leaderboard."""
        team = self.get_object()
        members = team.members.all()
        leaderboard = []
        for member in members:
            total_activities = Activity.objects.filter(user=member).count()
            total_duration = Activity.objects.filter(user=member).aggregate(Sum('duration_minutes'))['duration_minutes__sum'] or 0
            leaderboard.append({
                'user_id': member.id,
                'username': member.user.username,
                'total_activities': total_activities,
                'total_duration': total_duration,
            })
        leaderboard.sort(key=lambda x: x['total_duration'], reverse=True)
        for idx, entry in enumerate(leaderboard, 1):
            entry['rank'] = idx
        return Response(leaderboard)


class ActivityViewSet(viewsets.ModelViewSet):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent activities (last 20)."""
        qs = self.queryset.order_by('-timestamp')[:20]
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_user(self, request):
        """Get activities for a specific user."""
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        activities = Activity.objects.filter(user_id=user_id).order_by('-timestamp')
        serializer = self.get_serializer(activities, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get activities by type."""
        activity_type = request.query_params.get('activity_type')
        if not activity_type:
            return Response({'error': 'activity_type is required'}, status=status.HTTP_400_BAD_REQUEST)
        activities = Activity.objects.filter(activity_type=activity_type).order_by('-timestamp')
        serializer = self.get_serializer(activities, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def this_week(self, request):
        """Get activities from this week."""
        today = timezone.now()
        week_start = today - timedelta(days=today.weekday())
        activities = Activity.objects.filter(timestamp__gte=week_start).order_by('-timestamp')
        serializer = self.get_serializer(activities, many=True)
        return Response(serializer.data)


class WorkoutViewSet(viewsets.ModelViewSet):
    queryset = Workout.objects.all()
    serializer_class = WorkoutSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=['get'])
    def by_difficulty(self, request):
        """Get workouts by difficulty level."""
        difficulty = request.query_params.get('difficulty')
        if not difficulty:
            return Response({'error': 'difficulty is required'}, status=status.HTTP_400_BAD_REQUEST)
        workouts = Workout.objects.filter(difficulty=difficulty)
        serializer = self.get_serializer(workouts, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get workouts by category."""
        category = request.query_params.get('category')
        if not category:
            return Response({'error': 'category is required'}, status=status.HTTP_400_BAD_REQUEST)
        workouts = Workout.objects.filter(category=category)
        serializer = self.get_serializer(workouts, many=True)
        return Response(serializer.data)


class LeaderboardViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LeaderboardEntry.objects.order_by('-score')
    serializer_class = LeaderboardSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=['get'])
    def by_period(self, request):
        """Get leaderboard by period (weekly, monthly, all_time)."""
        period = request.query_params.get('period', 'all_time')
        leaderboard = LeaderboardEntry.objects.filter(period=period).order_by('-score')
        serializer = self.get_serializer(leaderboard, many=True)
        return Response(serializer.data)
