# BookSage: AI-Powered Book Recommendation System

BookSage is a comprehensive book recommendation system that uses hybrid filtering techniques and AI to provide personalized book recommendations. Built with Python, Flask, and the Gemini API, it offers content-based and collaborative filtering recommendations along with an intelligent chatbot for discussing books.



## Features

- **Hybrid Recommendation Engine**: Combines content-based and collaborative filtering for better recommendations
- **User Authentication**: Complete user management system with login/signup functionality
- **Personalized Recommendations**: Tailored suggestions based on user preferences and ratings
- **AI-Powered Chatbot**: Discuss books, authors, and get custom recommendations through natural conversation
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Book Search**: Find books by title, author, or genre
- **User Profiles**: Track your reading history and preferences

## Tech Stack

- **Backend**: Python + Flask
- **Database**: SQLAlchemy (SQLite for development, easily upgradable to PostgreSQL)
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **AI Integration**: Google Gemini API for the chatbot
- **Recommendation Algorithms**: TF-IDF, SVD, Cosine Similarity

## Installation

### Prerequisites
- Python 3.8 or higher
- Pip package manager
- Gemini API key (for chatbot functionality)

### Setup

1. Clone the repository:
```
git clone https://github.com/rukkya/recommendations.git
cd recommendations
```

2. Create a virtual environment:
```
python -m venv venv
```

3. Activate the virtual environment:
- On Windows:
```
venv\Scripts\activate
```
- On macOS/Linux:
```
source venv/bin/activate
```

4. Install dependencies:
```
pip install -r requirements.txt
```

5. Create a `.env` file in the project root with:
```
SECRET_KEY=your_secret_key_here
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=sqlite:///book_recommender.db
DEBUG=True
```

6. Initialize the database:
```
python init_db.py
```

7. Run the application:
```
python app.py
```

8. Open your browser and navigate to: `http://127.0.0.1:5000/`

## Usage

### First-time setup
1. Create an account by signing up
2. Complete the onboarding process by selecting your preferred genres and favorite books
3. Explore your personalized recommendations on your dashboard

### Rating Books
- Browse books through search or recommendations
- Rate books on a scale of 1-5 stars
- Add optional reviews for books you've read

### Using the Chatbot
- Navigate to the Book Chat page
- Ask for recommendations based on specific titles, authors, or genres
- Discuss book themes, plot elements, or literary concepts
- Get personalized reading suggestions based on your preferences

## Troubleshooting

### Common Issues

1. **Database initialization fails**
```
mkdir data
python init_db.py
```

2. **Gemini API chatbot errors**
- Check your API key in the `.env` file
- The free tier of Gemini API has rate limits (2 requests/minute)
- Add error handling for API timeouts

3. **Images not displaying**
```
mkdir -p static/img
```

4. **Reset database**
```
rm book_recommender.db
python init_db.py
```

## Customization

### Adding Books
To add more books to the system:
1. Prepare a CSV file with book data
2. Update the `DATASET_PATH` in `config.py`
3. Run `python init_db.py`

### Changing Recommendation Algorithm Parameters
Edit the parameters in `utils/recommendation_engine.py`:
- Adjust weights between content-based and collaborative filtering
- Modify the number of recommendations
- Change similarity thresholds

### Styling
- Edit `static/css/main.css` to customize the appearance
- Update templates in `templates/` directory for layout changes

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.


## Acknowledgements

- Goodreads Books dataset for sample book data
- Google Gemini API for powering the chatbot
- Bootstrap for the responsive UI components

---

Created by [RUKKYA] - [rokiaossama@gmail.com]
