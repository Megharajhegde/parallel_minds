import os
from PyPDF2 import PdfReader
from app import create_app
from models import db, Book

app = create_app()

def import_local_pdfs(folder_name):
    # Get the absolute path to the folder
    base_dir = os.path.abspath(os.path.dirname(__file__))
    folder_path = os.path.join(base_dir, folder_name)

    with app.app_context():
        if not os.path.exists(folder_path):
            print(f"Error: The folder '{folder_path}' does not exist.")
            return

        print(f"Scanning '{folder_name}' for PDFs...\n")
        
        # Loop through all files in the directory
        for filename in os.listdir(folder_path):
            if filename.endswith('.pdf'):
                filepath = os.path.join(folder_path, filename)
                print(f"Processing: {filename}")
                
                try:
                    # 1. Read the PDF file from the local hard drive
                    reader = PdfReader(filepath)
                    extracted_text = ""
                    
                    for page in reader.pages:
                        text = page.extract_text()
                        if text:
                            extracted_text += text + "\n"
                            
                    if not extracted_text.strip():
                        print(f"  -> Skipping: Could not find readable text in {filename}")
                        continue

                    # 2. Clean up the title (remove '.pdf' and replace underscores with spaces)
                    clean_title = filename.replace('.pdf', '').replace('_', ' ')

                    # 3. Save it to the database as a public book
                    new_book = Book(
                        title=clean_title,
                        author="Unknown Author", # You can update these manually in the DB later
                        content=extracted_text,
                        source="public" 
                    )
                    
                    db.session.add(new_book)
                    print(f"  -> Success: Added '{clean_title}' to the library.")

                except Exception as e:
                    print(f"  -> Error processing {filename}: {str(e)}")
                    
        # 4. Commit all the new books to the database at once
        db.session.commit()
        print("\nBatch import complete! All books are now in the database.")

if __name__ == '__main__':
    # Pass the name of the folder you created in Step 1
    import_local_pdfs('seed_books')