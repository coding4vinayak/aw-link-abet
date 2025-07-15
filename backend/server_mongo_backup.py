from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException, Form, BackgroundTasks
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
import aiofiles
import json
from models import (
    ImportJob, ImportType, ImportStatus, ImportResponse, ImportStatusResponse,
    LinkImportRequest, UserImportRequest, AnalyticsImportRequest,
    DomainImportRequest, ContactImportRequest, PlatformMigrationRequest,
    FileUploadResponse, ImportValidationResult,
    PlanType, PlanLimits, SubscriptionPlan, UserSubscription, User
)
from import_services import (
    ImportService, FileProcessor, DataValidator, DataProcessor,
    PlatformMigrationService
)


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Initialize services
import_service = ImportService(db)
file_processor = FileProcessor()
data_validator = DataValidator()
data_processor = DataProcessor(db)
platform_migration_service = PlatformMigrationService(db)

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
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

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
async def get_current_subscription(user_id: str):
    """Get current subscription for a user"""
    subscription = await db.subscriptions.find_one({"user_id": user_id, "is_active": True})
    if not subscription:
        # Return default basic subscription
        subscription = UserSubscription(
            user_id=user_id,
            plan_type=PlanType.BASIC,
            is_active=True
        )
        await db.subscriptions.insert_one(subscription.dict())
    else:
        subscription = UserSubscription(**subscription)
    return subscription

@api_router.post("/subscription/upgrade", response_model=UserSubscription)
async def upgrade_subscription(
    user_id: str = Form(...),
    plan_type: PlanType = Form(...),
    payment_method: str = Form(...),
    billing_cycle: str = Form("monthly")
):
    """Upgrade user subscription to Pro plan"""
    try:
        # Check if user already has an active subscription
        existing_subscription = await db.subscriptions.find_one({"user_id": user_id, "is_active": True})
        
        if existing_subscription:
            # Update existing subscription
            update_data = {
                "plan_type": plan_type,
                "updated_at": datetime.utcnow()
            }
            if plan_type == PlanType.PRO:
                # Set expiry to 1 month from now (in real app, handle payment processing)
                update_data["plan_expires"] = datetime.utcnow().replace(month=datetime.utcnow().month + 1)
            
            await db.subscriptions.update_one(
                {"user_id": user_id, "is_active": True},
                {"$set": update_data}
            )
            
            updated_subscription = await db.subscriptions.find_one({"user_id": user_id, "is_active": True})
            subscription = UserSubscription(**updated_subscription)
        else:
            # Create new subscription
            subscription = UserSubscription(
                user_id=user_id,
                plan_type=plan_type,
                is_active=True
            )
            if plan_type == PlanType.PRO:
                subscription.plan_expires = datetime.utcnow().replace(month=datetime.utcnow().month + 1)
            
            await db.subscriptions.insert_one(subscription.dict())
        
        # Update user limits based on plan
        user_limits = {"max_links": 5, "links_created": 0}
        if plan_type == PlanType.PRO:
            user_limits["max_links"] = 100
        
        await db.users.update_one(
            {"id": user_id},
            {"$set": {
                "plan_type": plan_type,
                "plan_expires": subscription.plan_expires,
                "max_links": user_limits["max_links"],
                "updated_at": datetime.utcnow()
            }}
        )
        
        return subscription
        
    except Exception as e:
        logger.error(f"Error upgrading subscription: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/subscription/validate-limits")
async def validate_plan_limits(
    user_id: str = Form(...),
    action: str = Form(...),  # "create_link", "access_analytics", etc.
):
    """Validate if user can perform action based on plan limits"""
    try:
        user = await db.users.find_one({"id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_obj = User(**user)
        
        if action == "create_link":
            if user_obj.plan_type == PlanType.BASIC and user_obj.links_created >= 5:
                return {
                    "allowed": False,
                    "message": "You've reached your link limit. Upgrade to Pro for up to 100 links.",
                    "current_usage": user_obj.links_created,
                    "limit": 5
                }
            elif user_obj.plan_type == PlanType.PRO and user_obj.links_created >= 100:
                return {
                    "allowed": False,
                    "message": "You've reached your Pro plan limit of 100 links.",
                    "current_usage": user_obj.links_created,
                    "limit": 100
                }
        
        elif action == "access_analytics":
            if user_obj.plan_type == PlanType.BASIC:
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
            if user_obj.plan_type == PlanType.BASIC:
                return {
                    "allowed": False,
                    "message": "Custom domains are available with Pro plan"
                }
        
        return {
            "allowed": True,
            "message": "Action allowed",
            "current_usage": user_obj.links_created,
            "limit": user_obj.max_links
        }
        
    except Exception as e:
        logger.error(f"Error validating plan limits: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/subscription/increment-usage")
async def increment_usage(
    user_id: str = Form(...),
    action: str = Form(...)  # "link_created", "api_call", etc.
):
    """Increment user usage counters"""
    try:
        if action == "link_created":
            await db.users.update_one(
                {"id": user_id},
                {"$inc": {"links_created": 1}}
            )
        
        return {"success": True, "message": "Usage incremented"}
        
    except Exception as e:
        logger.error(f"Error incrementing usage: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =====================================================
# DATA IMPORT ENDPOINTS
# =====================================================

@api_router.post("/import/upload", response_model=FileUploadResponse)
async def upload_import_file(
    file: UploadFile = File(...),
    import_type: ImportType = Form(...),
    created_by: str = Form(...)
):
    """Upload a file for import and validate its format"""
    try:
        # Validate file size (max 10MB)
        if file.size > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size exceeds 10MB limit")
        
        # Read file content
        content = await file.read()
        
        # Detect file format
        file_format = file_processor.detect_file_format(file.filename, file.content_type)
        
        # Parse file content
        if file_format == 'csv':
            parsed_data = file_processor.parse_csv_file(content)
        elif file_format == 'excel':
            parsed_data = file_processor.parse_excel_file(content)
        elif file_format == 'json':
            parsed_data = file_processor.parse_json_file(content)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file format: {file_format}")
        
        # Validate data based on import type
        if import_type == ImportType.LINKS:
            validation_result = data_validator.validate_links_data(parsed_data)
        elif import_type == ImportType.USERS:
            validation_result = data_validator.validate_users_data(parsed_data)
        elif import_type == ImportType.ANALYTICS:
            validation_result = data_validator.validate_analytics_data(parsed_data)
        else:
            validation_result = ImportValidationResult(
                is_valid=True,
                total_records=len(parsed_data),
                valid_records=len(parsed_data),
                errors=[],
                warnings=[]
            )
        
        # Save file
        upload_id = str(uuid.uuid4())
        filename = f"{upload_id}_{file.filename}"
        file_path = UPLOAD_DIR / filename
        
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
        # Get preview data (first 5 rows)
        preview_data = parsed_data[:5] if len(parsed_data) > 0 else []
        
        return FileUploadResponse(
            filename=filename,
            original_filename=file.filename,
            size=file.size,
            content_type=file.content_type,
            upload_id=upload_id,
            preview_data=preview_data,
            validation_result=validation_result
        )
        
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/import/links", response_model=ImportResponse)
async def import_links(
    background_tasks: BackgroundTasks,
    filename: str = Form(...),
    created_by: str = Form(...),
    skip_duplicates: bool = Form(True),
    update_existing: bool = Form(False)
):
    """Import links from uploaded file"""
    try:
        # Create import job
        job = await import_service.create_import_job(
            import_type=ImportType.LINKS,
            filename=filename,
            original_filename=filename,
            created_by=created_by
        )
        
        # Add background task to process import
        background_tasks.add_task(
            process_links_import, 
            job.id, 
            filename, 
            skip_duplicates, 
            update_existing
        )
        
        return ImportResponse(
            job_id=job.id,
            import_type=ImportType.LINKS,
            status=ImportStatus.PROCESSING,
            message="Links import started",
            total_records=0,
            estimated_time=60
        )
        
    except Exception as e:
        logger.error(f"Error starting links import: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/import/users", response_model=ImportResponse)
async def import_users(
    background_tasks: BackgroundTasks,
    filename: str = Form(...),
    created_by: str = Form(...),
    send_welcome_email: bool = Form(True),
    auto_generate_passwords: bool = Form(True)
):
    """Import users from uploaded file"""
    try:
        # Create import job
        job = await import_service.create_import_job(
            import_type=ImportType.USERS,
            filename=filename,
            original_filename=filename,
            created_by=created_by
        )
        
        # Add background task to process import
        background_tasks.add_task(
            process_users_import, 
            job.id, 
            filename, 
            send_welcome_email, 
            auto_generate_passwords
        )
        
        return ImportResponse(
            job_id=job.id,
            import_type=ImportType.USERS,
            status=ImportStatus.PROCESSING,
            message="Users import started",
            total_records=0,
            estimated_time=120
        )
        
    except Exception as e:
        logger.error(f"Error starting users import: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/import/analytics", response_model=ImportResponse)
async def import_analytics(
    background_tasks: BackgroundTasks,
    filename: str = Form(...),
    created_by: str = Form(...),
    aggregate_duplicates: bool = Form(True)
):
    """Import analytics data from uploaded file"""
    try:
        # Create import job
        job = await import_service.create_import_job(
            import_type=ImportType.ANALYTICS,
            filename=filename,
            original_filename=filename,
            created_by=created_by
        )
        
        # Add background task to process import
        background_tasks.add_task(
            process_analytics_import, 
            job.id, 
            filename, 
            aggregate_duplicates
        )
        
        return ImportResponse(
            job_id=job.id,
            import_type=ImportType.ANALYTICS,
            status=ImportStatus.PROCESSING,
            message="Analytics import started",
            total_records=0,
            estimated_time=90
        )
        
    except Exception as e:
        logger.error(f"Error starting analytics import: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/import/platform-migration", response_model=ImportResponse)
async def import_from_platform(
    background_tasks: BackgroundTasks,
    platform: str = Form(...),
    api_key: str = Form(None),
    access_token: str = Form(None),
    created_by: str = Form(...),
    include_analytics: bool = Form(True)
):
    """Import data from other platforms (Bitly, Rebrandly, etc.)"""
    try:
        # Create import job
        job = await import_service.create_import_job(
            import_type=ImportType.PLATFORM_MIGRATION,
            filename=f"{platform}_migration",
            original_filename=f"{platform}_migration",
            created_by=created_by
        )
        
        # Add background task to process migration
        background_tasks.add_task(
            process_platform_migration, 
            job.id, 
            platform, 
            api_key, 
            access_token, 
            include_analytics
        )
        
        return ImportResponse(
            job_id=job.id,
            import_type=ImportType.PLATFORM_MIGRATION,
            status=ImportStatus.PROCESSING,
            message=f"Platform migration from {platform} started",
            total_records=0,
            estimated_time=180
        )
        
    except Exception as e:
        logger.error(f"Error starting platform migration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/import/jobs", response_model=List[ImportStatusResponse])
async def get_import_jobs(
    created_by: str = None,
    import_type: ImportType = None,
    limit: int = 50
):
    """Get import jobs with optional filters"""
    try:
        jobs = await import_service.get_import_jobs(
            created_by=created_by,
            import_type=import_type,
            limit=limit
        )
        
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
                errors=job.errors,
                metadata=job.metadata
            )
            for job in jobs
        ]
        
    except Exception as e:
        logger.error(f"Error getting import jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/import/jobs/{job_id}", response_model=ImportStatusResponse)
async def get_import_job_status(job_id: str):
    """Get specific import job status"""
    try:
        job = await import_service.get_import_job(job_id)
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
            errors=job.errors,
            metadata=job.metadata
        )
        
    except Exception as e:
        logger.error(f"Error getting import job status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/import/jobs/{job_id}")
async def delete_import_job(job_id: str):
    """Delete an import job"""
    try:
        await db.import_jobs.delete_one({"id": job_id})
        return {"message": "Import job deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting import job: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =====================================================
# BACKGROUND TASK FUNCTIONS
# =====================================================

async def process_links_import(job_id: str, filename: str, skip_duplicates: bool, update_existing: bool):
    """Background task to process links import"""
    try:
        # Update job status
        await import_service.update_import_job(job_id, {"status": ImportStatus.PROCESSING})
        
        # Read file
        file_path = UPLOAD_DIR / filename
        async with aiofiles.open(file_path, 'rb') as f:
            content = await f.read()
        
        # Parse file
        if filename.endswith('.csv'):
            parsed_data = file_processor.parse_csv_file(content)
        elif filename.endswith(('.xlsx', '.xls')):
            parsed_data = file_processor.parse_excel_file(content)
        else:
            parsed_data = file_processor.parse_json_file(content)
        
        # Update total records
        await import_service.update_import_job(job_id, {"total_records": len(parsed_data)})
        
        # Process data
        result = await data_processor.process_links_import(parsed_data, job_id, skip_duplicates)
        
        # Update job completion
        await import_service.update_import_job(job_id, {
            "status": ImportStatus.COMPLETED,
            "processed_records": result["processed_count"],
            "success_count": result["success_count"],
            "error_count": result["error_count"],
            "completed_at": datetime.utcnow()
        })
        
    except Exception as e:
        logger.error(f"Error processing links import: {e}")
        await import_service.update_import_job(job_id, {
            "status": ImportStatus.FAILED,
            "errors": [{"error": str(e)}]
        })

async def process_users_import(job_id: str, filename: str, send_welcome_email: bool, auto_generate_passwords: bool):
    """Background task to process users import"""
    try:
        # Update job status
        await import_service.update_import_job(job_id, {"status": ImportStatus.PROCESSING})
        
        # Read file
        file_path = UPLOAD_DIR / filename
        async with aiofiles.open(file_path, 'rb') as f:
            content = await f.read()
        
        # Parse file
        if filename.endswith('.csv'):
            parsed_data = file_processor.parse_csv_file(content)
        elif filename.endswith(('.xlsx', '.xls')):
            parsed_data = file_processor.parse_excel_file(content)
        else:
            parsed_data = file_processor.parse_json_file(content)
        
        # Update total records
        await import_service.update_import_job(job_id, {"total_records": len(parsed_data)})
        
        # Process data
        result = await data_processor.process_users_import(parsed_data, job_id, auto_generate_passwords)
        
        # Update job completion
        await import_service.update_import_job(job_id, {
            "status": ImportStatus.COMPLETED,
            "processed_records": result["processed_count"],
            "success_count": result["success_count"],
            "error_count": result["error_count"],
            "completed_at": datetime.utcnow()
        })
        
    except Exception as e:
        logger.error(f"Error processing users import: {e}")
        await import_service.update_import_job(job_id, {
            "status": ImportStatus.FAILED,
            "errors": [{"error": str(e)}]
        })

async def process_analytics_import(job_id: str, filename: str, aggregate_duplicates: bool):
    """Background task to process analytics import"""
    try:
        # Update job status
        await import_service.update_import_job(job_id, {"status": ImportStatus.PROCESSING})
        
        # Read file
        file_path = UPLOAD_DIR / filename
        async with aiofiles.open(file_path, 'rb') as f:
            content = await f.read()
        
        # Parse file
        if filename.endswith('.csv'):
            parsed_data = file_processor.parse_csv_file(content)
        elif filename.endswith(('.xlsx', '.xls')):
            parsed_data = file_processor.parse_excel_file(content)
        else:
            parsed_data = file_processor.parse_json_file(content)
        
        # Update total records
        await import_service.update_import_job(job_id, {"total_records": len(parsed_data)})
        
        # Process data
        result = await data_processor.process_analytics_import(parsed_data, job_id)
        
        # Update job completion
        await import_service.update_import_job(job_id, {
            "status": ImportStatus.COMPLETED,
            "processed_records": result["processed_count"],
            "success_count": result["success_count"],
            "error_count": result["error_count"],
            "completed_at": datetime.utcnow()
        })
        
    except Exception as e:
        logger.error(f"Error processing analytics import: {e}")
        await import_service.update_import_job(job_id, {
            "status": ImportStatus.FAILED,
            "errors": [{"error": str(e)}]
        })

async def process_platform_migration(job_id: str, platform: str, api_key: str, access_token: str, include_analytics: bool):
    """Background task to process platform migration"""
    try:
        # Update job status
        await import_service.update_import_job(job_id, {"status": ImportStatus.PROCESSING})
        
        # Prepare migration data
        migration_data = {
            "platform": platform,
            "api_key": api_key,
            "access_token": access_token,
            "include_analytics": include_analytics
        }
        
        # Process migration based on platform
        if platform.lower() == "bitly":
            result = await platform_migration_service.migrate_from_bitly(migration_data)
        elif platform.lower() == "rebrandly":
            result = await platform_migration_service.migrate_from_rebrandly(migration_data)
        else:
            result = {"success": False, "error": f"Platform {platform} not supported"}
        
        if result["success"]:
            # Process migrated links
            links_result = await data_processor.process_links_import(result["links"], job_id, True)
            
            # Update job completion
            await import_service.update_import_job(job_id, {
                "status": ImportStatus.COMPLETED,
                "total_records": result["total_count"],
                "processed_records": links_result["processed_count"],
                "success_count": links_result["success_count"],
                "error_count": links_result["error_count"],
                "completed_at": datetime.utcnow()
            })
        else:
            # Update job failure
            await import_service.update_import_job(job_id, {
                "status": ImportStatus.FAILED,
                "errors": [{"error": result["error"]}]
            })
        
    except Exception as e:
        logger.error(f"Error processing platform migration: {e}")
        await import_service.update_import_job(job_id, {
            "status": ImportStatus.FAILED,
            "errors": [{"error": str(e)}]
        })

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

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
