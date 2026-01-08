"""
Database layer for Capture using SQLAlchemy.
Manages screenshot library with chain-of-custody tracking.
"""
import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from pathlib import Path
from typing import Optional, List
import json

Base = declarative_base()


class Screenshot(Base):
    """Screenshot model for database."""
    
    __tablename__ = 'screenshots'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    original_path = Column(String(512), nullable=False)
    modified_path = Column(String(512), nullable=True)
    import_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_modified = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    tags = Column(String(512), default='')  # Comma-separated tags
    image_metadata = Column(JSON, default={})  # Store width, height, file_size, etc.
    sanitization_log = Column(Text, nullable=True)  # Log of PII redactions
    
    def __repr__(self):
        return f"<Screenshot(id={self.id}, original={Path(self.original_path).name})>"


class DatabaseManager:
    """Manages database operations for Capture."""
    
    def __init__(self, db_path: str = None):
        """
        Initialize database manager.
        
        Args:
            db_path: Path to SQLite database file (optional, uses XDG base dir by default)
        """
        if db_path is None:
            # Use XDG-compliant base directory for Fedora
            xdg_data_home = os.path.expanduser("~/.local/share/capture")
            os.makedirs(xdg_data_home, exist_ok=True)
            db_path = os.path.join(xdg_data_home, "capture.db")
        
        self.db_path = db_path
        # Use four slashes for absolute path in SQLite URI
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def get_session(self) -> Session:
        """Get new database session."""
        return self.SessionLocal()
    
    def add_screenshot(
        self,
        original_path: str,
        image_metadata: dict = None,
        tags: str = ''
    ) -> Optional[Screenshot]:
        """
        Add new screenshot to database.
        
        Args:
            original_path: Path to original image
            image_metadata: Image metadata dictionary
            tags: Comma-separated tags
            
        Returns:
            Created Screenshot object or None
        """
        session = self.get_session()
        try:
            screenshot = Screenshot(
                original_path=original_path,
                image_metadata=image_metadata or {},
                tags=tags
            )
            session.add(screenshot)
            session.commit()
            session.refresh(screenshot)
            return screenshot
        except Exception as e:
            session.rollback()
            print(f"Error adding screenshot: {e}")
            return None
        finally:
            session.close()
    
    def update_screenshot(
        self,
        screenshot_id: int,
        modified_path: str = None,
        tags: str = None,
        sanitization_log: str = None
    ) -> bool:
        """
        Update screenshot record.
        
        Args:
            screenshot_id: Screenshot ID
            modified_path: Path to modified version
            tags: Updated tags
            sanitization_log: Log of sanitization actions
            
        Returns:
            True if successful, False otherwise
        """
        session = self.get_session()
        try:
            screenshot = session.query(Screenshot).filter_by(id=screenshot_id).first()
            if not screenshot:
                return False
            
            if modified_path:
                screenshot.modified_path = modified_path
            if tags is not None:
                screenshot.tags = tags
            if sanitization_log:
                screenshot.sanitization_log = sanitization_log
            
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error updating screenshot: {e}")
            return False
        finally:
            session.close()
    
    def get_all_screenshots(self) -> List[Screenshot]:
        """
        Get all screenshots from database.
        
        Returns:
            List of Screenshot objects
        """
        session = self.get_session()
        try:
            return session.query(Screenshot).order_by(Screenshot.import_date.desc()).all()
        finally:
            session.close()
    
    def get_screenshot(self, screenshot_id: int) -> Optional[Screenshot]:
        """
        Get specific screenshot by ID.
        
        Args:
            screenshot_id: Screenshot ID
            
        Returns:
            Screenshot object or None
        """
        session = self.get_session()
        try:
            return session.query(Screenshot).filter_by(id=screenshot_id).first()
        finally:
            session.close()
    
    def delete_screenshot(self, screenshot_id: int) -> bool:
        """
        Delete screenshot from database.
        
        Args:
            screenshot_id: Screenshot ID
            
        Returns:
            True if successful, False otherwise
        """
        session = self.get_session()
        try:
            screenshot = session.query(Screenshot).filter_by(id=screenshot_id).first()
            if screenshot:
                session.delete(screenshot)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            print(f"Error deleting screenshot: {e}")
            return False
        finally:
            session.close()
    
    def search_by_tags(self, tag: str) -> List[Screenshot]:
        """
        Search screenshots by tag.
        
        Args:
            tag: Tag to search for
            
        Returns:
            List of matching Screenshot objects
        """
        session = self.get_session()
        try:
            return session.query(Screenshot).filter(
                Screenshot.tags.like(f'%{tag}%')
            ).all()
        finally:
            session.close()
