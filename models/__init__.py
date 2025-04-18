from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def init_app(app):
    db.init_app(app)
    login_manager.init_app(app)
    
    # Import models to ensure they are registered with SQLAlchemy
    from .user import User
    from .book import Book
    from .rating import Rating
    from .recommendation import Recommendation
    
    # Create a user loader function
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
