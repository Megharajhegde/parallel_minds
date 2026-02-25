from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    mode = db.Column(db.String(20), default="normal") # "normal" or "dyslexia"
    
    # Relationships
    preferences = db.relationship('Preference', backref='user', uselist=False, cascade="all, delete-orphan")
    books_uploaded = db.relationship('Book', backref='uploader', lazy=True)
    bookmarks = db.relationship('Bookmark', backref='user', lazy=True)

class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=True)
    content = db.Column(db.Text, nullable=False)
    source = db.Column(db.String(50), default="public") # "public" or "uploaded"
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

class Preference(db.Model):
    __tablename__ = 'preferences'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    font_size = db.Column(db.Integer, default=16)
    line_spacing = db.Column(db.Float, default=1.5)
    letter_spacing = db.Column(db.Float, default=0.0)
    background_color = db.Column(db.String(20), default="white")

class Bookmark(db.Model):
    __tablename__ = 'bookmarks'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    position = db.Column(db.Integer, default=0) # Character index or page number