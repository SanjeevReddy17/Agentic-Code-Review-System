from flask import Flask, jsonify
from flask_cors import CORS

from routes.review_routes import review_bp
from database.db import initialize_database

# Create Flask application
app = Flask(__name__)

# Enable frontend-backend communication
CORS(app)

# Initialize SQLite database
initialize_database()

# Register code review routes
app.register_blueprint(review_bp)


# Home route
@app.route("/")
def home():
    return jsonify({
        "project": "Agentic Code Review System",
        "status": "Running Successfully"
    })


# Health check route
@app.route("/health")
def health():
    return jsonify({
        "status": "Healthy",
        "backend": "Active"
    })


# Run Flask application
if __name__ == "__main__":
    app.run(debug=True, port=5000)