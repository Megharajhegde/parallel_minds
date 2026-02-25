from flask import Flask
from flask_cors import CORS
from config import Config
from models import db
from routes import api

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Enable CORS for vanilla JS frontend integration
    CORS(app)
    
    # Initialize SQLAlchemy with app
    db.init_app(app)
    
    # Register API blueprint
    app.register_blueprint(api, url_prefix='/api')

    # Create tables automatically on startup if they don't exist
    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)