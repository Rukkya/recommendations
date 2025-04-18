from datetime import datetime
from . import db

class Recommendation(db.Model):
    __tablename__ = 'recommendations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))
    score = db.Column(db.Float, nullable=False)  # Recommendation score
    source = db.Column(db.String(50))  # 'content', 'collaborative', 'hybrid'
    has_viewed = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    book = db.relationship('Book')
    
    def __init__(self, user_id, book_id, score, source='hybrid'):
        self.user_id = user_id
        self.book_id = book_id
        self.score = score
        self.source = source
    
    def __repr__(self):
        return f'<Recommendation score={self.score} for book_id={self.book_id} to user_id={self.user_id}>'
