from datetime import datetime
from . import db

class Rating(db.Model):
    __tablename__ = 'ratings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))
    rating = db.Column(db.Float, nullable=False)  # 1-5 star rating
    review = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, user_id, book_id, rating, review=None):
        self.user_id = user_id
        self.book_id = book_id
        self.rating = rating
        self.review = review
    
    def __repr__(self):
        return f'<Rating {self.rating} for book_id={self.book_id} by user_id={self.user_id}>'
