from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, JSON, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from dotenv import load_dotenv
import os
import uuid
from datetime import datetime

# Load environment variables
load_dotenv()

# Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Create session factory
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Base class for database models
Base = declarative_base()

# Database Models
class StatusCheckTable(Base):
    __tablename__ = "status_checks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    client_name = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

class UserTable(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    user_type = Column(String, default="customer")  # customer, admin
    plan_type = Column(String, default="basic")  # basic, pro
    plan_expires = Column(DateTime, nullable=True)
    max_links = Column(Integer, default=5)
    links_created = Column(Integer, default=0)
    features_enabled = Column(JSON, default={})
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SubscriptionTable(Base):
    __tablename__ = "subscriptions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    plan_type = Column(String, default="basic")  # basic, pro
    plan_expires = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    auto_renew = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class LinkTable(Base):
    __tablename__ = "links"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    original_url = Column(Text, nullable=False)
    short_url = Column(String, unique=True, nullable=True)
    title = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    category = Column(String, default="General")
    tags = Column(JSON, default=[])
    custom_domain = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    clicks = Column(Integer, default=0)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    user_email = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ImportJobTable(Base):
    __tablename__ = "import_jobs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    import_type = Column(String, nullable=False)  # links, users, analytics, etc.
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    status = Column(String, default="pending")  # pending, processing, completed, failed
    total_records = Column(Integer, default=0)
    processed_records = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    errors = Column(JSON, default=[])
    job_metadata = Column(JSON, default={})  # Renamed from metadata to job_metadata
    created_by = Column(String, nullable=False)  # User ID who initiated

class AnalyticsTable(Base):
    __tablename__ = "analytics"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    link_id = Column(String, ForeignKey("links.id"), nullable=True)
    short_url = Column(String, nullable=True)
    original_url = Column(Text, nullable=True)
    clicks = Column(Integer, default=0)
    unique_clicks = Column(Integer, default=0)
    click_date = Column(DateTime, nullable=False)
    country = Column(String, nullable=True)
    city = Column(String, nullable=True)
    device_type = Column(String, nullable=True)
    browser = Column(String, nullable=True)
    os = Column(String, nullable=True)
    referrer = Column(String, nullable=True)
    user_agent = Column(Text, nullable=True)
    ip_address = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class DomainTable(Base):
    __tablename__ = "domains"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    domain = Column(String, unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    ssl_enabled = Column(Boolean, default=True)
    dns_verified = Column(Boolean, default=False)
    owner_user_id = Column(String, ForeignKey("users.id"), nullable=True)
    owner_email = Column(String, nullable=True)
    settings = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ContactTable(Base):
    __tablename__ = "contacts"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    company = Column(String, nullable=True)
    position = Column(String, nullable=True)
    tags = Column(JSON, default=[])
    notes = Column(Text, nullable=True)
    source = Column(String, nullable=True)
    status = Column(String, default="active")
    contact_metadata = Column(JSON, default={})  # Renamed from metadata to contact_metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Database utility functions
async def get_db():
    """Get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def create_tables():
    """Create all database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def drop_tables():
    """Drop all database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)