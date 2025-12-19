from django.contrib import admin
from .models import UserProfile, Team, Activity, LeaderboardEntry, Workout


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_activities', 'total_duration_minutes', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at', 'total_activities', 'total_duration_minutes')


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'leader', 'member_count', 'created_at')
    search_fields = ('name',)
    filter_horizontal = ('members',)
    readonly_fields = ('created_at', 'updated_at')

    def member_count(self, obj):
        return obj.members.count()
    member_count.short_description = 'Members'


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'duration_minutes', 'distance_km', 'intensity', 'timestamp')
    list_filter = ('activity_type', 'intensity', 'timestamp')
    search_fields = ('user__user__username',)
    readonly_fields = ('created_at',)
    date_hierarchy = 'timestamp'


@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'difficulty', 'duration_minutes', 'created_at')
    list_filter = ('category', 'difficulty')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(LeaderboardEntry)
class LeaderboardAdmin(admin.ModelAdmin):
    list_display = ('user', 'rank', 'score', 'period', 'total_activities', 'updated_at')
    list_filter = ('period',)
    search_fields = ('user__user__username',)
    readonly_fields = ('updated_at',)
