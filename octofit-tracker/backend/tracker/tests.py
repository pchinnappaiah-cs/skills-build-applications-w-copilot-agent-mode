from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from datetime import timedelta

from .models import UserProfile, Team, Activity, LeaderboardEntry, Workout

User = get_user_model()


class UserProfileModelTest(TestCase):
    """Test UserProfile model."""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123')
        self.profile = UserProfile.objects.create(user=self.user, bio='Test bio')

    def test_user_profile_creation(self):
        self.assertEqual(self.profile.user.username, 'testuser')
        self.assertEqual(self.profile.bio, 'Test bio')
        self.assertEqual(self.profile.total_activities, 0)

    def test_user_profile_string_representation(self):
        self.assertEqual(str(self.profile), 'testuser profile')


class TeamModelTest(TestCase):
    """Test Team model."""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123')
        self.profile = UserProfile.objects.create(user=self.user)
        self.team = Team.objects.create(name='Test Team', leader=self.profile)

    def test_team_creation(self):
        self.assertEqual(self.team.name, 'Test Team')
        self.assertEqual(self.team.leader, self.profile)

    def test_add_team_member(self):
        user2 = User.objects.create_user(username='testuser2', email='test2@example.com', password='testpass123')
        profile2 = UserProfile.objects.create(user=user2)
        self.team.members.add(profile2)
        self.assertEqual(self.team.members.count(), 1)

    def test_team_string_representation(self):
        self.assertEqual(str(self.team), 'Test Team')


class ActivityModelTest(TestCase):
    """Test Activity model."""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123')
        self.profile = UserProfile.objects.create(user=self.user)
        self.activity = Activity.objects.create(
            user=self.profile,
            activity_type='run',
            duration_minutes=30,
            distance_km=5.0,
            timestamp=timezone.now()
        )

    def test_activity_creation(self):
        self.assertEqual(self.activity.activity_type, 'run')
        self.assertEqual(self.activity.duration_minutes, 30)
        self.assertEqual(self.activity.distance_km, 5.0)

    def test_activity_string_representation(self):
        self.assertIn('testuser', str(self.activity))
        self.assertIn('run', str(self.activity))


class WorkoutModelTest(TestCase):
    """Test Workout model."""

    def setUp(self):
        self.workout = Workout.objects.create(
            title='Morning Run',
            description='A 30-minute running workout',
            category='cardio',
            difficulty='intermediate',
            duration_minutes=30,
            instructions='Warm up and run at steady pace'
        )

    def test_workout_creation(self):
        self.assertEqual(self.workout.title, 'Morning Run')
        self.assertEqual(self.workout.category, 'cardio')
        self.assertEqual(self.workout.difficulty, 'intermediate')

    def test_workout_string_representation(self):
        self.assertEqual(str(self.workout), 'Morning Run (intermediate)')


class LeaderboardEntryModelTest(TestCase):
    """Test LeaderboardEntry model."""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123')
        self.profile = UserProfile.objects.create(user=self.user)
        self.leaderboard_entry = LeaderboardEntry.objects.create(
            user=self.profile,
            score=100.0,
            rank=1,
            period='all_time'
        )

    def test_leaderboard_entry_creation(self):
        self.assertEqual(self.leaderboard_entry.score, 100.0)
        self.assertEqual(self.leaderboard_entry.rank, 1)
        self.assertEqual(self.leaderboard_entry.period, 'all_time')

    def test_leaderboard_entry_string_representation(self):
        self.assertIn('testuser', str(self.leaderboard_entry))
        self.assertIn('100.0', str(self.leaderboard_entry))


class UserProfileAPITest(APITestCase):
    """Test UserProfile API endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123')
        self.profile = UserProfile.objects.create(user=self.user, bio='Test bio')

    def test_get_profiles(self):
        url = reverse('profile-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_profile(self):
        user = User.objects.create_user(username='newuser', email='newuser@example.com', password='testpass123')
        url = reverse('profile-list')
        data = {'user': user.id, 'bio': 'New bio'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_user_stats(self):
        # Create some activities
        Activity.objects.create(
            user=self.profile,
            activity_type='run',
            duration_minutes=30,
            timestamp=timezone.now()
        )
        url = reverse('profile-stats', kwargs={'pk': self.profile.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_activities'], 1)


class TeamAPITest(APITestCase):
    """Test Team API endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123')
        self.profile = UserProfile.objects.create(user=self.user)
        self.team = Team.objects.create(name='Test Team', leader=self.profile)

    def test_get_teams(self):
        url = reverse('team-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_team(self):
        url = reverse('team-list')
        data = {'name': 'New Team', 'description': 'A new team'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Team')

    def test_add_team_member(self):
        user2 = User.objects.create_user(username='testuser2', email='test2@example.com', password='testpass123')
        profile2 = UserProfile.objects.create(user=user2)
        url = reverse('team-add_member', kwargs={'pk': self.team.id})
        data = {'user_id': profile2.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.team.refresh_from_db()
        self.assertEqual(self.team.members.count(), 1)

    def test_team_leaderboard(self):
        user2 = User.objects.create_user(username='testuser2', email='test2@example.com', password='testpass123')
        profile2 = UserProfile.objects.create(user=user2)
        self.team.members.add(profile2)
        Activity.objects.create(
            user=profile2,
            activity_type='run',
            duration_minutes=30,
            timestamp=timezone.now()
        )
        url = reverse('team-leaderboard', kwargs={'pk': self.team.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class ActivityAPITest(APITestCase):
    """Test Activity API endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123')
        self.profile = UserProfile.objects.create(user=self.user)
        self.activity = Activity.objects.create(
            user=self.profile,
            activity_type='run',
            duration_minutes=30,
            timestamp=timezone.now()
        )

    def test_get_activities(self):
        url = reverse('activity-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_activity(self):
        url = reverse('activity-list')
        data = {
            'user': self.profile.id,
            'activity_type': 'cycle',
            'duration_minutes': 45,
            'distance_km': 10.0
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_recent_activities(self):
        url = reverse('activity-recent')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_activities_by_type(self):
        url = reverse('activity-by_type')
        response = self.client.get(url, {'activity_type': 'run'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_activities_this_week(self):
        url = reverse('activity-this_week')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class WorkoutAPITest(APITestCase):
    """Test Workout API endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.workout = Workout.objects.create(
            title='Morning Run',
            description='A 30-minute running workout',
            category='cardio',
            difficulty='intermediate',
            duration_minutes=30,
            instructions='Warm up and run at steady pace'
        )

    def test_get_workouts(self):
        url = reverse('workout-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_workout(self):
        url = reverse('workout-list')
        data = {
            'title': 'Evening Yoga',
            'description': 'Relaxing yoga session',
            'category': 'flexibility',
            'difficulty': 'beginner',
            'duration_minutes': 45,
            'instructions': 'Follow along with instructor'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_workouts_by_difficulty(self):
        url = reverse('workout-by_difficulty')
        response = self.client.get(url, {'difficulty': 'intermediate'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_workouts_by_category(self):
        url = reverse('workout-by_category')
        response = self.client.get(url, {'category': 'cardio'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class LeaderboardAPITest(APITestCase):
    """Test Leaderboard API endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123')
        self.profile = UserProfile.objects.create(user=self.user)
        self.leaderboard = LeaderboardEntry.objects.create(
            user=self.profile,
            score=100.0,
            rank=1,
            period='all_time'
        )

    def test_get_leaderboard(self):
        url = reverse('leaderboard-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_leaderboard_by_period(self):
        url = reverse('leaderboard-by_period')
        response = self.client.get(url, {'period': 'all_time'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
