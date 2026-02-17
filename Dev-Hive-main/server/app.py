from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Register blueprints
from routes.ingest import ingest_bp
from routes.search import search_bp
from routes.ask import ask_bp
from routes.health import health_bp
from routes.integrations import integrations_bp
from routes.activities import activities_bp
from routes.flashcards import flashcards_bp
from routes.tokens import tokens_bp

app.register_blueprint(ingest_bp)
app.register_blueprint(search_bp)
app.register_blueprint(ask_bp)
app.register_blueprint(health_bp)
app.register_blueprint(integrations_bp)
app.register_blueprint(activities_bp)
app.register_blueprint(flashcards_bp)
app.register_blueprint(tokens_bp)

if __name__ == "__main__":
    app.run(debug=True)
