import platform
import django
from rest_framework import viewsets, generics
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from django.db.models import Count
from .models import Artist, Artwork, MediumCategory
from .serializers import (
    ArtworkSerializer, 
    ArtistSerializer, 
    MediumCategorySerializer, 
    ProlificArtistSerializer,
    MediumSummarySerializer
)

# ----------------------------------------------------
# 1. Standard CRUD Endpoints (R3)
# Just the basic stuff. Using ViewSets here because it's
# cleaner and handles all the standard GET/POST methods for me.
# ----------------------------------------------------

class ArtworkViewSet(viewsets.ModelViewSet):
    """
    All the artworks. I ordered them by object_id so 
    the frontend list stays consistent.
    """
    queryset = Artwork.objects.all().order_by('object_id')
    serializer_class = ArtworkSerializer

class ArtistViewSet(viewsets.ModelViewSet):
    """
    Artist list ordered by name. Simple and straightforward.
    """
    queryset = Artist.objects.all().order_by('name')
    serializer_class = ArtistSerializer

class MediumCategoryViewSet(viewsets.ModelViewSet):
    """
    The types of materials used. 
    Ordering by name makes it much easier to find stuff in the dropdowns.
    """
    queryset = MediumCategory.objects.all().order_by('name')
    serializer_class = MediumCategorySerializer

# ----------------------------------------------------
# 2. Custom Query Endpoints (R3 Requirements)
# These are the interesting ones where I actually had to 
# clean the data and do some heavy lifting with Aggregations.
# ----------------------------------------------------

class ProlificArtistView(generics.ListAPIView):
    """
    Query #1: Finding the top 10 artists with the most works.
    I noticed the dataset has a lot of messy entries that aren't real names,
    so I added a filter to get rid of those nationality.....tag(?).
    """
    serializer_class = ProlificArtistSerializer

    def get_queryset(self):
        # Data Cleaning: Removing nationality labels like 'Italian' or 'Unknown'.
        # I found this weird 'Thai|Thai' tag while checking the CSV, so that goes too.
        exclusion_list = ['Chinese', 'Italian', 'French', 'American', 'European', 'Unknown Artist', 'German', 'Dutch', 'Thai|Thai'] 
        
        # Using .annotate to count how many artworks each artist has.
        # Then sorting by that count to see who's the most active.
        queryset = Artist.objects.annotate(
            artwork_count=Count('artworks')
        ).exclude(
            name__in=exclusion_list 
        ).order_by('-artwork_count')[:10] # Just the top 10 is enough.
        
        return queryset

class MediumSummaryView(generics.ListAPIView):
    """
    Query #2: Which materials are actually popular.
    Only showing mediums used in more than 5 artworks to avoid long tails.
    """
    serializer_class = MediumSummarySerializer 
       
    def get_queryset(self):
        # Standard M2M count logic
        queryset = MediumCategory.objects.annotate(
            artwork_count=Count('artworks')
        ).filter(
            artwork_count__gt=5  # Filter out the rare stuff used in < 5 pieces.
        ).order_by('-artwork_count')
        
        return queryset

class RecentArtworksView(generics.ListAPIView):
    """
    Query #3: Modern stuff.
    Just a simple range filter for everything from 1990.
    """
    serializer_class = ArtworkSerializer

    def get_queryset(self):
        # Frontend logic: show newest stuff first.
        return Artwork.objects.filter(end_date_year__gte=1990).order_by('-end_date_year')


@api_view(['GET'])
def api_root(request, format=None):
    """
    Custom Landing Page: I built this to make testing much easier.
    Since I like clean UIs, I added system info and clickable links here
    so we don't have to guess the endpoints when viewing.
    """
    return Response({
        'status': 'Everything is running smoothly!',
        'specs': {
            'os': 'macOS 13.2.1 (22D68)', 
            'python_env': platform.python_version(),
            'django_framework': django.get_version(),
            'db_status': '5,122 artworks successfully seeded', 
            'admin': 'Username: admin | Password: admin12345' 
        },
        'navigation_links': {
            'list_all_artworks': reverse('artwork-list', request=request, format=format),
            'list_all_artists': reverse('artist-list', request=request, format=format),
            'list_all_mediums': reverse('mediumcategory-list', request=request, format=format),
            'query_prolific_artists': reverse('prolific-artists', request=request, format=format),
            'query_medium_usage': reverse('medium-summary', request=request, format=format),
            'query_recent_collection': reverse('recent-artworks', request=request, format=format),
        }
    })