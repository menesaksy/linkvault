from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from bookmarks.api import BookmarkViewSet, CollectionViewSet

router = DefaultRouter()
router.register(r'bookmarks', BookmarkViewSet, basename='api-bookmark')
router.register(r'collections', CollectionViewSet, basename='api-collection')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),  # DRF browsable API login
    path('', include('bookmarks.urls')),
]