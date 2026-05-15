from rest_framework import serializers
from .models import Bookmark, Collection, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


class CollectionSerializer(serializers.ModelSerializer):
    bookmark_count = serializers.IntegerField(source='bookmarks.count', read_only=True)

    class Meta:
        model = Collection
        fields = ['id', 'name', 'description', 'created_at', 'bookmark_count']
        read_only_fields = ['created_at']


class BookmarkSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    owner = serializers.StringRelatedField(read_only=True)
    collection_name = serializers.CharField(source='collection.name', read_only=True, default=None)

    class Meta:
        model = Bookmark
        fields = ['id', 'title', 'url', 'description', 'owner', 'collection',
                  'collection_name', 'tags', 'is_favorite', 'is_public',
                  'created_at', 'updated_at']
        read_only_fields = ['owner', 'created_at', 'updated_at']