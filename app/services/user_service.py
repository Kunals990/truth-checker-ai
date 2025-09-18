from sqlalchemy.orm import Session
from typing import Optional
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

class UserService:
    """Service to handle user operations"""
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_user_by_google_id(db: Session, google_id: str) -> Optional[User]:
        """Get user by Google ID"""
        return db.query(User).filter(User.google_id == google_id).first()
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """Create new user"""
        db_user = User(
            email=user_data.email,
            name=user_data.name,
            picture=user_data.picture,
            google_id=user_data.google_id
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def update_user(db: Session, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update user information"""
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            return None
        
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """Delete user"""
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            return False
        
        db.delete(user)
        db.commit()
        return True

# Global instance
user_service = UserService()