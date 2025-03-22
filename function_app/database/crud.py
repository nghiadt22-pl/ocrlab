from datetime import date, datetime
from typing import List, Optional, Dict, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, text

from .models import User, Folder, File, UsageStat

# User CRUD operations
def create_user(db: Session, user_id: str, email: str) -> User:
    """
    Create a new user in the database.
    
    Args:
        db: Database session
        user_id: User ID from Clerk
        email: User email
        
    Returns:
        Created user instance
    """
    db_user = User(id=user_id, email=email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: str) -> Optional[User]:
    """
    Get a user by ID.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        User if found, None otherwise
    """
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Get a user by email.
    
    Args:
        db: Database session
        email: User email
        
    Returns:
        User if found, None otherwise
    """
    return db.query(User).filter(User.email == email).first()

def update_user_settings(db: Session, user_id: str, settings: Dict[str, Any]) -> Optional[User]:
    """
    Update user settings.
    
    Args:
        db: Database session
        user_id: User ID
        settings: User settings dictionary
        
    Returns:
        Updated user if found, None otherwise
    """
    db_user = get_user(db, user_id)
    if db_user:
        db_user.settings = settings
        db_user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_user)
    return db_user

# Folder CRUD operations
def create_folder(db: Session, name: str, user_id: str, parent_id: Optional[int] = None) -> Folder:
    """
    Create a new folder.
    
    Args:
        db: Database session
        name: Folder name
        user_id: User ID
        parent_id: Parent folder ID (optional)
        
    Returns:
        Created folder instance
    """
    # Determine the path
    path = []
    if parent_id:
        parent_folder = get_folder(db, folder_id=parent_id)
        if parent_folder:
            path = parent_folder.path + [name]
        else:
            path = [name]
    else:
        path = [name]
    
    # Create the folder
    db_folder = Folder(name=name, user_id=user_id, parent_id=parent_id, path=path)
    db.add(db_folder)
    db.commit()
    db.refresh(db_folder)
    return db_folder

def get_folder(db: Session, folder_id: int) -> Optional[Folder]:
    """
    Get a folder by ID.
    
    Args:
        db: Database session
        folder_id: Folder ID
        
    Returns:
        Folder if found, None otherwise
    """
    return db.query(Folder).filter(Folder.id == folder_id).first()

def get_folders_by_user(db: Session, user_id: str, parent_id: Optional[int] = None) -> List[Folder]:
    """
    Get folders for a user, optionally filtered by parent folder.
    
    Args:
        db: Database session
        user_id: User ID
        parent_id: Parent folder ID (optional)
        
    Returns:
        List of folders
    """
    query = db.query(Folder).filter(Folder.user_id == user_id)
    if parent_id is not None:
        query = query.filter(Folder.parent_id == parent_id)
    else:
        query = query.filter(Folder.parent_id.is_(None))
    return query.all()

def update_folder(db: Session, folder_id: int, name: str) -> Optional[Folder]:
    """
    Update a folder name.
    
    Args:
        db: Database session
        folder_id: Folder ID
        name: New folder name
        
    Returns:
        Updated folder if found, None otherwise
    """
    db_folder = get_folder(db, folder_id)
    if db_folder:
        db_folder.name = name
        db_folder.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_folder)
    return db_folder

def delete_folder(db: Session, folder_id: int) -> bool:
    """
    Delete a folder.
    
    Args:
        db: Database session
        folder_id: Folder ID
        
    Returns:
        True if deleted, False otherwise
    """
    db_folder = get_folder(db, folder_id)
    if db_folder:
        db.delete(db_folder)
        db.commit()
        return True
    return False

# File CRUD operations
def create_file(
    db: Session, 
    name: str, 
    user_id: str, 
    blob_path: str,
    size_bytes: Optional[int] = None,
    mime_type: Optional[str] = None,
    folder_id: Optional[int] = None
) -> File:
    """
    Create a new file record.
    
    Args:
        db: Database session
        name: File name
        user_id: User ID
        blob_path: Path to the blob storage
        size_bytes: File size in bytes
        mime_type: File MIME type
        folder_id: Folder ID (optional)
        
    Returns:
        Created file instance
    """
    db_file = File(
        name=name,
        user_id=user_id,
        blob_path=blob_path,
        size_bytes=size_bytes,
        mime_type=mime_type,
        folder_id=folder_id,
        status='queued'
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file

def get_file(db: Session, file_id: int) -> Optional[File]:
    """
    Get a file by ID.
    
    Args:
        db: Database session
        file_id: File ID
        
    Returns:
        File if found, None otherwise
    """
    return db.query(File).filter(File.id == file_id).first()

def get_files_by_folder(db: Session, folder_id: Optional[int], user_id: str) -> List[File]:
    """
    Get files in a folder.
    
    Args:
        db: Database session
        folder_id: Folder ID (None for root folder)
        user_id: User ID
        
    Returns:
        List of files
    """
    query = db.query(File).filter(File.user_id == user_id)
    if folder_id is not None:
        query = query.filter(File.folder_id == folder_id)
    else:
        query = query.filter(File.folder_id.is_(None))
    return query.all()

def get_files_by_status(db: Session, status: str, limit: int = 100) -> List[File]:
    """
    Get files by processing status.
    
    Args:
        db: Database session
        status: File status
        limit: Maximum number of files to return
        
    Returns:
        List of files
    """
    return db.query(File).filter(File.status == status).limit(limit).all()

def update_file_status(
    db: Session, 
    file_id: int, 
    status: str, 
    metadata: Optional[Dict[str, Any]] = None,
    error_message: Optional[str] = None
) -> Optional[File]:
    """
    Update a file status and metadata.
    
    Args:
        db: Database session
        file_id: File ID
        status: New status
        metadata: File metadata
        error_message: Error message if status is 'error'
        
    Returns:
        Updated file if found, None otherwise
    """
    db_file = get_file(db, file_id)
    if db_file:
        db_file.status = status
        db_file.updated_at = datetime.utcnow()
        
        if status == 'processing':
            db_file.attempts += 1
            db_file.last_attempt_at = datetime.utcnow()
        
        if status == 'completed':
            db_file.processed_at = datetime.utcnow()
            
        if status == 'error':
            db_file.error_message = error_message
            
        if metadata:
            db_file.file_metadata = metadata
            
        db.commit()
        db.refresh(db_file)
    return db_file

def delete_file(db: Session, file_id: int) -> bool:
    """
    Delete a file record.
    
    Args:
        db: Database session
        file_id: File ID
        
    Returns:
        True if deleted, False otherwise
    """
    db_file = get_file(db, file_id)
    if db_file:
        db.delete(db_file)
        db.commit()
        return True
    return False

# Usage statistics CRUD operations
def get_or_create_usage_stat(db: Session, user_id: str, stat_date: date = None) -> UsageStat:
    """
    Get or create a usage statistics record for a user and date.
    
    Args:
        db: Database session
        user_id: User ID
        stat_date: Statistics date (default: today)
        
    Returns:
        Usage statistics record
    """
    if stat_date is None:
        stat_date = date.today()
        
    db_stat = db.query(UsageStat).filter(
        UsageStat.user_id == user_id,
        UsageStat.date == stat_date
    ).first()
    
    if not db_stat:
        db_stat = UsageStat(user_id=user_id, date=stat_date)
        db.add(db_stat)
        db.commit()
        db.refresh(db_stat)
        
    return db_stat

def update_pages_processed(db: Session, user_id: str, pages: int, stat_date: date = None) -> UsageStat:
    """
    Update the number of processed pages for a user.
    
    Args:
        db: Database session
        user_id: User ID
        pages: Number of pages to add
        stat_date: Statistics date (default: today)
        
    Returns:
        Updated usage statistics record
    """
    db_stat = get_or_create_usage_stat(db, user_id, stat_date)
    db_stat.pages_processed += pages
    db_stat.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_stat)
    return db_stat

def update_queries_made(db: Session, user_id: str, queries: int = 1, stat_date: date = None) -> UsageStat:
    """
    Update the number of queries made by a user.
    
    Args:
        db: Database session
        user_id: User ID
        queries: Number of queries to add
        stat_date: Statistics date (default: today)
        
    Returns:
        Updated usage statistics record
    """
    db_stat = get_or_create_usage_stat(db, user_id, stat_date)
    db_stat.queries_made += queries
    db_stat.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_stat)
    return db_stat

def update_storage_bytes(db: Session, user_id: str, bytes_added: int, stat_date: date = None) -> UsageStat:
    """
    Update the storage usage for a user.
    
    Args:
        db: Database session
        user_id: User ID
        bytes_added: Number of bytes to add
        stat_date: Statistics date (default: today)
        
    Returns:
        Updated usage statistics record
    """
    db_stat = get_or_create_usage_stat(db, user_id, stat_date)
    db_stat.storage_bytes += bytes_added
    db_stat.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_stat)
    return db_stat

def get_usage_stats_by_user(db: Session, user_id: str, start_date: date, end_date: date) -> List[UsageStat]:
    """
    Get usage statistics for a user within a date range.
    
    Args:
        db: Database session
        user_id: User ID
        start_date: Start date
        end_date: End date
        
    Returns:
        List of usage statistics records
    """
    return db.query(UsageStat).filter(
        UsageStat.user_id == user_id,
        UsageStat.date >= start_date,
        UsageStat.date <= end_date
    ).order_by(UsageStat.date).all()

def get_failed_files(db, max_attempts=3, cutoff_time=None):
    """
    Get files with error status for retry processing.
    
    Args:
        db: Database session
        max_attempts: Maximum number of retry attempts
        cutoff_time: Don't retry files created before this time
        
    Returns:
        List of File objects that need to be retried
    """
    query = db.query(File).filter(File.status == 'error', File.attempts < max_attempts)
    
    if cutoff_time:
        query = query.filter(File.created_at > cutoff_time)
        
    return query.all() 