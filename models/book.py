from . import db

class Book(db.Model):
    __tablename__ = 'books'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255))
    year = db.Column(db.Integer)
    isbn = db.Column(db.String(20), unique=True, index=True)
    description = db.Column(db.Text)
    genres = db.Column(db.String(255))  # Comma-separated genre tags
    image_url = db.Column(db.String(512))
    language = db.Column(db.String(50))
    average_rating = db.Column(db.Float, default=0.0)
    ratings_count = db.Column(db.Integer, default=0)
    
    # Relationships
    ratings = db.relationship('Rating', backref='book', lazy='dynamic')
    
    def __init__(self, title, author=None, year=None, isbn=None, description=None, 
                 genres=None, image_url=None, language=None):
        self.title = title
        self.author = author
        self.year = year
        self.isbn = isbn
        self.description = description
        self.genres = genres
        self.image_url = image_url
        self.language = language
    
    def update_average_rating(self):
        ratings = [r.rating for r in self.ratings.all()]
        if ratings:
            self.average_rating = sum(ratings) / len(ratings)
            self.ratings_count = len(ratings)
    
    def __repr__(self):
        return f'<Book {self.title} by {self.author}>'
