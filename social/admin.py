from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import PostPlatform, SocialPost

@admin.register(PostPlatform)
class PostPlatformAdmin(ModelAdmin):
    pass



@admin.register(SocialPost)
class SocialPostAdmin(ModelAdmin):
    pass
