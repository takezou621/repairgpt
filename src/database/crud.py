"""
CRUD (Create, Read, Update, Delete) operations for RepairGPT database
Provides high-level database operations for all models
"""

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any, Union

from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, selectinload

from .models import (
    User, Device, Issue, DeviceIssue, RepairGuide, RepairStep,
    ChatSession, ChatMessage, UserImage, RepairAttempt,
    ExternalDataSource, SyncLog
)


class UserCRUD:
    """CRUD operations for User model"""
    
    @staticmethod
    def create_user(db: Session, username: str, email: str, password_hash: str) -> User:
        """Create a new user"""
        user = User(
            username=username,
            email=email,
            password_hash=password_hash
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    async def create_user_async(db: AsyncSession, username: str, email: str, password_hash: str) -> User:
        """Create a new user asynchronously"""
        user = User(
            username=username,
            email=email, 
            password_hash=password_hash
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: Union[str, uuid.UUID]) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """Get user by username"""
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def update_last_login(db: Session, user_id: Union[str, uuid.UUID]) -> bool:
        """Update user's last login timestamp"""
        result = db.query(User).filter(User.id == user_id).update({
            "last_login_at": datetime.utcnow()
        })
        db.commit()
        return result > 0


class DeviceCRUD:
    """CRUD operations for Device model"""
    
    @staticmethod
    def create_device(db: Session, device_id: str, name: str, category: str, **kwargs) -> Device:
        """Create a new device"""
        device = Device(
            id=device_id,
            name=name,
            category=category,
            **kwargs
        )
        db.add(device)
        db.commit()
        db.refresh(device)
        return device
    
    @staticmethod
    def get_device_by_id(db: Session, device_id: str) -> Optional[Device]:
        """Get device by ID"""
        return db.query(Device).filter(Device.id == device_id).first()
    
    @staticmethod
    def get_devices_by_category(db: Session, category: str, limit: int = 10) -> List[Device]:
        """Get devices by category"""
        return db.query(Device).filter(
            Device.category == category,
            Device.is_active == True
        ).limit(limit).all()
    
    @staticmethod
    def search_devices(db: Session, query: str, limit: int = 10) -> List[Device]:
        """Search devices by name or manufacturer"""
        search_term = f"%{query}%"
        return db.query(Device).filter(
            or_(
                Device.name.ilike(search_term),
                Device.manufacturer.ilike(search_term)
            ),
            Device.is_active == True
        ).limit(limit).all()


class RepairGuideCRUD:
    """CRUD operations for RepairGuide model"""
    
    @staticmethod
    def create_repair_guide(
        db: Session,
        title: str,
        device_id: str,
        issue_id: str,
        difficulty: str,
        **kwargs
    ) -> RepairGuide:
        """Create a new repair guide"""
        guide = RepairGuide(
            title=title,
            device_id=device_id,
            issue_id=issue_id,
            difficulty=difficulty,
            **kwargs
        )
        db.add(guide)
        db.commit()
        db.refresh(guide)
        return guide
    
    @staticmethod
    def get_repair_guide_by_id(db: Session, guide_id: Union[str, uuid.UUID]) -> Optional[RepairGuide]:
        """Get repair guide by ID with steps"""
        return db.query(RepairGuide).options(
            selectinload(RepairGuide.repair_steps)
        ).filter(RepairGuide.id == guide_id).first()
    
    @staticmethod
    def get_guides_for_device_issue(
        db: Session,
        device_id: str,
        issue_id: str,
        difficulty: Optional[str] = None,
        limit: int = 10
    ) -> List[RepairGuide]:
        """Get repair guides for specific device and issue"""
        query = db.query(RepairGuide).filter(
            RepairGuide.device_id == device_id,
            RepairGuide.issue_id == issue_id,
            RepairGuide.is_active == True
        )
        
        if difficulty:
            query = query.filter(RepairGuide.difficulty == difficulty)
        
        return query.order_by(RepairGuide.success_rate.desc()).limit(limit).all()
    
    @staticmethod
    def search_repair_guides(
        db: Session,
        query: str,
        device_id: Optional[str] = None,
        limit: int = 10
    ) -> List[RepairGuide]:
        """Search repair guides by title or description"""
        search_term = f"%{query}%"
        db_query = db.query(RepairGuide).filter(
            or_(
                RepairGuide.title.ilike(search_term),
                RepairGuide.description.ilike(search_term)
            ),
            RepairGuide.is_active == True
        )
        
        if device_id:
            db_query = db_query.filter(RepairGuide.device_id == device_id)
        
        return db_query.order_by(RepairGuide.success_rate.desc()).limit(limit).all()


class ChatSessionCRUD:
    """CRUD operations for ChatSession model"""
    
    @staticmethod
    def create_chat_session(
        db: Session,
        user_id: Optional[Union[str, uuid.UUID]] = None,
        device_id: Optional[str] = None,
        issue_id: Optional[str] = None,
        session_data: Optional[Dict] = None
    ) -> ChatSession:
        """Create a new chat session"""
        session = ChatSession(
            user_id=user_id,
            device_id=device_id,
            issue_id=issue_id,
            session_data=session_data or {}
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session
    
    @staticmethod
    async def create_chat_session_async(
        db: AsyncSession,
        user_id: Optional[Union[str, uuid.UUID]] = None,
        device_id: Optional[str] = None,
        issue_id: Optional[str] = None,
        session_data: Optional[Dict] = None
    ) -> ChatSession:
        """Create a new chat session asynchronously"""
        session = ChatSession(
            user_id=user_id,
            device_id=device_id,
            issue_id=issue_id,
            session_data=session_data or {}
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)
        return session
    
    @staticmethod
    def get_chat_session_by_id(db: Session, session_id: Union[str, uuid.UUID]) -> Optional[ChatSession]:
        """Get chat session by ID with messages"""
        return db.query(ChatSession).options(
            selectinload(ChatSession.chat_messages)
        ).filter(ChatSession.id == session_id).first()
    
    @staticmethod
    def add_message_to_session(
        db: Session,
        session_id: Union[str, uuid.UUID],
        sender: str,
        content: str,
        message_type: str = "text",
        metadata: Optional[Dict] = None
    ) -> ChatMessage:
        """Add a message to a chat session"""
        message = ChatMessage(
            session_id=session_id,
            sender=sender,
            content=content,
            message_type=message_type,
            metadata=metadata or {}
        )
        db.add(message)
        
        # Update session activity
        db.query(ChatSession).filter(ChatSession.id == session_id).update({
            "last_activity_at": datetime.utcnow()
        })
        
        db.commit()
        db.refresh(message)
        return message
    
    @staticmethod
    def end_chat_session(db: Session, session_id: Union[str, uuid.UUID]) -> bool:
        """End a chat session"""
        result = db.query(ChatSession).filter(ChatSession.id == session_id).update({
            "status": "completed",
            "ended_at": datetime.utcnow()
        })
        db.commit()
        return result > 0


class RepairAttemptCRUD:
    """CRUD operations for RepairAttempt model"""
    
    @staticmethod
    def create_repair_attempt(
        db: Session,
        session_id: Union[str, uuid.UUID],
        device_id: str,
        issue_id: str,
        user_id: Optional[Union[str, uuid.UUID]] = None,
        repair_guide_id: Optional[Union[str, uuid.UUID]] = None
    ) -> RepairAttempt:
        """Create a new repair attempt"""
        attempt = RepairAttempt(
            user_id=user_id,
            session_id=session_id,
            repair_guide_id=repair_guide_id,
            device_id=device_id,
            issue_id=issue_id
        )
        db.add(attempt)
        db.commit()
        db.refresh(attempt)
        return attempt
    
    @staticmethod
    def update_repair_progress(
        db: Session,
        attempt_id: Union[str, uuid.UUID],
        completion_rate: float,
        status: Optional[str] = None
    ) -> bool:
        """Update repair attempt progress"""
        update_data = {"completion_rate": completion_rate}
        if status:
            update_data["status"] = status
        
        result = db.query(RepairAttempt).filter(RepairAttempt.id == attempt_id).update(update_data)
        db.commit()
        return result > 0
    
    @staticmethod
    def complete_repair_attempt(
        db: Session,
        attempt_id: Union[str, uuid.UUID],
        success: bool,
        feedback: Optional[str] = None,
        rating: Optional[int] = None
    ) -> bool:
        """Complete a repair attempt with feedback"""
        update_data = {
            "status": "completed",
            "success": success,
            "completed_at": datetime.utcnow(),
            "completion_rate": 1.0 if success else None
        }
        
        if feedback:
            update_data["feedback"] = feedback
        if rating and 1 <= rating <= 5:
            update_data["rating"] = rating
        
        result = db.query(RepairAttempt).filter(RepairAttempt.id == attempt_id).update(update_data)
        db.commit()
        return result > 0
    
    @staticmethod
    def get_user_repair_history(
        db: Session,
        user_id: Union[str, uuid.UUID],
        limit: int = 10
    ) -> List[RepairAttempt]:
        """Get user's repair attempt history"""
        return db.query(RepairAttempt).filter(
            RepairAttempt.user_id == user_id
        ).order_by(RepairAttempt.started_at.desc()).limit(limit).all()


class StatisticsCRUD:
    """CRUD operations for statistics and analytics"""
    
    @staticmethod
    def get_repair_success_rate_by_device(db: Session) -> List[Dict[str, Any]]:
        """Get repair success rate by device"""
        results = db.query(
            RepairAttempt.device_id,
            Device.name.label("device_name"),
            func.avg(func.cast(RepairAttempt.success, func.Float)).label("success_rate"),
            func.count(RepairAttempt.id).label("total_attempts")
        ).join(Device).filter(
            RepairAttempt.status == "completed"
        ).group_by(RepairAttempt.device_id, Device.name).all()
        
        return [
            {
                "device_id": r.device_id,
                "device_name": r.device_name,
                "success_rate": float(r.success_rate) if r.success_rate else 0.0,
                "total_attempts": r.total_attempts
            }
            for r in results
        ]
    
    @staticmethod
    def get_popular_devices(db: Session, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most popular devices by chat sessions"""
        results = db.query(
            ChatSession.device_id,
            Device.name.label("device_name"),
            func.count(ChatSession.id).label("session_count")
        ).join(Device).filter(
            ChatSession.device_id.isnot(None)
        ).group_by(ChatSession.device_id, Device.name).order_by(
            func.count(ChatSession.id).desc()
        ).limit(limit).all()
        
        return [
            {
                "device_id": r.device_id,
                "device_name": r.device_name,
                "session_count": r.session_count
            }
            for r in results
        ]
    
    @staticmethod
    def get_database_stats(db: Session) -> Dict[str, int]:
        """Get general database statistics"""
        return {
            "total_users": db.query(User).count(),
            "total_devices": db.query(Device).filter(Device.is_active == True).count(),
            "total_repair_guides": db.query(RepairGuide).filter(RepairGuide.is_active == True).count(),
            "total_chat_sessions": db.query(ChatSession).count(),
            "active_sessions": db.query(ChatSession).filter(ChatSession.status == "active").count(),
            "total_repair_attempts": db.query(RepairAttempt).count(),
            "successful_repairs": db.query(RepairAttempt).filter(
                RepairAttempt.success == True
            ).count()
        }


# Export CRUD classes for easy import
__all__ = [
    "UserCRUD",
    "DeviceCRUD", 
    "RepairGuideCRUD",
    "ChatSessionCRUD",
    "RepairAttemptCRUD",
    "StatisticsCRUD"
]