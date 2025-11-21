"""
Database Connection and Session Management

This module handles:
1. Creating the SQLite database engine
2. Managing database sessions
3. Providing database dependency for FastAPI routes

Tech Tip: The 'engine' is the connection to the database.
The 'session' is like a workspace where you make changes before committing.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.models.database import Base
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get database URL from environment variable
# Default to SQLite file in current directory
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./prompt_trainer.db")

# Create database engine
# Tech Tip: The engine is the "connection pool" to the database
# connect_args is needed for SQLite to work with FastAPI (thread safety)
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Required for SQLite
    echo=False  # Set to True to see all SQL queries (useful for debugging)
)

# Session factory
# Tech Tip: A session is like a "shopping cart" - you add/modify things,
# then commit() to save everything at once, or rollback() to cancel
SessionLocal = sessionmaker(
    autocommit=False,  # Don't auto-save changes
    autoflush=False,   # Don't auto-send to database
    bind=engine        # Connect to our database
)


# Dependency for FastAPI routes
# Tech Tip: This is a "dependency injection" function
# FastAPI will call this automatically when you use Depends(get_db)
def get_db():
    """
    Provides a database session to API routes.

    Usage in routes:
        @app.get("/papers")
        def get_papers(db: Session = Depends(get_db)):
            papers = db.query(Paper).all()
            return papers

    The 'try/finally' ensures the session is always closed,
    even if an error occurs.
    """
    db = SessionLocal()
    try:
        yield db  # Give the session to the route
    finally:
        db.close()  # Always close when done


# Initialize database (create all tables)
def init_db():
    """
    Creates all database tables defined in models.

    Tech Tip: This reads all the classes in database.py
    and creates corresponding tables if they don't exist.

    Tables created:
    - papers
    - rubrics
    - criteria
    - prompts
    - evaluations
    - feedback_entries
    """
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")


# Helper function to drop all tables (useful for testing/development)
def drop_all_tables():
    """
    WARNING: Deletes ALL data!
    Only use during development for fresh starts.
    """
    Base.metadata.drop_all(bind=engine)
    print("⚠️  All database tables dropped")


# Tech Tip: Why use sessions?
#
# Without sessions, every database operation is separate:
#   CREATE paper
#   CREATE evaluation
#   Oops! Error! But paper already created...
#
# With sessions, everything is transactional:
#   session.add(paper)
#   session.add(evaluation)
#   session.commit()  # Both saved together, or both fail
#
# This prevents partial saves and data corruption!
