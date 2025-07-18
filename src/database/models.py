"""
SQLAlchemy Models for RepairGPT Database
Implements comprehensive database schema with 12 tables
"""

import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Decimal,
    ForeignKey,
    Integer,
    String,
    Text,
    CheckConstraint,
    JSON,
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class User(Base):
    """User information and authentication"""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_login_at = Column(DateTime, nullable=True)

    # Relationships
    chat_sessions = relationship("ChatSession", back_populates="user")
    repair_attempts = relationship("RepairAttempt", back_populates="user")
    repair_guides = relationship("RepairGuide", back_populates="created_by_user")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


class Device(Base):
    """Device catalog and specifications"""

    __tablename__ = "devices"

    id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)
    manufacturer = Column(String(100), nullable=True)
    model_variants = Column(JSON, nullable=True)  # For SQLite compatibility
    release_year = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    device_issues = relationship("DeviceIssue", back_populates="device")
    repair_guides = relationship("RepairGuide", back_populates="device")
    chat_sessions = relationship("ChatSession", back_populates="device")
    repair_attempts = relationship("RepairAttempt", back_populates="device")

    def __repr__(self):
        return f"<Device(id='{self.id}', name='{self.name}')>"


class Issue(Base):
    """Problem categories and descriptions"""

    __tablename__ = "issues"

    id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=False)
    severity = Column(String(20), default="medium")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())

    # Constraints
    __table_args__ = (
        CheckConstraint(
            severity.in_(["low", "medium", "high", "critical"]),
            name="chk_issue_severity",
        ),
    )

    # Relationships
    device_issues = relationship("DeviceIssue", back_populates="issue")
    repair_guides = relationship("RepairGuide", back_populates="issue")
    chat_sessions = relationship("ChatSession", back_populates="issue")
    repair_attempts = relationship("RepairAttempt", back_populates="issue")

    def __repr__(self):
        return f"<Issue(id='{self.id}', name='{self.name}')>"


class DeviceIssue(Base):
    """Device-Issue relationship with frequency and difficulty"""

    __tablename__ = "device_issues"

    device_id = Column(String(50), ForeignKey("devices.id"), primary_key=True)
    issue_id = Column(String(50), ForeignKey("issues.id"), primary_key=True)
    frequency = Column(Decimal(3, 2), default=0.0)
    difficulty = Column(String(20), default="medium")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            difficulty.in_(["beginner", "intermediate", "advanced"]),
            name="chk_device_issue_difficulty",
        ),
    )

    # Relationships
    device = relationship("Device", back_populates="device_issues")
    issue = relationship("Issue", back_populates="device_issues")

    def __repr__(self):
        return (
            f"<DeviceIssue(device_id='{self.device_id}', issue_id='{self.issue_id}')>"
        )


class RepairGuide(Base):
    """Repair guides and instructions"""

    __tablename__ = "repair_guides"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)
    device_id = Column(String(50), ForeignKey("devices.id"), nullable=False)
    issue_id = Column(String(50), ForeignKey("issues.id"), nullable=False)
    difficulty = Column(String(20), nullable=False, default="medium")
    estimated_time = Column(Integer, nullable=True)  # minutes
    success_rate = Column(Decimal(3, 2), default=0.0)
    tools_required = Column(JSON, nullable=True)  # JSON array
    parts_required = Column(JSON, nullable=True)  # JSON array
    safety_warnings = Column(JSON, nullable=True)  # JSON array
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Constraints
    __table_args__ = (
        CheckConstraint(
            difficulty.in_(["beginner", "intermediate", "advanced"]),
            name="chk_repair_guide_difficulty",
        ),
    )

    # Relationships
    device = relationship("Device", back_populates="repair_guides")
    issue = relationship("Issue", back_populates="repair_guides")
    created_by_user = relationship("User", back_populates="repair_guides")
    repair_steps = relationship(
        "RepairStep", back_populates="repair_guide", cascade="all, delete-orphan"
    )
    repair_attempts = relationship("RepairAttempt", back_populates="repair_guide")

    def __repr__(self):
        return f"<RepairGuide(id={self.id}, title='{self.title}')>"


class RepairStep(Base):
    """Individual steps within repair guides"""

    __tablename__ = "repair_steps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    repair_guide_id = Column(
        UUID(as_uuid=True),
        ForeignKey("repair_guides.id", ondelete="CASCADE"),
        nullable=False,
    )
    step_number = Column(Integer, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    image_url = Column(String(500), nullable=True)
    warning = Column(Text, nullable=True)
    tips = Column(Text, nullable=True)
    estimated_time = Column(Integer, nullable=True)  # minutes
    created_at = Column(DateTime, default=func.now())

    # Relationships
    repair_guide = relationship("RepairGuide", back_populates="repair_steps")

    def __repr__(self):
        return f"<RepairStep(id={self.id}, step_number={self.step_number})>"


class ChatSession(Base):
    """Chat sessions between users and AI"""

    __tablename__ = "chat_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    device_id = Column(String(50), ForeignKey("devices.id"), nullable=True)
    issue_id = Column(String(50), ForeignKey("issues.id"), nullable=True)
    session_data = Column(JSON, nullable=True)  # Session-specific data
    status = Column(String(20), default="active")
    started_at = Column(DateTime, default=func.now())
    ended_at = Column(DateTime, nullable=True)
    last_activity_at = Column(DateTime, default=func.now())

    # Constraints
    __table_args__ = (
        CheckConstraint(
            status.in_(["active", "completed", "abandoned"]),
            name="chk_chat_session_status",
        ),
    )

    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    device = relationship("Device", back_populates="chat_sessions")
    issue = relationship("Issue", back_populates="chat_sessions")
    chat_messages = relationship(
        "ChatMessage", back_populates="chat_session", cascade="all, delete-orphan"
    )
    user_images = relationship("UserImage", back_populates="chat_session")
    repair_attempts = relationship("RepairAttempt", back_populates="chat_session")

    def __repr__(self):
        return f"<ChatSession(id={self.id}, status='{self.status}')>"


class ChatMessage(Base):
    """Individual messages within chat sessions"""

    __tablename__ = "chat_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    sender = Column(String(10), nullable=False)  # 'user' or 'bot'
    content = Column(Text, nullable=False)
    message_type = Column(String(20), default="text")  # 'text', 'image', 'repair_guide'
    metadata = Column(JSON, nullable=True)  # Additional data (image URLs, etc.)
    created_at = Column(DateTime, default=func.now())

    # Constraints
    __table_args__ = (
        CheckConstraint(sender.in_(["user", "bot"]), name="chk_chat_message_sender"),
    )

    # Relationships
    chat_session = relationship("ChatSession", back_populates="chat_messages")

    def __repr__(self):
        return f"<ChatMessage(id={self.id}, sender='{self.sender}')>"


class UserImage(Base):
    """User-uploaded images for analysis"""

    __tablename__ = "user_images"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(
        UUID(as_uuid=True), ForeignKey("chat_sessions.id"), nullable=False
    )
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=True)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=True)
    mime_type = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    analysis_result = Column(JSON, nullable=True)  # Image analysis results
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, nullable=True)  # For automatic cleanup

    # Relationships
    chat_session = relationship("ChatSession", back_populates="user_images")

    def __repr__(self):
        return f"<UserImage(id={self.id}, filename='{self.filename}')>"


class RepairAttempt(Base):
    """User attempts at repairs with tracking"""

    __tablename__ = "repair_attempts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    session_id = Column(
        UUID(as_uuid=True), ForeignKey("chat_sessions.id"), nullable=False
    )
    repair_guide_id = Column(
        UUID(as_uuid=True), ForeignKey("repair_guides.id"), nullable=True
    )
    device_id = Column(String(50), ForeignKey("devices.id"), nullable=False)
    issue_id = Column(String(50), ForeignKey("issues.id"), nullable=False)
    status = Column(String(20), default="in_progress")
    success = Column(Boolean, nullable=True)
    completion_rate = Column(Decimal(3, 2), default=0.0)
    feedback = Column(Text, nullable=True)
    rating = Column(Integer, nullable=True)
    started_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime, nullable=True)

    # Constraints
    __table_args__ = (
        CheckConstraint(
            status.in_(["in_progress", "completed", "failed", "abandoned"]),
            name="chk_repair_attempt_status",
        ),
        CheckConstraint(
            "rating >= 1 AND rating <= 5", name="chk_repair_attempt_rating"
        ),
    )

    # Relationships
    user = relationship("User", back_populates="repair_attempts")
    chat_session = relationship("ChatSession", back_populates="repair_attempts")
    repair_guide = relationship("RepairGuide", back_populates="repair_attempts")
    device = relationship("Device", back_populates="repair_attempts")
    issue = relationship("Issue", back_populates="repair_attempts")

    def __repr__(self):
        return f"<RepairAttempt(id={self.id}, status='{self.status}')>"


class ExternalDataSource(Base):
    """External data sources for sync operations"""

    __tablename__ = "external_data_sources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    source_type = Column(String(50), nullable=False)  # 'ifixit', 'reddit', 'youtube'
    base_url = Column(String(500), nullable=True)
    api_key_name = Column(String(100), nullable=True)
    last_sync_at = Column(DateTime, nullable=True)
    sync_status = Column(String(20), default="pending")
    config = Column(JSON, nullable=True)  # Source-specific configuration
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    sync_logs = relationship("SyncLog", back_populates="external_data_source")

    def __repr__(self):
        return f"<ExternalDataSource(id={self.id}, name='{self.name}')>"


class SyncLog(Base):
    """Synchronization logs for external data sources"""

    __tablename__ = "sync_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id = Column(
        UUID(as_uuid=True), ForeignKey("external_data_sources.id"), nullable=False
    )
    sync_type = Column(String(50), nullable=False)
    records_processed = Column(Integer, default=0)
    records_created = Column(Integer, default=0)
    records_updated = Column(Integer, default=0)
    records_failed = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    external_data_source = relationship(
        "ExternalDataSource", back_populates="sync_logs"
    )

    def __repr__(self):
        return f"<SyncLog(id={self.id}, sync_type='{self.sync_type}')>"
