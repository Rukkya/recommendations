from flask import Flask
from config import Config
from models import db, init_app
from utils.data_loader import download_goodreads_dataset, load_books_dataset
import os

def create_app():
    """Create a Flask application instance"""
    app = Flask(__name__)
    app.config.from_object(Config)
    init_app(app)
    return app

def init_database():
    """Initialize the database and load sample data"""
    app = create_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if books table is empty
        from models.book import Book
        if Book.query.count() == 0:
            print("Loading books dataset...")
            # Download or create sample dataset
            dataset_path = download_goodreads_dataset()
            # Load books into database
            books_added = load_books_dataset(dataset_path)
            print(f"Added {books_added} books to the database.")
        else:
            print("Books already loaded in the database.")

if __name__ == '__main__':
    init_database()
