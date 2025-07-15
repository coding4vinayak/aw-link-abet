from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException, Form, BackgroundTasks, Depends
from fastapi.responses import JSONResponse, RedirectResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete, func
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
import aiofiles
import json

# Import database models and session
from database import (
    get_db, create_tables, engine, AsyncSessionLocal,
    StatusCheckTable, UserTable, SubscriptionTable, LinkTable, 
    ImportJobTable, AnalyticsTable, DomainTable, ContactTable
)

# Import Pydantic models
from models import (
    ImportJob, ImportType, ImportStatus, ImportResponse, ImportStatusResponse,
    LinkImportRequest, UserImportRequest, AnalyticsImportRequest,
    DomainImportRequest, ContactImportRequest, PlatformMigrationRequest,
    FileUploadResponse, ImportValidationResult,
    PlanType, PlanLimits, SubscriptionPlan, UserSubscription, User
)

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Create upload directory
UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Define Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate, db: AsyncSession = Depends(get_db)):
    status_obj = StatusCheck(**input.dict())
    
    # Create new status check record
    stmt = insert(StatusCheckTable).values(
        id=status_obj.id,
        client_name=status_obj.client_name,
        timestamp=status_obj.timestamp
    )
    await db.execute(stmt)
    await db.commit()
    
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks(db: AsyncSession = Depends(get_db)):
    # Get all status checks
    stmt = select(StatusCheckTable)
    result = await db.execute(stmt)
    status_checks = result.scalars().all()
    
    return [StatusCheck(
        id=row.id,
        client_name=row.client_name,
        timestamp=row.timestamp
    ) for row in status_checks]

# =====================================================
# SUBSCRIPTION & PLAN ENDPOINTS
# =====================================================

@api_router.get("/subscription/plans", response_model=List[SubscriptionPlan])
async def get_subscription_plans():
    """Get all available subscription plans"""
    plans = [
        SubscriptionPlan(
            name="Basic",
            plan_type=PlanType.BASIC,
            price_monthly=0.0,
            price_yearly=0.0,
            limits=PlanLimits(
                max_links=5,
                max_clicks_per_month=1000,
                custom_domains=False,
                analytics_retention_days=30,
                api_access=False,
                ads_free=False
            ),
            features=[
                "Up to 5 shortened links",
                "Basic analytics (30 days)",
                "Standard support",
                "QR code generation"
            ]
        ),
        SubscriptionPlan(
            name="Pro",
            plan_type=PlanType.PRO,
            price_monthly=9.99,
            price_yearly=99.99,
            limits=PlanLimits(
                max_links=100,
                max_clicks_per_month=100000,
                custom_domains=True,
                analytics_retention_days=365,
                api_access=True,
                ads_free=True
            ),
            features=[
                "Up to 100 shortened links",
                "Advanced analytics (365 days)",
                "Priority support",
                "Custom domains",
                "Ad-free experience",
                "API access",
                "Advanced QR code styling",
                "Bulk operations"
            ]
        )
    ]
    return plans

@api_router.get("/subscription/current/{user_id}", response_model=UserSubscription)
async def get_current_subscription(user_id: str, db: AsyncSession = Depends(get_db)):
    """Get current subscription for a user"""
    # Get active subscription
    stmt = select(SubscriptionTable).where(
        SubscriptionTable.user_id == user_id,
        SubscriptionTable.is_active == True
    )
    result = await db.execute(stmt)
    subscription_row = result.fetchone()
    
    if not subscription_row:
        # Create default basic subscription
        subscription = UserSubscription(
            user_id=user_id,
            plan_type=PlanType.BASIC,
            is_active=True
        )
        
        # Insert new subscription
        stmt = insert(SubscriptionTable).values(
            id=subscription.id,
            user_id=subscription.user_id,
            plan_type=subscription.plan_type,
            is_active=subscription.is_active,
            auto_renew=subscription.auto_renew,
            created_at=subscription.created_at,
            updated_at=subscription.updated_at
        )
        await db.execute(stmt)
        await db.commit()
    else:
        subscription = UserSubscription(
            id=subscription_row.id,
            user_id=subscription_row.user_id,
            plan_type=subscription_row.plan_type,
            plan_expires=subscription_row.plan_expires,
            is_active=subscription_row.is_active,
            auto_renew=subscription_row.auto_renew,
            created_at=subscription_row.created_at,
            updated_at=subscription_row.updated_at
        )
    
    return subscription

@api_router.post("/subscription/upgrade", response_model=UserSubscription)
async def upgrade_subscription(
    user_id: str = Form(...),
    plan_type: PlanType = Form(...),
    payment_method: str = Form(...),
    billing_cycle: str = Form("monthly"),
    db: AsyncSession = Depends(get_db)
):
    """Upgrade user subscription to Pro plan"""
    try:
        # Check if user already has an active subscription
        stmt = select(SubscriptionTable).where(
            SubscriptionTable.user_id == user_id,
            SubscriptionTable.is_active == True
        )
        result = await db.execute(stmt)
        existing_subscription = result.fetchone()
        
        if existing_subscription:
            # Update existing subscription
            update_data = {
                "plan_type": plan_type,
                "updated_at": datetime.utcnow()
            }
            if plan_type == PlanType.PRO:
                # Set expiry to 1 month from now
                update_data["plan_expires"] = datetime.utcnow().replace(month=datetime.utcnow().month + 1)
            
            stmt = update(SubscriptionTable).where(
                SubscriptionTable.user_id == user_id,
                SubscriptionTable.is_active == True
            ).values(**update_data)
            await db.execute(stmt)
            await db.commit()
            
            # Get updated subscription
            stmt = select(SubscriptionTable).where(
                SubscriptionTable.user_id == user_id,
                SubscriptionTable.is_active == True
            )
            result = await db.execute(stmt)
            updated_row = result.fetchone()
            
            subscription = UserSubscription(
                id=updated_row.id,
                user_id=updated_row.user_id,
                plan_type=updated_row.plan_type,
                plan_expires=updated_row.plan_expires,
                is_active=updated_row.is_active,
                auto_renew=updated_row.auto_renew,
                created_at=updated_row.created_at,
                updated_at=updated_row.updated_at
            )
        else:
            # Create new subscription
            subscription = UserSubscription(
                user_id=user_id,
                plan_type=plan_type,
                is_active=True
            )
            if plan_type == PlanType.PRO:
                subscription.plan_expires = datetime.utcnow().replace(month=datetime.utcnow().month + 1)
            
            stmt = insert(SubscriptionTable).values(
                id=subscription.id,
                user_id=subscription.user_id,
                plan_type=subscription.plan_type,
                plan_expires=subscription.plan_expires,
                is_active=subscription.is_active,
                auto_renew=subscription.auto_renew,
                created_at=subscription.created_at,
                updated_at=subscription.updated_at
            )
            await db.execute(stmt)
            await db.commit()
        
        # Update user limits based on plan
        user_limits = {"max_links": 5, "links_created": 0}
        if plan_type == PlanType.PRO:
            user_limits["max_links"] = 100
        
        stmt = update(UserTable).where(UserTable.id == user_id).values(
            plan_type=plan_type,
            plan_expires=subscription.plan_expires,
            max_links=user_limits["max_links"],
            updated_at=datetime.utcnow()
        )
        await db.execute(stmt)
        await db.commit()
        
        return subscription
        
    except Exception as e:
        logger.error(f"Error upgrading subscription: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/subscription/validate-limits")
async def validate_plan_limits(
    user_id: str = Form(...),
    action: str = Form(...),  # "create_link", "access_analytics", etc.
    db: AsyncSession = Depends(get_db)
):
    """Validate if user can perform action based on plan limits"""
    try:
        # Get user
        stmt = select(UserTable).where(UserTable.id == user_id)
        result = await db.execute(stmt)
        user_row = result.fetchone()
        
        if not user_row:
            raise HTTPException(status_code=404, detail="User not found")
        
        if action == "create_link":
            if user_row.plan_type == "basic" and user_row.links_created >= 5:
                return {
                    "allowed": False,
                    "message": "You've reached your link limit. Upgrade to Pro for up to 100 links.",
                    "current_usage": user_row.links_created,
                    "limit": 5
                }
            elif user_row.plan_type == "pro" and user_row.links_created >= 100:
                return {
                    "allowed": False,
                    "message": "You've reached your Pro plan limit of 100 links.",
                    "current_usage": user_row.links_created,
                    "limit": 100
                }
        
        elif action == "access_analytics":
            if user_row.plan_type == "basic":
                return {
                    "allowed": True,
                    "message": "Basic analytics (30 days) available",
                    "retention_days": 30
                }
            else:
                return {
                    "allowed": True,
                    "message": "Advanced analytics (365 days) available",
                    "retention_days": 365
                }
        
        elif action == "custom_domain":
            if user_row.plan_type == "basic":
                return {
                    "allowed": False,
                    "message": "Custom domains are available with Pro plan"
                }
        
        return {
            "allowed": True,
            "message": "Action allowed",
            "current_usage": user_row.links_created,
            "limit": user_row.max_links
        }
        
    except Exception as e:
        logger.error(f"Error validating plan limits: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/subscription/increment-usage")
async def increment_usage(
    user_id: str = Form(...),
    action: str = Form(...),  # "link_created", "api_call", etc.
    db: AsyncSession = Depends(get_db)
):
    """Increment user usage counters"""
    try:
        if action == "link_created":
            stmt = update(UserTable).where(UserTable.id == user_id).values(
                links_created=UserTable.links_created + 1
            )
            await db.execute(stmt)
            await db.commit()
        
        return {"success": True, "message": "Usage incremented"}
        
    except Exception as e:
        logger.error(f"Error incrementing usage: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =====================================================
# BASIC IMPORT ENDPOINTS (Simplified for initial migration)
# =====================================================

@api_router.post("/import/jobs", response_model=ImportResponse)
async def create_import_job(
    import_type: ImportType = Form(...),
    filename: str = Form(...),
    created_by: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    """Create a new import job"""
    try:
        job = ImportJob(
            import_type=import_type,
            filename=filename,
            original_filename=filename,
            created_by=created_by
        )
        
        # Insert import job
        stmt = insert(ImportJobTable).values(
            id=job.id,
            import_type=job.import_type,
            filename=job.filename,
            original_filename=job.original_filename,
            status=job.status,
            created_by=job.created_by,
            created_at=job.created_at,
            updated_at=job.updated_at
        )
        await db.execute(stmt)
        await db.commit()
        
        return ImportResponse(
            job_id=job.id,
            import_type=job.import_type,
            status=job.status,
            message="Import job created successfully",
            total_records=0,
            estimated_time=60
        )
        
    except Exception as e:
        logger.error(f"Error creating import job: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/import/jobs", response_model=List[ImportStatusResponse])
async def get_import_jobs(
    created_by: str = None,
    import_type: ImportType = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """Get import jobs with optional filters"""
    try:
        stmt = select(ImportJobTable)
        
        if created_by:
            stmt = stmt.where(ImportJobTable.created_by == created_by)
        if import_type:
            stmt = stmt.where(ImportJobTable.import_type == import_type)
        
        stmt = stmt.limit(limit)
        
        result = await db.execute(stmt)
        jobs = result.scalars().all()
        
        return [
            ImportStatusResponse(
                job_id=job.id,
                import_type=job.import_type,
                status=job.status,
                progress=job.processed_records / job.total_records if job.total_records > 0 else 0,
                total_records=job.total_records,
                processed_records=job.processed_records,
                success_count=job.success_count,
                error_count=job.error_count,
                created_at=job.created_at,
                updated_at=job.updated_at,
                completed_at=job.completed_at,
                errors=job.errors or [],
                metadata=job.job_metadata or {}
            )
            for job in jobs
        ]
        
    except Exception as e:
        logger.error(f"Error getting import jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/import/jobs/{job_id}", response_model=ImportStatusResponse)
async def get_import_job_status(job_id: str, db: AsyncSession = Depends(get_db)):
    """Get specific import job status"""
    try:
        stmt = select(ImportJobTable).where(ImportJobTable.id == job_id)
        result = await db.execute(stmt)
        job = result.scalar_one_or_none()
        
        if not job:
            raise HTTPException(status_code=404, detail="Import job not found")
        
        return ImportStatusResponse(
            job_id=job.id,
            import_type=job.import_type,
            status=job.status,
            progress=job.processed_records / job.total_records if job.total_records > 0 else 0,
            total_records=job.total_records,
            processed_records=job.processed_records,
            success_count=job.success_count,
            error_count=job.error_count,
            created_at=job.created_at,
            updated_at=job.updated_at,
            completed_at=job.completed_at,
            errors=job.errors or [],
            metadata=job.job_metadata or {}
        )
        
    except Exception as e:
        logger.error(f"Error getting import job status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/import/jobs/{job_id}")
async def delete_import_job(job_id: str, db: AsyncSession = Depends(get_db)):
    """Delete an import job"""
    try:
        stmt = delete(ImportJobTable).where(ImportJobTable.id == job_id)
        await db.execute(stmt)
        await db.commit()
        
        return {"message": "Import job deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting import job: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =====================================================
# USER MANAGEMENT ENDPOINTS
# =====================================================

@api_router.get("/users", response_model=List[User])
async def get_users(db: AsyncSession = Depends(get_db)):
    """Get all users"""
    try:
        stmt = select(UserTable)
        result = await db.execute(stmt)
        users = result.scalars().all()
        
        return [
            User(
                id=user.id,
                email=user.email,
                name=user.name,
                user_type=user.user_type,
                plan_type=user.plan_type,
                plan_expires=user.plan_expires,
                max_links=user.max_links,
                links_created=user.links_created,
                features_enabled=user.features_enabled,
                is_active=user.is_active,
                created_at=user.created_at,
                updated_at=user.updated_at
            )
            for user in users
        ]
        
    except Exception as e:
        logger.error(f"Error getting users: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/users/{user_id}", response_model=User)
async def get_user(user_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific user"""
    try:
        stmt = select(UserTable).where(UserTable.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        return User(
            id=user.id,
            email=user.email,
            name=user.name,
            user_type=user.user_type,
            plan_type=user.plan_type,
            plan_expires=user.plan_expires,
            max_links=user.max_links,
            links_created=user.links_created,
            features_enabled=user.features_enabled,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/users/{user_id}", response_model=User)
async def update_user(
    user_id: str,
    name: str = Form(...),
    email: str = Form(...),
    user_type: str = Form(...),
    plan_type: str = Form(...),
    max_links: int = Form(...),
    is_active: bool = Form(...),
    db: AsyncSession = Depends(get_db)
):
    """Update a user"""
    try:
        stmt = select(UserTable).where(UserTable.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        # Update user fields
        update_stmt = update(UserTable).where(UserTable.id == user_id).values(
            name=name,
            email=email,
            user_type=user_type,
            plan_type=plan_type,
            max_links=max_links,
            is_active=is_active,
            updated_at=datetime.utcnow()
        )
        
        await db.execute(update_stmt)
        await db.commit()
        
        # Return updated user
        stmt = select(UserTable).where(UserTable.id == user_id)
        result = await db.execute(stmt)
        updated_user = result.scalar_one()
        
        return User(
            id=updated_user.id,
            email=updated_user.email,
            name=updated_user.name,
            user_type=updated_user.user_type,
            plan_type=updated_user.plan_type,
            plan_expires=updated_user.plan_expires,
            max_links=updated_user.max_links,
            links_created=updated_user.links_created,
            features_enabled=updated_user.features_enabled,
            is_active=updated_user.is_active,
            created_at=updated_user.created_at,
            updated_at=updated_user.updated_at
        )
        
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/users/{user_id}/suspend")
async def suspend_user(user_id: str, db: AsyncSession = Depends(get_db)):
    """Suspend a user"""
    try:
        stmt = select(UserTable).where(UserTable.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        # Update user status
        update_stmt = update(UserTable).where(UserTable.id == user_id).values(
            is_active=False,
            updated_at=datetime.utcnow()
        )
        
        await db.execute(update_stmt)
        await db.commit()
        
        return {"message": "User suspended successfully"}
        
    except Exception as e:
        logger.error(f"Error suspending user: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/users/{user_id}/activate")
async def activate_user(user_id: str, db: AsyncSession = Depends(get_db)):
    """Activate a user"""
    try:
        stmt = select(UserTable).where(UserTable.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        # Update user status
        update_stmt = update(UserTable).where(UserTable.id == user_id).values(
            is_active=True,
            updated_at=datetime.utcnow()
        )
        
        await db.execute(update_stmt)
        await db.commit()
        
        return {"message": "User activated successfully"}
        
    except Exception as e:
        logger.error(f"Error activating user: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =====================================================
# LINK MANAGEMENT ENDPOINTS
# =====================================================

class LinkCreate(BaseModel):
    original_url: str
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = "General"
    custom_domain: Optional[str] = None
    user_id: Optional[str] = None
    user_email: Optional[str] = None

class LinkResponse(BaseModel):
    id: str
    original_url: str
    short_url: str
    title: Optional[str] = None
    description: Optional[str] = None
    category: str
    custom_domain: Optional[str] = None
    is_active: bool
    clicks: int
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    created_at: datetime
    updated_at: datetime

def generate_short_code():
    """Generate a unique short code for URLs"""
    import random
    import string
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))

@api_router.post("/links", response_model=LinkResponse)
async def create_link(link: LinkCreate, db: AsyncSession = Depends(get_db)):
    """Create a new short link"""
    try:
        # Generate unique short code
        short_code = generate_short_code()
        
        # Check if short code already exists
        while True:
            stmt = select(LinkTable).where(LinkTable.short_url.like(f"%{short_code}%"))
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()
            if not existing:
                break
            short_code = generate_short_code()
        
        # Create short URL using backend domain and API endpoint
        backend_domain = "https://a607128e-f79c-4214-bb20-5cec9f7a82ee.preview.emergentagent.com"
        short_url = f"{backend_domain}/api/redirect/{short_code}"
        
        # Create new link
        new_link = LinkTable(
            id=str(uuid.uuid4()),
            original_url=link.original_url,
            short_url=short_url,
            title=link.title,
            description=link.description,
            category=link.category,
            custom_domain=link.custom_domain,
            user_id=link.user_id,
            user_email=link.user_email,
            is_active=True,
            clicks=0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(new_link)
        await db.commit()
        await db.refresh(new_link)
        
        return LinkResponse(
            id=new_link.id,
            original_url=new_link.original_url,
            short_url=new_link.short_url,
            title=new_link.title,
            description=new_link.description,
            category=new_link.category,
            custom_domain=new_link.custom_domain,
            is_active=new_link.is_active,
            clicks=new_link.clicks,
            user_id=new_link.user_id,
            user_email=new_link.user_email,
            created_at=new_link.created_at,
            updated_at=new_link.updated_at
        )
        
    except Exception as e:
        logger.error(f"Error creating link: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/links", response_model=List[LinkResponse])
async def get_links(
    user_id: Optional[str] = None,
    user_email: Optional[str] = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get links with optional filters"""
    try:
        stmt = select(LinkTable)
        
        if user_id:
            stmt = stmt.where(LinkTable.user_id == user_id)
        elif user_email:
            stmt = stmt.where(LinkTable.user_email == user_email)
        
        stmt = stmt.limit(limit).order_by(LinkTable.created_at.desc())
        
        result = await db.execute(stmt)
        links = result.scalars().all()
        
        return [
            LinkResponse(
                id=link.id,
                original_url=link.original_url,
                short_url=link.short_url,
                title=link.title,
                description=link.description,
                category=link.category,
                custom_domain=link.custom_domain,
                is_active=link.is_active,
                clicks=link.clicks,
                user_id=link.user_id,
                user_email=link.user_email,
                created_at=link.created_at,
                updated_at=link.updated_at
            )
            for link in links
        ]
        
    except Exception as e:
        logger.error(f"Error getting links: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/links/{link_id}", response_model=LinkResponse)
async def get_link(link_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific link"""
    try:
        stmt = select(LinkTable).where(LinkTable.id == link_id)
        result = await db.execute(stmt)
        link = result.scalar_one_or_none()
        
        if not link:
            raise HTTPException(status_code=404, detail="Link not found")
            
        return LinkResponse(
            id=link.id,
            original_url=link.original_url,
            short_url=link.short_url,
            title=link.title,
            description=link.description,
            category=link.category,
            custom_domain=link.custom_domain,
            is_active=link.is_active,
            clicks=link.clicks,
            user_id=link.user_id,
            user_email=link.user_email,
            created_at=link.created_at,
            updated_at=link.updated_at
        )
        
    except Exception as e:
        logger.error(f"Error getting link: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/links/{link_id}/toggle")
async def toggle_link(link_id: str, db: AsyncSession = Depends(get_db)):
    """Toggle link active status"""
    try:
        stmt = select(LinkTable).where(LinkTable.id == link_id)
        result = await db.execute(stmt)
        link = result.scalar_one_or_none()
        
        if not link:
            raise HTTPException(status_code=404, detail="Link not found")
            
        # Toggle active status
        update_stmt = update(LinkTable).where(LinkTable.id == link_id).values(
            is_active=not link.is_active,
            updated_at=datetime.utcnow()
        )
        
        await db.execute(update_stmt)
        await db.commit()
        
        return {"message": f"Link {'activated' if not link.is_active else 'deactivated'} successfully"}
        
    except Exception as e:
        logger.error(f"Error toggling link: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/links/{link_id}")
async def delete_link(link_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a link"""
    try:
        stmt = delete(LinkTable).where(LinkTable.id == link_id)
        result = await db.execute(stmt)
        
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Link not found")
            
        await db.commit()
        
        return {"message": "Link deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting link: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =====================================================
# REDIRECT ENDPOINT (Critical for link shortening)
# =====================================================

from fastapi.responses import RedirectResponse

@api_router.get("/redirect/{short_code}")
async def redirect_link(short_code: str, db: AsyncSession = Depends(get_db)):
    """Redirect short URL to original URL"""
    try:
        # Look for link with this short code
        stmt = select(LinkTable).where(LinkTable.short_url.like(f"%{short_code}%"))
        result = await db.execute(stmt)
        link = result.scalar_one_or_none()
        
        if not link or not link.is_active:
            raise HTTPException(status_code=404, detail="Link not found or inactive")
            
        # Increment click count
        update_stmt = update(LinkTable).where(LinkTable.id == link.id).values(
            clicks=link.clicks + 1,
            updated_at=datetime.utcnow()
        )
        await db.execute(update_stmt)
        await db.commit()
        
        # Log analytics
        analytics_record = AnalyticsTable(
            id=str(uuid.uuid4()),
            link_id=link.id,
            short_url=link.short_url,
            original_url=link.original_url,
            clicks=1,
            unique_clicks=1,
            click_date=datetime.utcnow(),
            created_at=datetime.utcnow()
        )
        db.add(analytics_record)
        await db.commit()
        
        # Redirect to original URL
        return RedirectResponse(url=link.original_url, status_code=302)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error redirecting link: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =====================================================
# DIRECT REDIRECT ENDPOINT (for short URLs)
# =====================================================

@app.get("/go/{short_code}")
async def direct_redirect(short_code: str, db: AsyncSession = Depends(get_db)):
    """Direct redirect endpoint for short URLs"""
    try:
        # Look for link with this short code
        stmt = select(LinkTable).where(LinkTable.short_url.like(f"%{short_code}%"))
        result = await db.execute(stmt)
        link = result.scalar_one_or_none()
        
        if not link or not link.is_active:
            raise HTTPException(status_code=404, detail="Link not found or inactive")
            
        # Increment click count
        update_stmt = update(LinkTable).where(LinkTable.id == link.id).values(
            clicks=link.clicks + 1,
            updated_at=datetime.utcnow()
        )
        await db.execute(update_stmt)
        await db.commit()
        
        # Log analytics
        analytics_record = AnalyticsTable(
            id=str(uuid.uuid4()),
            link_id=link.id,
            short_url=link.short_url,
            original_url=link.original_url,
            clicks=1,
            unique_clicks=1,
            click_date=datetime.utcnow(),
            created_at=datetime.utcnow()
        )
        db.add(analytics_record)
        await db.commit()
        
        # Redirect to original URL
        return RedirectResponse(url=link.original_url, status_code=302)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error redirecting link: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    """Create database tables on startup and seed sample data"""
    try:
        await create_tables()
        logger.info("Database tables created successfully")
        
        # Seed sample users for testing
        await seed_sample_data()
        logger.info("Sample data seeded successfully")
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")

async def seed_sample_data():
    """Seed sample users for testing"""
    try:
        async with AsyncSessionLocal() as db:
            # Check if users already exist
            stmt = select(UserTable).limit(1)
            result = await db.execute(stmt)
            existing_user = result.scalar_one_or_none()
            
            if not existing_user:
                # Create sample users
                sample_users = [
                    UserTable(
                        id=str(uuid.uuid4()),
                        email='john@example.com',
                        name='John Doe',
                        user_type='customer',
                        plan_type='basic',
                        max_links=5,
                        links_created=0,
                        is_active=True,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    ),
                    UserTable(
                        id=str(uuid.uuid4()),
                        email='sarah@example.com',
                        name='Sarah Wilson',
                        user_type='customer',
                        plan_type='pro',
                        max_links=100,
                        links_created=0,
                        is_active=True,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    ),
                    UserTable(
                        id=str(uuid.uuid4()),
                        email='admin@linkly.com',
                        name='Admin User',
                        user_type='admin',
                        plan_type='pro',
                        max_links=1000,
                        links_created=0,
                        is_active=True,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    ),
                    UserTable(
                        id=str(uuid.uuid4()),
                        email='mike@example.com',
                        name='Mike Johnson',
                        user_type='customer',
                        plan_type='basic',
                        max_links=5,
                        links_created=0,
                        is_active=False,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                ]
                
                for user in sample_users:
                    db.add(user)
                
                await db.commit()
                logger.info("Sample users created successfully")
                
    except Exception as e:
        logger.error(f"Error seeding sample data: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connections on shutdown"""
    try:
        await engine.dispose()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")