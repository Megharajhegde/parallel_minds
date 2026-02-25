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
                    # 1. Read the PDF file
                    reader = PdfReader(filepath)
                    extracted_text = ""
                    
                    for page in reader.pages:
                        text = page.extract_text()
                        if text:
                            extracted_text += text + "\n"
                            
                    if not extracted_text.strip():
                        print(f"  -> Skipping: Could not find readable text in {filename}")
                        continue

                    # --- THE FIXES ARE HERE ---
                    # Clean the text: Encode to utf-8 and ignore/drop any corrupted surrogate characters
                    clean_extracted_text = extracted_text.encode('utf-8', 'ignore').decode('utf-8')

                    # Clean up the title
                    clean_title = filename.replace('.pdf', '').replace('_', ' ').replace('-', ' ')

                    # Save to database
                    new_book = Book(
                        title=clean_title,
                        author="Unknown Author",
                        content=clean_extracted_text, # Use the sanitized text
                        source="public" 
                    )
                    
                    db.session.add(new_book)
                    # Commit IMMEDIATELY inside the loop so one bad book doesn't crash the batch
                    db.session.commit() 
                    print(f"  -> Success: Added '{clean_title}' to the library.")

                except Exception as e:
                    # If this specific book fails, rollback the error and keep going!
                    db.session.rollback()
                    print(f"  -> Error processing {filename}: {str(e)}")
                    
        print("\nBatch import complete!")

if __name__ == '__main__':
    import_local_pdfs('seed_books')