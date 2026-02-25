from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from PyPDF2 import PdfReader
from models import db, User, Book, Preference, Bookmark

api = Blueprint('api', __name__)

@api.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password') or not data.get('name'):
        return jsonify({'error': 'Missing required fields'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 409

    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    
    new_user = User(
        name=data['name'],
        email=data['email'],
        password_hash=hashed_password,
        mode="normal"
    )
    db.session.add(new_user)
    db.session.flush() # Get the new_user.id before committing

    # Create default preferences for the new user
    default_prefs = Preference(user_id=new_user.id)
    db.session.add(default_prefs)
    
    db.session.commit()
    
    return jsonify({
        'message': 'User registered successfully',
        'user': {'id': new_user.id, 'name': new_user.name, 'email': new_user.email}
    }), 201

@api.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Missing email or password'}), 400

    user = User.query.filter_by(email=data['email']).first()
    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401

    return jsonify({
        'message': 'Login successful',
        'user': {
            'id': user.id, 
            'name': user.name, 
            'email': user.email, 
            'mode': user.mode
        }
    }), 200

@api.route('/books', methods=['GET'])
def get_books():
    # Allow filtering by user_id to see public + user's uploaded books
    user_id = request.args.get('user_id', type=int)
    
    if user_id:
        books = Book.query.filter((Book.source == 'public') | (Book.uploaded_by == user_id)).all()
    else:
        books = Book.query.filter_by(source='public').all()

    books_data = [{'id': b.id, 'title': b.title, 'author': b.author, 'source': b.source} for b in books]
    return jsonify({'books': books_data}), 200

@api.route('/books/<int:id>', methods=['GET'])
def get_book(id):
    book = Book.query.get(id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404

    return jsonify({
        'id': book.id,
        'title': book.title,
        'author': book.author,
        'content': book.content,
        'source': book.source
    }), 200

@api.route('/upload', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part provided'}), 400
        
    file = request.files['file']
    user_id = request.form.get('user_id')
    title = request.form.get('title', 'Unknown Title')
    author = request.form.get('author', 'Unknown Author')

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if not user_id or not User.query.get(user_id):
        return jsonify({'error': 'Valid user_id required'}), 400

    if file and file.filename.endswith('.pdf'):
        try:
            # Extract text in-memory directly from the file stream
            reader = PdfReader(file.stream)
            extracted_text = ""
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    extracted_text += text + "\n"

            if not extracted_text.strip():
                return jsonify({'error': 'Could not extract text from PDF or PDF is empty'}), 400

            new_book = Book(
                title=title,
                author=author,
                content=extracted_text,
                source="uploaded",
                uploaded_by=user_id
            )
            db.session.add(new_book)
            db.session.commit()

            return jsonify({'message': 'Book uploaded and processed successfully', 'book_id': new_book.id}), 201

        except Exception as e:
            return jsonify({'error': f'Failed to process PDF: {str(e)}'}), 500
            
    return jsonify({'error': 'Invalid file type. Only PDFs are allowed.'}), 400

@api.route('/mode/<int:user_id>', methods=['PUT'])
def update_mode(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()
    new_mode = data.get('mode')
    
    if new_mode not in ['normal', 'dyslexia']:
        return jsonify({'error': 'Invalid mode. Use normal or dyslexia'}), 400

    user.mode = new_mode
    db.session.commit()
    return jsonify({'message': f'Reading mode updated to {new_mode}'}), 200

@api.route('/preferences/<int:user_id>', methods=['PUT'])
def update_preferences(user_id):
    prefs = Preference.query.filter_by(user_id=user_id).first()
    if not prefs:
        return jsonify({'error': 'Preferences not found for this user'}), 404

    data = request.get_json()
    
    # Update fields if provided
    if 'font_size' in data: prefs.font_size = data['font_size']
    if 'line_spacing' in data: prefs.line_spacing = data['line_spacing']
    if 'letter_spacing' in data: prefs.letter_spacing = data['letter_spacing']
    if 'background_color' in data: prefs.background_color = data['background_color']

    db.session.commit()
    return jsonify({'message': 'Preferences updated successfully'}), 200

@api.route('/bookmark', methods=['POST'])
def add_bookmark():
    data = request.get_json()
    if not data or not data.get('user_id') or not data.get('book_id') or 'position' not in data:
        return jsonify({'error': 'Missing required fields'}), 400

    # Check if bookmark already exists to update it, otherwise create new
    bookmark = Bookmark.query.filter_by(user_id=data['user_id'], book_id=data['book_id']).first()
    
    if bookmark:
        bookmark.position = data['position']
        msg = 'Bookmark updated'
    else:
        bookmark = Bookmark(
            user_id=data['user_id'],
            book_id=data['book_id'],
            position=data['position']
        )
        db.session.add(bookmark)
        msg = 'Bookmark created'

    db.session.commit()
    return jsonify({'message': msg, 'bookmark_id': bookmark.id}), 200