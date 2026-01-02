from rest_framework import serializers
from .models import SocialPost, PostPlatform


class PostPlatformSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostPlatform
        fields = ['id', 'name', 'code', 'website']


class SocialPostSerializer(serializers.ModelSerializer):
    platform = PostPlatformSerializer(read_only=True)
    tags = serializers.SerializerMethodField()
    
    class Meta:
        model = SocialPost
        fields = [
            'id', 'name', 'platform', 'link', 'description', 
            'tags', 'created_at', 'updated_at'
        ]
    
    def get_tags(self, obj):
        return [tag.name for tag in obj.tags.all()]