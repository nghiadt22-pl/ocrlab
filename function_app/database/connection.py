import os
import urllib.parse
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection details
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_PORT = os.getenv('DB_PORT')
DB_DATABASE = os.getenv('DB_DATABASE')

# URL encode the password to handle special characters
ENCODED_PASSWORD = urllib.parse.quote_plus(DB_PASSWORD)

# Create database URL
DATABASE_URL = f"postgresql://{DB_USER}:{ENCODED_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"

# Create engine
engine = create_engine(DATABASE_URL, pool_size=5, max_overflow=10)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create scoped session for thread safety
db_session = scoped_session(SessionLocal)

# Function to get a database session
def get_db():
    """
    Get a database session.
    
    Returns:
        sqlalchemy.orm.Session: Database session
    """
    db = db_session()
    try:
        yield db
    finally:
        db.close()

# Function to get a database session for non-generator contexts
def get_db_session():
    """
    Get a database session for non-generator contexts.
    
    Returns:
        sqlalchemy.orm.Session: Database session
    """
    return db_session() 