import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, BigInteger, Integer, Date, Text, UniqueConstraint, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(String(255), primary_key=True)  # Clerk user ID
    email = Column(String(255), nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    settings = Column(JSONB, default={})
    
    def __repr__(self):
        return f"<User(id='{self.id}', email='{self.email}')>"

class Folder(Base):
    __tablename__ = 'folders'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    parent_id = Column(Integer, ForeignKey('folders.id'), nullable=True)
    user_id = Column(String(255), ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    path = Column(ARRAY(Text), nullable=False, default=[])
    
    __table_args__ = (
        UniqueConstraint('user_id', 'name', 'parent_id', name='folders_name_user_id_key'),
    )
    
    def __repr__(self):
        return f"<Folder(id='{self.id}', name='{self.name}', user_id='{self.user_id}')>"

class File(Base):
    __tablename__ = 'files'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    folder_id = Column(Integer, ForeignKey('folders.id', ondelete='CASCADE'), nullable=True)
    user_id = Column(String(255), ForeignKey('users.id'), nullable=True)
    blob_path = Column(Text, nullable=False)
    size_bytes = Column(BigInteger, nullable=True)
    mime_type = Column(String(255), nullable=True)
    status = Column(String(50), nullable=False, default='queued')
    attempts = Column(Integer, default=0)
    last_attempt_at = Column(DateTime(timezone=True), nullable=True)
    file_metadata = Column('metadata', JSONB, default={})
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<File(id='{self.id}', name='{self.name}', status='{self.status}')>"

class UsageStat(Base):
    __tablename__ = 'usage_stats'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), ForeignKey('users.id'), nullable=True)
    date = Column(Date, nullable=False)
    pages_processed = Column(Integer, default=0)
    queries_made = Column(Integer, default=0)
    storage_bytes = Column(BigInteger, default=0)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('user_id', 'date', name='usage_stats_user_id_date_key'),
    )
    
    def __repr__(self):
        return f"<UsageStat(id='{self.id}', user_id='{self.user_id}', date='{self.date}')>" 