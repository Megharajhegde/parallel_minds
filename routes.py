from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from PyPDF2 import PdfReader
from models import db, User, Book, Preference, Bookmark
import os
from google import genai
import os
import pdfplumber
from dotenv import load_dotenv
load_dotenv()

api = Blueprint('api', __name__)
import os
import tempfile
import traceback
import pdfplumber
from flask import request, jsonify
from models import db, Book

@api.route('/upload', methods=['POST'])
def upload_pdf():
    # 1. Security Check
    user_id = request.form.get('user_id')
    if not user_id or user_id == "null":
        return jsonify({'error': 'Authentication required to upload books.'}), 401

    if 'file' not in request.files:
        return jsonify({'error': 'No file part provided'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    clean_filename = file.filename.replace('.pdf', '').replace('_', ' ').replace('-', ' ')
    title = request.form.get('title', clean_filename)
    author = "Unknown Author" # Default fallback

    if file and file.filename.endswith('.pdf'):
        try:
            extracted_text = ""
            
            # 2. Secure temporary physical file creation
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
                file.save(temp_pdf.name)
                temp_pdf_path = temp_pdf.name

            try:
                # 3. Open the REAL file with pdfplumber
                with pdfplumber.open(temp_pdf_path) as pdf:
                    
                    # Grab Metadata if it exists
                    if pdf.metadata:
                        meta_author = pdf.metadata.get('Author')
                        if meta_author and str(meta_author).strip():
                            author = str(meta_author).strip()

                    # Extract text safely (limited to 20 pages for speed in hackathon)
                    max_pages = min(20, len(pdf.pages))
                    for page in pdf.pages[:max_pages]:
                        text = page.extract_text(x_tolerance=4.0, y_tolerance=3.0)
                        if text:
                            extracted_text += text + "\n"
            finally:
                # 4. ALWAYS delete the temp file when done to save server memory!
                if os.path.exists(temp_pdf_path):
                    os.remove(temp_pdf_path)

            if not extracted_text.strip():
                return jsonify({'error': 'Could not extract text from PDF.'}), 400

            # 5. Save to Database
            new_book = Book(
                title=title,
                author=author,
                content=extracted_text,
                source="uploaded",
                uploaded_by=user_id
            )
            db.session.add(new_book)
            db.session.commit()

            return jsonify({'message': 'Book uploaded successfully', 'book_id': new_book.id}), 201

        except Exception as e:
            # Print the exact error to the terminal so we can see it without crashing the server
            traceback.print_exc() 
            return jsonify({'error': 'Failed to process PDF on the server.'}), 500
            
    return jsonify({'error': 'Invalid file type. Please upload a PDF.'}), 400

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



@api.route('/summarize', methods=['POST'])
def summarize_text():
    data = request.get_json()
    text_to_summarize = data.get('text')

    if not text_to_summarize:
        return jsonify({'error': 'No text provided'}), 400

    # It's best practice to keep API keys in environment variables
    
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    api_key =GEMINI_API_KEY
    if not api_key:
        return jsonify({'error': 'Gemini API key not configured on server'}), 500

    try:
        # Initialize the Gemini client
        client = genai.Client(api_key=api_key)
        
        # Create a prompt tailored for dyslexic readers
        prompt = f"Please provide a clear, concise, and easy-to-understand summary of the following text. Use simple language suitable for a reader who may have dyslexia. Here is the text:\n\n{text_to_summarize}"
        
        # Call the Gemini 2.5 Flash model (it is extremely fast for this use case)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        
        return jsonify({'summary': response.text}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500