import sqlite3
import os

DATABASE_FOLDER = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(DATABASE_FOLDER, "reviews.db")


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    connection = get_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            source_code TEXT NOT NULL,
            syntax_status TEXT,
            code_issues INTEGER DEFAULT 0,
            security_issues INTEGER DEFAULT 0,
            quality_score INTEGER DEFAULT 0,
            ai_review TEXT,
            full_results_json TEXT
        )
    """)

    connection.commit()
    connection.close()

    print("SQLite database initialized successfully!")