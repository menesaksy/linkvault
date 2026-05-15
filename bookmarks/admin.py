from django.contrib import admin
from .models import Tag, Collection, Bookmark


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    search_fields = ['name']


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'collection', 'is_favorite', 'is_public', 'created_at']
    list_filter = ['is_favorite', 'is_public', 'created_at', 'tags']
    search_fields = ['title', 'url', 'description']
    filter_horizontal = ['tags']