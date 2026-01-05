# collection/serializers.py

from rest_framework import serializers
from .models import Artist, Artwork, MediumCategory

# --- 1. Basic Serializers ---
class MediumCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MediumCategory
        fields = ('name',)

class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = ('name', 'period_style')

# --- 2. Core Artwork Serializer ---
class ArtworkSerializer(serializers.ModelSerializer):
    # Use the nested serializer for M2M relationship
    mediums = MediumCategorySerializer(many=True, read_only=True)
    # Display the artist's name, not just the ID (Foreign Key)
    artist_name = serializers.CharField(source='artist.name', read_only=True)

    class Meta:
        model = Artwork
        # Include all fields plus the custom artist_name field
        fields = ('object_id', 'title', 'department', 'end_date_year', 'artist_name', 'mediums')
        read_only_fields = ('artist_name', 'mediums')

# --- 3. Custom Query Serializers (For Complex R3 Queries) ---

# This serializer is used for Query #1: Most Prolific Artist by Style
class ProlificArtistSerializer(serializers.Serializer):
    artist_name = serializers.CharField(source='name')
    artwork_count = serializers.IntegerField()
    period_style = serializers.CharField()

# Query #2: Medium Summary
class MediumSummarySerializer(serializers.Serializer):
    name = serializers.CharField()
    artwork_count = serializers.IntegerField()