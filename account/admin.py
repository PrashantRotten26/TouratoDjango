from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_type', 'approval_status', 'is_active', 'created_at']
    list_filter = ['user_type', 'approval_status', 'is_active']
    search_fields = ['user__username', 'user__email']
    actions = ['approve_users', 'reject_users']
    
    def approve_users(self, request, queryset):
        queryset.update(approval_status='approved', is_active=True)
        self.message_user(request, f'{queryset.count()} users approved successfully.')
    approve_users.short_description = 'Approve selected users'
    
    def reject_users(self, request, queryset):
        queryset.update(approval_status='rejected', is_active=False)
        self.message_user(request, f'{queryset.count()} users rejected.')
    reject_users.short_description = 'Reject selected users'
