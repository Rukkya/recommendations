from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
from datetime import datetime

from config import Config
from models import db, init_app
from models.user import User
from models.book import Book
from models.rating import Rating
from models.recommendation import Recommendation
from utils.recommendation_engine import RecommendationEngine
from utils.data_loader import load_books_dataset, download_goodreads_dataset
from utils.chatbot import BookChatbot

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
init_app(app)

# Initialize global objects
recommendation_engine = RecommendationEngine()
chatbot = BookChatbot()
# Add this import at the top of the file
import json
def _build_collaborative_matrix(self):
    """Build collaborative filtering matrix using SVD"""
    # Get all ratings from database
    ratings = Rating.query.all()
    
    if not ratings or len(ratings) < 2:
        # Not enough ratings to build a meaningful matrix
        self.collaborative_matrix = None
        return
    
    # Continue with building the matrix...
# Add a book_by_id filter
@app.template_filter('book_by_id')
def book_by_id_filter(book_id):
    """Get a book by its ID for use in templates"""
    from models.book import Book
    return Book.query.get(book_id)
# Add a fromjson filter
@app.template_filter('fromjson')
def fromjson_filter(value):
    return json.loads(value)


from datetime import datetime

# Add this context processor before your routes
@app.context_processor
def inject_now():
    return {'now': datetime.utcnow}
# Routes
@app.route('/')
def index():
    """Homepage - shows popular books for non-logged-in users"""
    popular_books = Book.query.order_by(Book.average_rating.desc()).limit(10).all()
    return render_template('index.html', popular_books=popular_books)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """User signup page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered', 'error')
            return render_template('signup.html')
            
        # Create new user
        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        
        # Log in the new user
        login_user(user)
        
        # Redirect to onboarding
        return redirect(url_for('onboarding'))
    
    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    return redirect(url_for('index'))

@app.route('/onboarding', methods=['GET', 'POST'])
@login_required
def onboarding():
    """Onboarding page to collect user preferences"""
    if request.method == 'POST':
        # Get selected genres
        selected_genres = request.form.getlist('genres')
        
        # Get favorite books
        favorite_books = request.form.getlist('favorite_books')
        
        # Update user preferences
        preferences = {
            'genres': selected_genres,
            'favorite_books': favorite_books
        }
        
        current_user.preferences = json.dumps(preferences)
        db.session.commit()
        
        # Generate initial recommendations
        recommendation_engine.generate_recommendations(current_user.id)
        
        return redirect(url_for('dashboard'))
    
    # Get a selection of popular genres
    genres = [
        'Fiction', 'Fantasy', 'Science Fiction', 'Mystery', 'Thriller', 
        'Romance', 'Historical Fiction', 'Non-fiction', 'Biography', 
        'Self-help', 'Business', 'Science', 'Poetry', 'Comics', 'Classics'
    ]
    
    # Get popular books for selection
    popular_books = Book.query.order_by(Book.ratings_count.desc()).limit(20).all()
    
    return render_template('onboarding.html', genres=genres, popular_books=popular_books)

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard with personalized recommendations"""
    # Get recommendations for the user
    recommendations = Recommendation.query.filter_by(user_id=current_user.id).order_by(Recommendation.score.desc()).limit(10).all()
    
    # If no recommendations exist, generate them
    if not recommendations:
        recommendation_engine.generate_recommendations(current_user.id)
        recommendations = Recommendation.query.filter_by(user_id=current_user.id).order_by(Recommendation.score.desc()).limit(10).all()
    
    # Get recently rated books
    recent_ratings = Rating.query.filter_by(user_id=current_user.id).order_by(Rating.timestamp.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                           recommendations=recommendations, 
                           recent_ratings=recent_ratings)

@app.route('/book/<int:book_id>')
def book_detail(book_id):
    """Book detail page"""
    book = Book.query.get_or_404(book_id)
    
    # Get similar books based on content
    similar_books = []
    if recommendation_engine.is_initialized:
        similar_book_ids = recommendation_engine.get_content_based_recommendations(book.id, top_n=5)
        similar_books = [Book.query.get(book_id) for book_id, _ in similar_book_ids if Book.query.get(book_id)]
    
    # Check if user has rated this book
    user_rating = None
    if current_user.is_authenticated:
        user_rating = Rating.query.filter_by(user_id=current_user.id, book_id=book.id).first()
    
    return render_template('book_detail.html', book=book, similar_books=similar_books, user_rating=user_rating)

@app.route('/rate/<int:book_id>', methods=['POST'])
@login_required
def rate_book(book_id):
    """Rate a book"""
    book = Book.query.get_or_404(book_id)
    
    rating_value = float(request.form.get('rating', 0))
    review = request.form.get('review', '')
    
    # Check if user has already rated this book
    existing_rating = Rating.query.filter_by(user_id=current_user.id, book_id=book.id).first()
    
    if existing_rating:
        # Update existing rating
        existing_rating.rating = rating_value
        existing_rating.review = review
        existing_rating.timestamp = datetime.utcnow()
    else:
        # Create new rating
        new_rating = Rating(
            user_id=current_user.id,
            book_id=book.id,
            rating=rating_value,
            review=review
        )
        db.session.add(new_rating)
    
    db.session.commit()
    
    # Update book's average rating
    book.update_average_rating()
    db.session.commit()
    
    # Regenerate recommendations
    recommendation_engine.generate_recommendations(current_user.id)
    
    flash('Thank you for your rating!', 'success')
    return redirect(url_for('book_detail', book_id=book.id))

@app.route('/chatbot')
@login_required
def chatbot_page():
    """Chatbot interface"""
    return render_template('chatbot.html')

@app.route('/api/chatbot', methods=['POST'])
@login_required
def chatbot_api():
    """API endpoint for chatbot interaction"""
    data = request.json
    message = data.get('message', '')
    book_id = data.get('book_id')
    
    # Get book context if provided
    book_context = None
    if book_id:
        book_context = chatbot.get_book_context(book_id)
    
    # Get user context
    user_ratings = Rating.query.filter_by(user_id=current_user.id).all()
    user_context = chatbot.get_user_context(user_ratings, current_user.preferences)
    
    # Get response from chatbot
    response = chatbot.chat(message, user_context, book_context)
    
    return jsonify({'response': response})

@app.route('/search')
def search():
    """Search for books"""
    query = request.args.get('q', '')
    
    if not query:
        return render_template('search.html', books=[], query='')
    
    # Search in title, author, and description
    books = Book.query.filter(
        db.or_(
            Book.title.ilike(f'%{query}%'),
            Book.author.ilike(f'%{query}%'),
            Book.description.ilike(f'%{query}%')
        )
    ).limit(20).all()
    
    return render_template('search.html', books=books, query=query)

@app.route('/preferences', methods=['GET', 'POST'])
@login_required
def preferences():
    """User preferences page"""
    if request.method == 'POST':
        # Get selected genres
        selected_genres = request.form.getlist('genres')
        
        # Update user preferences
        preferences = json.loads(current_user.preferences or '{}')
        preferences['genres'] = selected_genres
        
        current_user.preferences = json.dumps(preferences)
        db.session.commit()
        
        # Regenerate recommendations
        recommendation_engine.generate_recommendations(current_user.id)
        
        flash('Preferences updated successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    # Get current preferences
    preferences = json.loads(current_user.preferences or '{}')
    selected_genres = preferences.get('genres', [])
    
    # Get a selection of popular genres
    genres = [
        'Fiction', 'Fantasy', 'Science Fiction', 'Mystery', 'Thriller', 
        'Romance', 'Historical Fiction', 'Non-fiction', 'Biography', 
        'Self-help', 'Business', 'Science', 'Poetry', 'Comics', 'Classics'
    ]
    
    return render_template('preferences.html', genres=genres, selected_genres=selected_genres)

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# Initialize database
# Replace this:
# With this:
with app.app_context():
    # Initialize the application
    db.create_all()
    
    # Check if books table is empty
    if Book.query.count() == 0:
        # Download or create sample dataset
        dataset_path = download_goodreads_dataset()
        # Load books into database
        load_books_dataset(dataset_path)

    # Initialize recommendation engine
    recommendation_engine.initialize()
    
    # Initialize chatbot
    chatbot.initialize()
if __name__ == '__main__':
    app.run(debug=True)
