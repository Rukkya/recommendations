import pandas as pd
import os
from flask import current_app
from models import db
from models.book import Book

def load_books_dataset(csv_path=None):
    """Load books from CSV file into the database"""
    if not csv_path:
        csv_path = current_app.config['DATASET_PATH']
    
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset file not found at {csv_path}")
    
    # Read the CSV file
    books_df = pd.read_csv(csv_path)
    
    # Clean the data
    books_df = books_df.fillna({
        'title': '',
        'authors': '',
        'average_rating': 0.0,
        'isbn': '',
        'language_code': '',
        'ratings_count': 0,
        'publication_date': '',
        'publisher': ''
    })
    
    # Process the data and insert into database
    books_added = 0
    
    for _, row in books_df.iterrows():
        # Check if book already exists by ISBN
        existing_book = Book.query.filter_by(isbn=row.get('isbn', '')).first()
        if existing_book:
            continue
            
        # Extract year from publication_date if available
        year = None
        if 'publication_date' in row and row['publication_date']:
            try:
                year = int(row['publication_date'].split('/')[-1])
                # Handle 2-digit years
                if year < 100:
                    year = 1900 + year if year > 20 else 2000 + year
            except (ValueError, IndexError):
                pass
        
        # Create new book
        book = Book(
            title=row.get('title', ''),
            author=row.get('authors', ''),
            year=year,
            isbn=row.get('isbn', ''),
            description=row.get('description', ''),
            genres=row.get('categories', ''),
            image_url=row.get('thumbnail', ''),
            language=row.get('language_code', 'en')
        )
        
        # Set ratings data
        book.average_rating = float(row.get('average_rating', 0))
        book.ratings_count = int(row.get('ratings_count', 0))
        
        # Add to database
        db.session.add(book)
        books_added += 1
        
        # Commit in batches to avoid memory issues
        if books_added % 100 == 0:
            db.session.commit()
    
    # Final commit
    db.session.commit()
    
    return books_added

def download_goodreads_dataset():
    """Download Goodreads books dataset if not available"""
    import requests
    import io
    import zipfile
    
    dataset_path = current_app.config['DATASET_PATH']
    data_dir = os.path.dirname(dataset_path)
    
    # Create data directory if it doesn't exist
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    # Skip if dataset already exists
    if os.path.exists(dataset_path):
        return dataset_path
    
    # Sample dataset URL (consider hosting a sample dataset)
    dataset_url = "https://github.com/zygmuntz/goodbooks-10k/raw/master/samples/books.csv"
    
    try:
        # Download the dataset
        response = requests.get(dataset_url)
        response.raise_for_status()
        
        # Save the dataset
        with open(dataset_path, 'wb') as f:
            f.write(response.content)
        
        return dataset_path
    
    except Exception as e:
        print(f"Error downloading dataset: {e}")
        
        # Create a minimal sample dataset if download fails
        create_sample_dataset(dataset_path)
        return dataset_path

def create_sample_dataset(output_path):
    """Create a minimal sample dataset if download fails"""
    # Sample books data
    sample_books = [
        {"title": "To Kill a Mockingbird", "authors": "Harper Lee", "average_rating": 4.27, 
         "isbn": "9780061120084", "language_code": "en", "ratings_count": 3198671, 
         "publication_date": "7/5/1960", "categories": "fiction,classics,literature"},
        {"title": "1984", "authors": "George Orwell", "average_rating": 4.18, 
         "isbn": "9780451524935", "language_code": "en", "ratings_count": 2733221, 
         "publication_date": "6/8/1949", "categories": "fiction,classics,dystopian"},
        {"title": "The Great Gatsby", "authors": "F. Scott Fitzgerald", "average_rating": 3.91, 
         "isbn": "9780743273565", "language_code": "en", "ratings_count": 3275814, 
         "publication_date": "4/10/1925", "categories": "fiction,classics,literature"},
        {"title": "Harry Potter and the Sorcerer's Stone", "authors": "J.K. Rowling", "average_rating": 4.47, 
         "isbn": "9780590353427", "language_code": "en", "ratings_count": 6325594, 
         "publication_date": "6/26/1997", "categories": "fiction,fantasy,young adult"},
        {"title": "The Hobbit", "authors": "J.R.R. Tolkien", "average_rating": 4.28, 
         "isbn": "9780618260300", "language_code": "en", "ratings_count": 2560196, 
         "publication_date": "9/21/1937", "categories": "fiction,fantasy,classics"}
    ]
    
    # Create DataFrame and save to CSV
    df = pd.DataFrame(sample_books)
    df.to_csv(output_path, index=False)
