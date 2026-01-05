import csv
import os
from collection.models import Artist, Artwork, MediumCategory
from django.db import transaction # Used for efficient bulk operations

# --- FILE PATHS (Relative to the project root, where you will run the script) ---
# NOTE: The file names MUST match the output of your filtering script.
ARTIST_CSV_PATH = 'data/artist_final.csv'
ARTWORK_CSV_PATH = 'data/artwork_final.csv'
MEDIUM_CSV_PATH = 'data/medium_final.csv' 


def run():
    """
    The main function called by `python manage.py runscript data_loader`
    """
    print("--- Starting Data Load for Lehman Collection ---")

    # Clear old data first to ensure a clean run
    MediumCategory.objects.all().delete()
    Artwork.objects.all().delete()
    Artist.objects.all().delete()
    
    # --- 1. Load the Independent Tables First ---
    load_mediums()
    load_artists()

    # --- 2. Load the Core Table (Artwork) and Create Relationships ---
    load_artworks_and_relationships()

    print("\n--- Data Load Complete: Database is Populated ---")


def load_mediums():
    """Loads the MediumCategory table (M2M target)"""
    print("1. Loading Medium Categories...")
    
    with open(MEDIUM_CSV_PATH, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        mediums_to_create = []
        
        for row in reader:
            name = row.get('name', '').strip()
            if name:
                mediums_to_create.append(MediumCategory(name=name))
        
        # Bulk creation is efficient for large datasets (R4)
        MediumCategory.objects.bulk_create(mediums_to_create, ignore_conflicts=True)
        print(f"   -> Created {MediumCategory.objects.count()} Mediums.")


def load_artists():
    """Loads the Artist table (FK parent)"""
    print("2. Loading Artists...")
    
    with open(ARTIST_CSV_PATH, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        artists_to_create = []
        
        for row in reader:
            # Note: We only extracted the unique 'name' field in the final filtering script
            name = row.get('name', '').strip()
            # If you included the 'Artist Nationality' column in your final artist CSV, 
            # you would assign it here, e.g., period_style = row.get('Artist Nationality')
            
            if name:
                artists_to_create.append(Artist(name=name)) 
        
        Artist.objects.bulk_create(artists_to_create, ignore_conflicts=True)
        print(f"   -> Created {Artist.objects.count()} Artists.")


def load_artworks_and_relationships():
    """Loads Artwork and establishes Foreign Key and Many-to-Many links"""
    print("\n3. Loading Artworks and establishing relationships...")
    
    # Pre-fetch FK and M2M targets for fast lookups
    artist_lookup = {artist.name: artist for artist in Artist.objects.all()}
    medium_lookup = {medium.name: medium for medium in MediumCategory.objects.all()}

    artworks_to_create = []
    artwork_mediums_map = {} # Maps Artwork ID to a list of MediumCategory objects

    with open(ARTWORK_CSV_PATH, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)

        for row in reader:
            # --- 3a. Handle Foreign Key Lookup (Artist) ---
            artist_name_key = row.get('Artist Display Name', '').strip()
            artist_obj = artist_lookup.get(artist_name_key) 
            
            if not artist_obj:
                # If the artist is missing (e.g., blank name), skip this artwork
                continue

            try:
                # --- 3b. Data Conversion ---
                object_id = int(row.get('Object ID'))
                end_year = int(row.get('Object End Date')) if row.get('Object End Date', '').isdigit() else None
                
                # --- Create the Artwork Object ---
                artwork = Artwork(
                    object_id=object_id,
                    title=row.get('Title', row.get('Object Name', 'Untitled')), # Use Title, fallback to Object Name
                    department=row.get('Department', ''),
                    end_date_year=end_year,
                    artist=artist_obj # This sets the Foreign Key!
                )
                artworks_to_create.append(artwork)

                # --- 3c. Prepare Many-to-Many Links (MediumCategory) ---
                raw_medium_string = row.get('Medium', '')
                if raw_medium_string:
                    medium_names = [m.strip() for m in raw_medium_string.split(',') if m.strip()]
                    
                    # Store M2M objects only if they exist in our lookup table
                    medium_objects = [medium_lookup[name] for name in medium_names if name in medium_lookup]
                    if medium_objects:
                        artwork_mediums_map[object_id] = medium_objects

            except Exception as e:
                print(f"Error processing artwork ID {row.get('Object ID')}: {e}")
        
    # --- 3d. Bulk Create Artworks ---
    Artwork.objects.bulk_create(artworks_to_create)
    print(f"   -> Created {Artwork.objects.count()} Artworks.")

    # --- 3e. Set Many-to-Many Relationships ---
    # NOTE: M2M cannot be set during bulk_create, must be done separately.
    print("4. Establishing Many-to-Many links for Mediums...")
    
    # Retrieve the objects we just created
    all_artworks = {a.object_id: a for a in Artwork.objects.all()}

    # Use a transaction for efficiency when updating M2M fields
    with transaction.atomic():
        for artwork_id, medium_list in artwork_mediums_map.items():
            artwork_obj = all_artworks.get(artwork_id)
            if artwork_obj:
                # Use set() to establish the relationship
                artwork_obj.mediums.set(medium_list)
    
    print(f"   -> Successfully linked Mediums to Artworks.")