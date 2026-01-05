# tests.py
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from collection.models import Artist, Artwork # Fixed relative import for Django test runner

class ArtApiTests(TestCase):
    def setUp(self):
        # Setting up some dummy data to verify JSON structure.
        # Just making sure the API doesn't break when rendering for the frontend.
        self.client = APIClient()
        self.artist = Artist.objects.create(name="Test Artist", period_style="Modern")
        self.artwork = Artwork.objects.create(
            object_id=9999, 
            title="Test Piece", 
            department="Lehman",
            end_date_year=2020,
            artist=self.artist
        )

    def test_get_artwork_list(self):
        # Basic check: test if we can fetch the artwork list
        response = self.client.get('/api/artworks/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_prolific_artist_query(self):
        # Checking if my exclude logic works. 
        # It should at least find the 'Test Artist' I just created.
        response = self.client.get('/api/artists/prolific/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) >= 1)

    def test_post_artwork(self):
        # POST Test: Testing if new entries are correctly saved to the SQLite DB.
        # Crucial for R3 requirements.
        data = {
            "object_id": 8888,
            "title": "New POST Artwork",
            "department": "Lehman Collection",
            "end_date_year": 2024
        }
        response = self.client.post('/api/artworks/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)