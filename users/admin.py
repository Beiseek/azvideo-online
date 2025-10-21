"""
Custom admin for users app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from .models import UserProfile, UserActivity


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Профиль'
    filter_horizontal = ['favorite_movies', 'favorite_series', 'watchlist_movies', 'watchlist_series']


class UserAdmin(BaseUserAdmin):
    inlines = [UserProfileInline]
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_blocked', 'date_joined']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'profile__is_blocked']
    
    def is_blocked(self, obj):
        return obj.profile.is_blocked if hasattr(obj, 'profile') else False
    is_blocked.boolean = True
    is_blocked.short_description = 'Заблокирован'


# Перерегистрация User модели с новым админом
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'activity_type', 'content_type', 'content_title', 'created_at']
    list_filter = ['activity_type', 'content_type', 'created_at']
    search_fields = ['user__username', 'content_title']
    readonly_fields = ['user', 'activity_type', 'content_type', 'content_id', 'content_title', 'created_at']
    
    def has_add_permission(self, request):
        return False

