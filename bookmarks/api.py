from rest_framework import viewsets, permissions
from .models import Bookmark, Collection
from .serializers import BookmarkSerializer, CollectionSerializer


class IsOwner(permissions.BasePermission):
    """Sadece nesnenin sahibi erişebilir."""
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class BookmarkViewSet(viewsets.ModelViewSet):
    serializer_class = BookmarkSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        # Kullanıcı sadece kendi bookmark'larını görür
        return Bookmark.objects.filter(owner=self.request.user)\
            .select_related('collection').prefetch_related('tags')

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class CollectionViewSet(viewsets.ModelViewSet):
    serializer_class = CollectionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Collection.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)