# collection/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ArtworkViewSet, ArtistViewSet, MediumCategoryViewSet,
    ProlificArtistView, MediumSummaryView, RecentArtworksView,
    api_root
)
# Create a router instance for handling ViewSets (standard CRUD)
router = DefaultRouter()
router.register(r'artworks', ArtworkViewSet)
router.register(r'artists', ArtistViewSet)
router.register(r'mediums', MediumCategoryViewSet)

urlpatterns = [
    # My landing page
    path('', api_root, name='api-root'),

    # Custom Query Routes (Required for R3)
    # Query 1: Most Prolific Artist by Style
    path('artists/prolific/', ProlificArtistView.as_view(), name='prolific-artists'),

    # Query 2: Summary of medium usage
    path('mediums/summary/', MediumSummaryView.as_view(), name='medium-summary'),

    # Query 3: Recent artworks (on or after 1990)
    path('artworks/recent/', RecentArtworksView.as_view(), name='recent-artworks'),

# Standard CRUD routes (handled by the router)
    path('', include(router.urls)),
]