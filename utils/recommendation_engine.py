import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
import json
from datetime import datetime

from models import db
from models.book import Book
from models.rating import Rating
from models.recommendation import Recommendation
from models.user import User

class RecommendationEngine:
    def __init__(self):
        self.content_based_matrix = None
        self.collaborative_matrix = None
        self.book_indices = None
        self.user_indices = None
        self.is_initialized = False
    
    def initialize(self):
        """Initialize the recommendation engine with data from the database"""
        self._build_content_based_matrix()
        self._build_collaborative_matrix()
        self.is_initialized = True
        
    def _build_content_based_matrix(self):
        """Build the content-based similarity matrix using TF-IDF"""
        # Get all books from the database
        books = Book.query.all()
        
        # Create a DataFrame with book information
        book_data = []
        for book in books:
            # Combine title, author, description, genres for TF-IDF
            combined_features = f"{book.title} {book.author or ''} {book.description or ''} {book.genres or ''}"
            book_data.append({
                'id': book.id,
                'combined_features': combined_features
            })
        
        if not book_data:
            return
            
        df = pd.DataFrame(book_data)
        
        # Create TF-IDF matrix
        tfidf = TfidfVectorizer(stop_words='english')
        tfidf_matrix = tfidf.fit_transform(df['combined_features'])
        
        # Calculate cosine similarity matrix
        self.content_based_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)
        
        # Create a Series mapping book indices to book IDs
        self.book_indices = pd.Series(df.index, index=df['id'])
    
    def _build_collaborative_matrix(self):
        """Build collaborative filtering matrix using SVD"""
        # Get all ratings from database
        ratings = Rating.query.all()
        
        if not ratings:
            self.collaborative_matrix = None
            return
            
        # Build user-item matrix
        ratings_data = [(r.user_id, r.book_id, r.rating) for r in ratings]
        ratings_df = pd.DataFrame(ratings_data, columns=['user_id', 'book_id', 'rating'])
        
        # Check if we have enough distinct books and users
        distinct_users = ratings_df['user_id'].nunique()
        distinct_books = ratings_df['book_id'].nunique()
        
        if distinct_users < 2 or distinct_books < 2:
            # Not enough data for collaborative filtering
            self.collaborative_matrix = None
            return
        
        # Create user-item matrix
        user_item_matrix = ratings_df.pivot_table(
            index='user_id', 
            columns='book_id', 
            values='rating', 
            fill_value=0
        )
        
        # Check if the matrix shape is sufficient for SVD
        if min(user_item_matrix.shape) < 2:
            self.collaborative_matrix = None
            return
        
        # Save indices mapping
        self.user_indices = {user_id: i for i, user_id in enumerate(user_item_matrix.index)}
        
        # Apply SVD for dimensionality reduction
        # Ensure at least 1 component
        n_components = max(1, min(50, min(user_item_matrix.shape) - 1))
        svd = TruncatedSVD(n_components=n_components)
        
        try:
            latent_matrix = svd.fit_transform(user_item_matrix)
            # Calculate similarity between users in the latent space
            self.collaborative_matrix = cosine_similarity(latent_matrix)
        except Exception as e:
            print(f"Error in collaborative filtering: {e}")
            self.collaborative_matrix = None
        
    def get_content_based_recommendations(self, book_id, top_n=10):
        """Get content-based recommendations based on a book"""
        if not self.is_initialized or self.content_based_matrix is None:
            return []
            
        # Check if book_id exists in our matrix
        if book_id not in self.book_indices:
            return []
            
        # Get the book index
        idx = self.book_indices[book_id]
        
        # Get similarity scores for all books
        sim_scores = list(enumerate(self.content_based_matrix[idx]))
        
        # Sort based on similarity scores
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        
        # Get top N similar books (excluding the book itself)
        sim_scores = sim_scores[1:top_n+1]
        
        # Get book indices
        book_indices = [i[0] for i in sim_scores]
        
        # Return results as (book_id, similarity_score) tuples
        result = []
        book_ids = self.book_indices.index.tolist()
        for idx, score in zip(book_indices, [i[1] for i in sim_scores]):
            if idx < len(book_ids):
                result.append((book_ids[idx], float(score)))
        
        return result
    
    def get_user_based_recommendations(self, user_id, top_n=10):
        """Get collaborative filtering recommendations based on user similarity"""
        if not self.is_initialized or self.collaborative_matrix is None:
            return []
            
        # Check if user exists in our matrix
        if user_id not in self.user_indices:
            return []
            
        # Get user's index
        user_idx = self.user_indices[user_id]
        
        # Get similar users
        sim_users = list(enumerate(self.collaborative_matrix[user_idx]))
        sim_users = sorted(sim_users, key=lambda x: x[1], reverse=True)
        
        # Get top similar users (excluding the user itself)
        sim_users = sim_users[1:6]  # Use top 5 similar users
        
        # Get user IDs of similar users
        user_ids_list = list(self.user_indices.keys())
        similar_user_ids = [user_ids_list[i[0]] for i in sim_users if i[0] < len(user_ids_list)]
        
        # Get books rated highly by similar users
        rated_books = {}
        for sim_user_id in similar_user_ids:
            # Get highly rated books (rating > 3.5) from this similar user
            high_ratings = Rating.query.filter_by(user_id=sim_user_id).filter(Rating.rating > 3.5).all()
            
            for rating in high_ratings:
                # Skip books the user has already rated
                user_rated = Rating.query.filter_by(user_id=user_id, book_id=rating.book_id).first()
                if user_rated:
                    continue
                    
                if rating.book_id not in rated_books:
                    rated_books[rating.book_id] = 0
                
                # Add weighted rating (weighted by user similarity)
                user_sim = sim_users[similar_user_ids.index(sim_user_id)][1]
                rated_books[rating.book_id] += rating.rating * user_sim
        
        # Sort books by weighted scores
        recommended_books = sorted(rated_books.items(), key=lambda x: x[1], reverse=True)
        
        # Return top N recommendations
        return recommended_books[:top_n]
    
    def get_hybrid_recommendations(self, user_id, top_n=10):
        """Get hybrid recommendations combining content and collaborative approaches"""
        # Get user's rated books
        user_ratings = Rating.query.filter_by(user_id=user_id).all()
        
        if not user_ratings:
            # If user has no ratings, return popular books
            popular_books = Book.query.order_by(Book.average_rating.desc()).limit(top_n).all()
            return [(book.id, book.average_rating/5.0) for book in popular_books]
        
        content_recs = []
        # For each book the user has rated highly, get content-based recommendations
        for rating in user_ratings:
            if rating.rating >= 4.0:  # Only use books rated 4 or higher
                book_recs = self.get_content_based_recommendations(rating.book_id, top_n=5)
                content_recs.extend(book_recs)
        
        # Get collaborative recommendations
        collab_recs = self.get_user_based_recommendations(user_id, top_n=10)
        
        # Combine both recommendation sets
        # Weight content more if the user has few ratings, otherwise weight collaborative more
        if len(user_ratings) < 5:
            content_weight = 0.7
            collab_weight = 0.3
        else:
            content_weight = 0.3
            collab_weight = 0.7
        
        # Combine and normalize scores
        combined_recs = {}
        
        # Add content-based recommendations
        for book_id, score in content_recs:
            if book_id not in combined_recs:
                combined_recs[book_id] = 0
            combined_recs[book_id] += score * content_weight
        
        # Add collaborative recommendations
        for book_id, score in collab_recs:
            if book_id not in combined_recs:
                combined_recs[book_id] = 0
            combined_recs[book_id] += score * collab_weight
        
        # Sort and get top recommendations
        final_recs = sorted(combined_recs.items(), key=lambda x: x[1], reverse=True)
        
        # Filter out books the user has already rated
        rated_book_ids = {rating.book_id for rating in user_ratings}
        final_recs = [(book_id, score) for book_id, score in final_recs if book_id not in rated_book_ids]
        
        return final_recs[:top_n]
    
    def generate_recommendations(self, user_id, max_recommendations=20):
        """Generate and store recommendations for a user"""
        if not self.is_initialized:
            self.initialize()
            
        # Get hybrid recommendations
        recommendations = self.get_hybrid_recommendations(user_id, top_n=max_recommendations)
        
        # Delete existing recommendations
        Recommendation.query.filter_by(user_id=user_id).delete()
        
        # Store new recommendations
        for book_id, score in recommendations:
            recommendation = Recommendation(
                user_id=user_id,
                book_id=book_id,
                score=score,
                source='hybrid'
            )
            db.session.add(recommendation)
        
        db.session.commit()
        
        return len(recommendations)
    
    def update_user_preferences(self, user_id, preferences):
        """Update user preferences and regenerate recommendations"""
        user = User.query.get(user_id)
        if user:
            user.preferences = json.dumps(preferences)
            db.session.commit()
            
            # Regenerate recommendations
            return self.generate_recommendations(user_id)
        
        return 0
