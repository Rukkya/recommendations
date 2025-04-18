import google.generativeai as genai
from flask import current_app
import json
from models.book import Book

class BookChatbot:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.is_initialized = False
        self.model = None
        self.chat_session = None
        self.context = """
        You are a helpful assistant for a book recommendation system.
        You can discuss books, authors, genres, and provide personalized reading recommendations.
        Keep your responses focused on books, reading, and literature.
        If asked about a specific book, try to provide insights about its themes, author background, and similar books.
        """

    def initialize(self):
        """Initialize the Gemini API client"""
        if not self.api_key:
            self.api_key = current_app.config['GEMINI_API_KEY']

        if not self.api_key:
            raise ValueError("Gemini API key is required")

        # Configure the Gemini API
        genai.configure(api_key=self.api_key)

        # Initialize the model
        self.model = genai.GenerativeModel('gemini-1.5-pro')

        # Start a new chat session
        self.chat_session = self.model.start_chat(history=[])

        # Add the system context as a first message instead
        self.chat_session.send_message(self.context)

        self.is_initialized = True

    def get_book_context(self, book_id):
        """Get context about a specific book to enhance chatbot responses"""
        book = Book.query.get(book_id)
        if not book:
            return ""

        book_context = f"""
        Title: {book.title}
        Author: {book.author}
        Publication Year: {book.year or 'Unknown'}
        Genres: {book.genres or 'Not specified'}
        Average Rating: {book.average_rating}/5 from {book.ratings_count} ratings
        Description: {book.description or 'No description available'}
        """

        return book_context

    def get_user_context(self, user_ratings, preferences=None):
        """Get context about a user's reading habits"""
        if not user_ratings:
            return "No rating history available for this user."

        # Get books the user has rated
        rated_books = []
        for rating in user_ratings:
            book = Book.query.get(rating.book_id)
            if book:
                rated_books.append({
                    'title': book.title,
                    'author': book.author,
                    'rating': rating.rating,
                    'genres': book.genres
                })

        # Extract favorite genres based on highly rated books
        genre_counts = {}
        for book in rated_books:
            if book['rating'] >= 4.0 and book['genres']:
                for genre in book['genres'].split(','):
                    genre = genre.strip()
                    if genre:
                        if genre not in genre_counts:
                            genre_counts[genre] = 0
                        genre_counts[genre] += 1

        favorite_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        favorite_genres = [genre for genre, _ in favorite_genres]

        # Create user context
        user_context = "User's reading profile:\n"

        if favorite_genres:
            user_context += f"Favorite genres: {', '.join(favorite_genres)}\n"

        if preferences:
            user_context += f"Stated preferences: {preferences}\n"

        # Add recently rated books
        if rated_books:
            user_context += "Recently rated books:\n"
            for book in rated_books[-5:]:  # Last 5 rated books
                user_context += f"- {book['title']} by {book['author']}: {book['rating']}/5\n"

        return user_context

    def chat(self, message, user_context=None, book_context=None):
        """Send a message to the chatbot and get a response"""
        if not self.is_initialized:
            self.initialize()

        # Prepare the full context
        full_context = ""
        if user_context:
            full_context += f"USER CONTEXT:\n{user_context}\n\n"

        if book_context:
            full_context += f"BOOK CONTEXT:\n{book_context}\n\n"

        # Include context if available
        if full_context:
            # Add context as a system message
            context_message = f"Here's some additional context to help you respond better:\n{full_context}"
            response = self.chat_session.send_message(context_message, stream=False)

        # Send user message and get response
        response = self.chat_session.send_message(message, stream=False)

        return response.text
