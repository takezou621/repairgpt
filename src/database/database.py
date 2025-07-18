"""
Database configuration and connection management for RepairGPT
Supports both SQLite (development) and PostgreSQL (production)
"""

import os
import logging
from typing import AsyncGenerator, Generator
from contextlib import asynccontextmanager, contextmanager

from sqlalchemy import create_engine, event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from .models import Base

logger = logging.getLogger(__name__)

# Environment configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./repairgpt.db")
ASYNC_DATABASE_URL = os.getenv(
    "ASYNC_DATABASE_URL", "sqlite+aiosqlite:///./repairgpt.db"
)
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")


class DatabaseConfig:
    """Database configuration management"""

    def __init__(self):
        self.database_url = DATABASE_URL
        self.async_database_url = ASYNC_DATABASE_URL
        self.is_sqlite = "sqlite" in self.database_url.lower()
        self.is_production = ENVIRONMENT.lower() == "production"

    def get_engine_args(self) -> dict:
        """Get engine arguments based on database type"""
        args = {
            "echo": not self.is_production,  # SQL logging in development
        }

        if self.is_sqlite:
            # SQLite-specific configuration
            args.update(
                {
                    "poolclass": StaticPool,
                    "connect_args": {"check_same_thread": False, "timeout": 20},
                }
            )
        else:
            # PostgreSQL-specific configuration
            args.update(
                {
                    "pool_size": 20,
                    "max_overflow": 0,
                    "pool_pre_ping": True,
                    "pool_recycle": 300,
                }
            )

        return args

    def get_async_engine_args(self) -> dict:
        """Get async engine arguments based on database type"""
        args = {
            "echo": not self.is_production,
        }

        if self.is_sqlite:
            # SQLite async configuration
            args.update(
                {
                    "poolclass": StaticPool,
                    "connect_args": {"check_same_thread": False, "timeout": 20},
                }
            )
        else:
            # PostgreSQL async configuration
            args.update(
                {
                    "pool_size": 20,
                    "max_overflow": 0,
                    "pool_pre_ping": True,
                    "pool_recycle": 300,
                }
            )

        return args


# Database configuration instance
db_config = DatabaseConfig()

# Synchronous engine and session factory
engine = create_engine(db_config.database_url, **db_config.get_engine_args())

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Asynchronous engine and session factory
async_engine = create_async_engine(
    db_config.async_database_url, **db_config.get_async_engine_args()
)

AsyncSessionLocal = async_sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)


def enable_sqlite_foreign_keys(dbapi_connection, connection_record):
    """Enable foreign key constraints for SQLite"""
    if db_config.is_sqlite:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


# Enable foreign keys for SQLite
if db_config.is_sqlite:
    event.listen(engine, "connect", enable_sqlite_foreign_keys)


# Dependency injection functions for FastAPI
def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session for FastAPI endpoints

    Example usage:
        @app.get("/users/")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Async dependency function to get database session for FastAPI endpoints

    Example usage:
        @app.get("/users/")
        async def get_users(db: AsyncSession = Depends(get_async_db)):
            result = await db.execute(select(User))
            return result.scalars().all()
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Async database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


# Context managers for manual session management
@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Context manager for manual database session management

    Example usage:
        with get_db_session() as db:
            user = db.query(User).first()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        logger.error(f"Database transaction error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


@asynccontextmanager
async def get_async_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Async context manager for manual database session management

    Example usage:
        async with get_async_db_session() as db:
            result = await db.execute(select(User))
            users = result.scalars().all()
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            logger.error(f"Async database transaction error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


# Database utility functions
def create_tables():
    """Create all database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


async def create_tables_async():
    """Create all database tables asynchronously"""
    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully (async)")
    except Exception as e:
        logger.error(f"Error creating database tables (async): {e}")
        raise


def drop_tables():
    """Drop all database tables - USE WITH CAUTION!"""
    try:
        Base.metadata.drop_all(bind=engine)
        logger.warning("All database tables dropped")
    except Exception as e:
        logger.error(f"Error dropping database tables: {e}")
        raise


async def drop_tables_async():
    """Drop all database tables asynchronously - USE WITH CAUTION!"""
    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        logger.warning("All database tables dropped (async)")
    except Exception as e:
        logger.error(f"Error dropping database tables (async): {e}")
        raise


def check_database_health() -> bool:
    """Check database connectivity and health"""
    try:
        with get_db_session() as db:
            # Simple query to test connection
            db.execute("SELECT 1")
        logger.info("Database health check passed")
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False


async def check_database_health_async() -> bool:
    """Check database connectivity and health asynchronously"""
    try:
        async with get_async_db_session() as db:
            # Simple query to test connection
            await db.execute("SELECT 1")
        logger.info("Database health check passed (async)")
        return True
    except Exception as e:
        logger.error(f"Database health check failed (async): {e}")
        return False


# Database information functions
def get_database_info() -> dict:
    """Get database information and statistics"""
    info = {
        "database_url": (
            db_config.database_url.split("@")[-1]
            if "@" in db_config.database_url
            else db_config.database_url
        ),
        "database_type": "sqlite" if db_config.is_sqlite else "postgresql",
        "environment": ENVIRONMENT,
        "tables": [],
    }

    try:
        with get_db_session() as db:
            # Get table names
            if db_config.is_sqlite:
                result = db.execute("SELECT name FROM sqlite_master WHERE type='table'")
            else:
                result = db.execute(
                    "SELECT tablename FROM pg_tables WHERE schemaname='public'"
                )

            info["tables"] = [row[0] for row in result.fetchall()]
            info["health_status"] = "healthy"

    except Exception as e:
        logger.error(f"Error getting database info: {e}")
        info["health_status"] = "unhealthy"
        info["error"] = str(e)

    return info


# Export commonly used items
__all__ = [
    "engine",
    "async_engine",
    "SessionLocal",
    "AsyncSessionLocal",
    "get_db",
    "get_async_db",
    "get_db_session",
    "get_async_db_session",
    "create_tables",
    "create_tables_async",
    "drop_tables",
    "drop_tables_async",
    "check_database_health",
    "check_database_health_async",
    "get_database_info",
    "Base",
]
