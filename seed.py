from app import create_app
from models import db, Book

app = create_app()

def seed_database():
    with app.app_context():
        # Check if books already exist
        if Book.query.count() == 0:
            book1 = Book(
                title="The History of the Web",
                author="Tim Berners-Lee",
                content="This is the simplified text of the first book. It is designed to be easy to read for testing the dyslexia features. The web was created to share information.",
                source="public"
            )
            book2 = Book(
                title="Understanding AI",
                author="Alan Turing",
                content="Artificial intelligence is the simulation of human intelligence processes by machines. These processes include learning, reasoning, and self-correction.",
                source="public"
            )
            
            db.session.add_all([book1, book2])
            db.session.commit()
            print("Successfully added test books to the database!")
        else:
            print("Database already has books. Skipping seed.")

if __name__ == "__main__":
    seed_database()