import os
import pdfplumber
from app import create_app
from models import db, Book

app = create_app()

def import_local_pdfs(folder_name):
    base_dir = os.path.abspath(os.path.dirname(__file__))
    folder_path = os.path.join(base_dir, folder_name)

    with app.app_context():
        if not os.path.exists(folder_path):
            print(f"Error: The folder '{folder_path}' does not exist.")
            return

        print(f"Scanning '{folder_name}' for PDFs...\n")
        
        for filename in os.listdir(folder_path):
            if filename.endswith('.pdf'):
                filepath = os.path.join(folder_path, filename)
                print(f"Processing: {filename}")
                
                try:
                    extracted_text = ""
                    author_name = "Unknown Author" # Default fallback
                    
                    # 1. Open the PDF with pdfplumber
                    with pdfplumber.open(filepath) as pdf:
                        
                        # --- NEW: Extract Metadata ---
                        if pdf.metadata:
                            # Safely try to get the Author from the PDF properties
                            meta_author = pdf.metadata.get('Author')
                            # Ensure it exists and isn't just empty spaces
                            if meta_author and str(meta_author).strip():
                                author_name = str(meta_author).strip()
                        
                        # Extract text from the first 20 pages
                        for page in pdf.pages[:20]: 
                            text = page.extract_text(x_tolerance=4.0, y_tolerance=3.0)
                            if text:
                                extracted_text += text + "\n"
                                
                    if not extracted_text.strip():
                        print(f"  -> Skipping: Could not find readable text in {filename}")
                        continue

                    # 3. Sanitize text for SQLite
                    clean_extracted_text = extracted_text.encode('utf-8', 'ignore').decode('utf-8')
                    clean_title = filename.replace('.pdf', '').replace('_', ' ').replace('-', ' ')

                    # 4. Save to database using the extracted author
                    new_book = Book(
                        title=clean_title,
                        author=author_name, # <--- Updated this line!
                        content=clean_extracted_text, 
                        source="public" 
                    )
                    
                    db.session.add(new_book)
                    db.session.commit() 
                    print(f"  -> Success: Added '{clean_title}' by {author_name} to the library.")

                except Exception as e:
                    db.session.rollback()
                    print(f"  -> Error processing {filename}: {str(e)}")
                    
        print("\nBatch import complete!")

if __name__ == '__main__':
    import_local_pdfs('seed_books')