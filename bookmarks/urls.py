from django.urls import path
from . import views

urlpatterns = [
    path('', views.BookmarkListView.as_view(), name='bookmark_list'),
    path('bookmark/<int:pk>/', views.BookmarkDetailView.as_view(), name='bookmark_detail'),
    path('bookmark/new/', views.BookmarkCreateView.as_view(), name='bookmark_create'),
    path('bookmark/<int:pk>/edit/', views.BookmarkUpdateView.as_view(), name='bookmark_update'),
    path('bookmark/<int:pk>/delete/', views.BookmarkDeleteView.as_view(), name='bookmark_delete'),

    path('collections/', views.CollectionListView.as_view(), name='collection_list'),
    path('collection/<int:pk>/', views.CollectionDetailView.as_view(), name='collection_detail'),
    path('collection/new/', views.CollectionCreateView.as_view(), name='collection_create'),
    path('collection/<int:pk>/edit/', views.CollectionUpdateView.as_view(), name='collection_update'),
    path('collection/<int:pk>/delete/', views.CollectionDeleteView.as_view(), name='collection_delete'),

    path('signup/', views.signup, name='signup'),
    path('bookmark/<int:pk>/toggle-favorite/', views.toggle_favorite, name='toggle_favorite'),
]