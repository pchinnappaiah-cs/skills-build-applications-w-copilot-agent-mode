from django.urls import path, include
from rest_framework import routers
from .views import (
    UserProfileViewSet,
    TeamViewSet,
    ActivityViewSet,
    WorkoutViewSet,
    LeaderboardViewSet,
)

router = routers.DefaultRouter()
router.register(r'profiles', UserProfileViewSet, basename='profile')
router.register(r'teams', TeamViewSet, basename='team')
router.register(r'activities', ActivityViewSet, basename='activity')
router.register(r'workouts', WorkoutViewSet, basename='workout')
router.register(r'leaderboard', LeaderboardViewSet, basename='leaderboard')

# The router.urls includes the api_root view
urlpatterns = [
    path('', include(router.urls)),
]
