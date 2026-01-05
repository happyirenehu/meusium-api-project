# collection/models.py

from django.db import models

# 1. The Artist Model (Parent)
# I kept this simple but made 'name' unique so my seeding script 
# won't create the same person twice if they appear in multiple rows.
class Artist(models.Model):
    # Prevent duplicates during bulk loading
    name = models.CharField(max_length=255, unique=True)
    
    # Mapping 'Nationality' from the MET CSV to this field. 
    # It helps group artists by their background or style.
    period_style = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name

# 2. The Medium Category Model (M2M Target)
# This handles the complexity of materials (Requirement R2).
# Separating this into its own table makes it way easier to filter by medium.
class MediumCategory(models.Model):
    # Must be unique so we have a clean list of materials (like 'Oil on canvas')
    name = models.CharField(max_length=100, unique=True)
    
    class Meta:
        verbose_name_plural = "Medium Categories" # Fix the annoying 's' in Django Admin

    def __str__(self):
        return self.name
        
# 3. The Artwork Model (Core)
# This is the main table that ties everything together.
# I used the MET's 'Object ID' as the PK to stay consistent with the source.
class Artwork(models.Model):
    # Using 'Object ID' from the dataset as the primary key
    object_id = models.IntegerField(primary_key=True) 
    title = models.CharField(max_length=255)
    department = models.CharField(max_length=150)
    
    # Keeping this as an Integer so I can easily do range filters (e.g., artworks after 1990)
    end_date_year = models.IntegerField(null=True, blank=True) 

    # One-to-Many: Each artwork has one main artist.
    # Set to NULL on delete so we don't lose the artwork if an artist record is removed.
    artist = models.ForeignKey(
        Artist, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='artworks'
    )

    # Many-to-Many: Some art uses multiple materials.
    # This many-to-many link is what allows my 'Medium Summary' query to work.
    mediums = models.ManyToManyField(MediumCategory, related_name='artworks')

    def __str__(self):
        return self.title