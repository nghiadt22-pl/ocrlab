import os
import sys
from datetime import date
from sqlalchemy.exc import SQLAlchemyError

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.connection import get_db_session
from database.models import User, Folder, File, UsageStat
from database import crud

def test_database_connection():
    """Test database connection and basic operations."""
    try:
        # Get a session
        db = get_db_session()
        
        print("Connected to the database!")
        
        # Test operations
        print("\n=== Testing User Operations ===")
        test_user_operations(db)
        
        print("\n=== Testing Folder Operations ===")
        test_folder_operations(db)
        
        print("\n=== Testing File Operations ===")
        test_file_operations(db)
        
        print("\n=== Testing Usage Stats Operations ===")
        test_usage_stats_operations(db)
        
        print("\nAll tests completed successfully!")
        
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'db' in locals():
            db.close()

def test_user_operations(db):
    """Test user CRUD operations."""
    # Get or create a test user
    test_email = "test@example.com"
    test_user_id = "test_user_123"
    
    user = crud.get_user_by_email(db, test_email)
    if not user:
        print(f"Creating user {test_email}...")
        user = crud.create_user(db, test_user_id, test_email)
        print(f"Created user with ID {user.id}")
    else:
        print(f"Found existing user {user.email} with ID {user.id}")
    
    # Update user settings
    test_settings = {"theme": "dark", "notifications": True}
    user = crud.update_user_settings(db, user.id, test_settings)
    print(f"Updated user settings: {user.settings}")

def test_folder_operations(db):
    """Test folder CRUD operations."""
    # Get a user for testing
    user = crud.get_user_by_email(db, "test@example.com")
    if not user:
        print("No test user found. Please run the user operations test first.")
        return
    
    # Check for existing root folder or create a new one
    root_folder_name = "Test Root Folder"
    root_folders = crud.get_folders_by_user(db, user.id)
    
    if root_folders:
        print(f"Found existing root folder with ID {root_folders[0].id}")
        root_folder = root_folders[0]
    else:
        print(f"Creating root folder '{root_folder_name}'...")
        root_folder = crud.create_folder(db, root_folder_name, user.id)
        print(f"Created root folder with ID {root_folder.id}")
    
    # Check for existing subfolder or create a new one
    subfolder_name = "Test Subfolder"
    subfolders = crud.get_folders_by_user(db, user.id, root_folder.id)
    
    if subfolders:
        print(f"Found existing subfolder with ID {subfolders[0].id}")
        subfolder = subfolders[0]
    else:
        print(f"Creating subfolder '{subfolder_name}'...")
        subfolder = crud.create_folder(db, subfolder_name, user.id, root_folder.id)
        print(f"Created subfolder with ID {subfolder.id}")
    
    # Get folders by user and parent
    root_folders = crud.get_folders_by_user(db, user.id)
    print(f"Found {len(root_folders)} root folders")
    
    subfolders = crud.get_folders_by_user(db, user.id, root_folder.id)
    print(f"Found {len(subfolders)} subfolders in root folder")
    
    # Update folder name
    updated_subfolder_name = "Updated Subfolder"
    print(f"Renaming subfolder to '{updated_subfolder_name}'...")
    subfolder = crud.update_folder(db, subfolder.id, updated_subfolder_name)
    print(f"Updated subfolder name to '{subfolder.name}'")
    
    # Delete subfolder (we'll keep the root folder for file tests)
    print(f"Deleting subfolder {subfolder.id}...")
    deleted = crud.delete_folder(db, subfolder.id)
    print(f"Subfolder deleted: {deleted}")

def test_file_operations(db):
    """Test file CRUD operations."""
    # Get a user for testing
    user = crud.get_user_by_email(db, "test@example.com")
    if not user:
        print("No test user found. Please run the user operations test first.")
        return
    
    # Find the root folder
    root_folders = crud.get_folders_by_user(db, user.id)
    if not root_folders:
        print("No root folder found. Please run the folder operations test first.")
        return
    
    root_folder = root_folders[0]
    
    # File test parameters
    test_file_name = "test_document.pdf"
    test_blob_path = "test-container/test_document.pdf"
    test_size = 1024 * 1024  # 1MB
    test_mime_type = "application/pdf"
    
    # Check for existing file
    existing_files = crud.get_files_by_folder(db, root_folder.id, user.id)
    if existing_files:
        print(f"Found existing file with ID {existing_files[0].id}")
        file = existing_files[0]
    else:
        print(f"Creating file '{test_file_name}'...")
        file = crud.create_file(
            db, 
            test_file_name, 
            user.id, 
            test_blob_path,
            test_size,
            test_mime_type,
            root_folder.id
        )
        print(f"Created file with ID {file.id}")
    
    # Get files by folder
    folder_files = crud.get_files_by_folder(db, root_folder.id, user.id)
    print(f"Found {len(folder_files)} files in folder")
    
    # Get files by status
    queued_files = crud.get_files_by_status(db, "queued")
    print(f"Found {len(queued_files)} queued files")
    
    # Update file status
    print("Updating file status to 'processing'...")
    file = crud.update_file_status(db, file.id, "processing")
    print(f"Updated file status to '{file.status}'")
    
    print("Updating file status to 'completed' with metadata...")
    test_metadata = {
        "page_count": 5,
        "text_content": "Sample extracted text",
        "languages": ["en"],
        "confidence": 0.95
    }
    file = crud.update_file_status(db, file.id, "completed", test_metadata)
    print(f"Updated file status to '{file.status}' with metadata")
    
    # Delete file
    print(f"Deleting file {file.id}...")
    deleted = crud.delete_file(db, file.id)
    print(f"File deleted: {deleted}")
    
    # Delete the test root folder
    print(f"Deleting root folder {root_folder.id}...")
    deleted = crud.delete_folder(db, root_folder.id)
    print(f"Root folder deleted: {deleted}")

def test_usage_stats_operations(db):
    """Test usage statistics operations."""
    # Get a user for testing
    user = crud.get_user_by_email(db, "test@example.com")
    if not user:
        print("No test user found. Please run the user operations test first.")
        return
    
    # Get or create usage stat for today
    today = date.today()
    print(f"Getting or creating usage stats for {today}...")
    usage_stat = crud.get_or_create_usage_stat(db, user.id)
    print(f"Got usage stat with ID {usage_stat.id}")
    
    # Update pages processed
    print("Updating pages processed...")
    pages_to_add = 10
    usage_stat = crud.update_pages_processed(db, user.id, pages_to_add)
    print(f"Pages processed: {usage_stat.pages_processed}")
    
    # Update queries made
    print("Updating queries made...")
    queries_to_add = 5
    usage_stat = crud.update_queries_made(db, user.id, queries_to_add)
    print(f"Queries made: {usage_stat.queries_made}")
    
    # Update storage bytes
    print("Updating storage bytes...")
    bytes_to_add = 2 * 1024 * 1024  # 2MB
    usage_stat = crud.update_storage_bytes(db, user.id, bytes_to_add)
    print(f"Storage bytes: {usage_stat.storage_bytes}")
    
    # Get usage stats for a date range
    start_date = date(today.year, today.month, 1)  # First day of the month
    end_date = today
    print(f"Getting usage stats from {start_date} to {end_date}...")
    stats = crud.get_usage_stats_by_user(db, user.id, start_date, end_date)
    print(f"Found {len(stats)} usage stat records")

if __name__ == "__main__":
    test_database_connection() 