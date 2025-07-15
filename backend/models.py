from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
from enum import Enum

# Data Models for LinkAbet Import System

class ImportType(str, Enum):
    LINKS = "links"
    USERS = "users"
    ANALYTICS = "analytics"
    DOMAINS = "domains"
    CONTACTS = "contacts"
    PLATFORM_MIGRATION = "platform_migration"

class ImportStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"

# Subscription and Plan Models
class PlanType(str, Enum):
    BASIC = "basic"
    PRO = "pro"

class PlanLimits(BaseModel):
    max_links: int
    max_clicks_per_month: int
    custom_domains: bool
    analytics_retention_days: int
    api_access: bool
    ads_free: bool

class SubscriptionPlan(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    plan_type: PlanType
    price_monthly: float
    price_yearly: float
    limits: PlanLimits
    features: List[str]
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserSubscription(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    plan_type: PlanType = PlanType.BASIC
    plan_expires: Optional[datetime] = None
    is_active: bool = True
    auto_renew: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    name: str
    user_type: str = "customer"  # "customer" or "admin"
    plan_type: PlanType = PlanType.BASIC
    plan_expires: Optional[datetime] = None
    max_links: int = 5
    links_created: int = 0
    features_enabled: Dict[str, bool] = {}
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Base Import Model
class ImportJob(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    import_type: ImportType
    filename: str
    original_filename: str
    status: ImportStatus = ImportStatus.PENDING
    total_records: int = 0
    processed_records: int = 0
    success_count: int = 0
    error_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    errors: List[Dict[str, Any]] = []
    metadata: Dict[str, Any] = {}
    created_by: str  # User ID who initiated the import

# Link Import Models
class LinkImportData(BaseModel):
    original_url: str
    short_url: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = "General"
    tags: Optional[List[str]] = []
    custom_domain: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    clicks: int = 0
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    
    @validator('original_url')
    def validate_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v

class LinkImportRequest(BaseModel):
    import_type: ImportType = ImportType.LINKS
    data: List[LinkImportData]
    batch_size: int = 100
    skip_duplicates: bool = True
    update_existing: bool = False

# User Import Models
class UserImportData(BaseModel):
    name: str
    email: str
    password: Optional[str] = None
    user_type: str = "customer"  # customer, admin
    plan: str = "Basic"  # Basic, Pro, Enterprise
    status: str = "active"
    phone: Optional[str] = None
    company: Optional[str] = None
    created_at: Optional[datetime] = None
    custom_domains: Optional[List[str]] = []
    metadata: Dict[str, Any] = {}

class UserImportRequest(BaseModel):
    import_type: ImportType = ImportType.USERS
    data: List[UserImportData]
    send_welcome_email: bool = True
    auto_generate_passwords: bool = True

# Analytics Import Models
class AnalyticsImportData(BaseModel):
    link_id: Optional[str] = None
    short_url: Optional[str] = None
    original_url: Optional[str] = None
    clicks: int = 0
    unique_clicks: int = 0
    click_date: datetime
    country: Optional[str] = None
    city: Optional[str] = None
    device_type: Optional[str] = None
    browser: Optional[str] = None
    os: Optional[str] = None
    referrer: Optional[str] = None
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None

class AnalyticsImportRequest(BaseModel):
    import_type: ImportType = ImportType.ANALYTICS
    data: List[AnalyticsImportData]
    aggregate_duplicates: bool = True

# Domain Import Models
class DomainImportData(BaseModel):
    domain: str
    is_active: bool = True
    ssl_enabled: bool = True
    dns_verified: bool = False
    owner_user_id: Optional[str] = None
    owner_email: Optional[str] = None
    created_at: Optional[datetime] = None
    settings: Dict[str, Any] = {}

class DomainImportRequest(BaseModel):
    import_type: ImportType = ImportType.DOMAINS
    data: List[DomainImportData]
    verify_dns: bool = True
    auto_ssl: bool = True

# Contact Import Models
class ContactImportData(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    company: Optional[str] = None
    position: Optional[str] = None
    tags: Optional[List[str]] = []
    notes: Optional[str] = None
    source: Optional[str] = None
    status: str = "active"
    created_at: Optional[datetime] = None
    metadata: Dict[str, Any] = {}

class ContactImportRequest(BaseModel):
    import_type: ImportType = ImportType.CONTACTS
    data: List[ContactImportData]
    merge_duplicates: bool = True

# Platform Migration Models
class PlatformMigrationData(BaseModel):
    platform: str  # bitly, tinyurl, rebrandly, etc.
    api_key: Optional[str] = None
    access_token: Optional[str] = None
    username: Optional[str] = None
    include_analytics: bool = True
    date_range_start: Optional[datetime] = None
    date_range_end: Optional[datetime] = None
    migrate_custom_domains: bool = True

class PlatformMigrationRequest(BaseModel):
    import_type: ImportType = ImportType.PLATFORM_MIGRATION
    platform_data: PlatformMigrationData
    batch_size: int = 50

# Import Response Models
class ImportResponse(BaseModel):
    job_id: str
    import_type: ImportType
    status: ImportStatus
    message: str
    total_records: int
    estimated_time: Optional[int] = None  # seconds

class ImportStatusResponse(BaseModel):
    job_id: str
    import_type: ImportType
    status: ImportStatus
    progress: float  # 0.0 to 1.0
    total_records: int
    processed_records: int
    success_count: int
    error_count: int
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    errors: List[Dict[str, Any]] = []
    metadata: Dict[str, Any] = {}

# Error Models
class ImportError(BaseModel):
    row_number: int
    field: str
    error: str
    data: Dict[str, Any]
    severity: str = "error"  # error, warning

class ImportValidationResult(BaseModel):
    is_valid: bool
    total_records: int
    valid_records: int
    errors: List[ImportError]
    warnings: List[ImportError]

# File Upload Models
class FileUploadResponse(BaseModel):
    filename: str
    original_filename: str
    size: int
    content_type: str
    upload_id: str
    preview_data: Optional[List[Dict[str, Any]]] = None
    validation_result: Optional[ImportValidationResult] = None

# Batch Processing Models
class BatchProcessingStatus(BaseModel):
    batch_id: str
    total_batches: int
    current_batch: int
    records_per_batch: int
    processed_records: int
    success_count: int
    error_count: int
    estimated_remaining_time: Optional[int] = None

# Export Models (for data export functionality)
class ExportRequest(BaseModel):
    export_type: str  # links, users, analytics, etc.
    format: str = "csv"  # csv, json, excel
    filters: Dict[str, Any] = {}
    include_analytics: bool = False
    date_range_start: Optional[datetime] = None
    date_range_end: Optional[datetime] = None

class ExportResponse(BaseModel):
    export_id: str
    download_url: str
    expires_at: datetime
    file_size: int
    record_count: int