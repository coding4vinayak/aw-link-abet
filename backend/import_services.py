from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete
from database import ImportJobTable, UserTable, LinkTable, AnalyticsTable
from models import ImportJob, ImportType, ImportStatus
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
import logging
import pandas as pd
import json
import csv
import io

logger = logging.getLogger(__name__)

class ImportService:
    """Service for managing import operations with PostgreSQL"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_import_job(
        self,
        import_type: ImportType,
        filename: str,
        original_filename: str,
        created_by: str
    ) -> ImportJob:
        """Create a new import job"""
        job = ImportJob(
            import_type=import_type,
            filename=filename,
            original_filename=original_filename,
            created_by=created_by
        )
        
        # Insert into database
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
        await self.db.execute(stmt)
        await self.db.commit()
        
        return job
    
    async def get_import_job(self, job_id: str) -> Optional[ImportJob]:
        """Get import job by ID"""
        stmt = select(ImportJobTable).where(ImportJobTable.id == job_id)
        result = await self.db.execute(stmt)
        job_row = result.fetchone()
        
        if job_row:
            return ImportJob(
                id=job_row.id,
                import_type=job_row.import_type,
                filename=job_row.filename,
                original_filename=job_row.original_filename,
                status=job_row.status,
                total_records=job_row.total_records,
                processed_records=job_row.processed_records,
                success_count=job_row.success_count,
                error_count=job_row.error_count,
                created_at=job_row.created_at,
                updated_at=job_row.updated_at,
                completed_at=job_row.completed_at,
                errors=job_row.errors or [],
                metadata=job_row.job_metadata or {},  # Use job_metadata column
                created_by=job_row.created_by
            )
        return None
    
    async def get_import_jobs(
        self,
        created_by: Optional[str] = None,
        import_type: Optional[ImportType] = None,
        limit: int = 50
    ) -> List[ImportJob]:
        """Get import jobs with filters"""
        stmt = select(ImportJobTable)
        
        if created_by:
            stmt = stmt.where(ImportJobTable.created_by == created_by)
        if import_type:
            stmt = stmt.where(ImportJobTable.import_type == import_type)
        
        stmt = stmt.limit(limit)
        
        result = await self.db.execute(stmt)
        jobs = result.fetchall()
        
        return [
            ImportJob(
                id=job.id,
                import_type=job.import_type,
                filename=job.filename,
                original_filename=job.original_filename,
                status=job.status,
                total_records=job.total_records,
                processed_records=job.processed_records,
                success_count=job.success_count,
                error_count=job.error_count,
                created_at=job.created_at,
                updated_at=job.updated_at,
                completed_at=job.completed_at,
                errors=job.errors or [],
                metadata=job.job_metadata or {},  # Use job_metadata column
                created_by=job.created_by
            )
            for job in jobs
        ]
    
    async def update_import_job(self, job_id: str, update_data: Dict[str, Any]):
        """Update import job"""
        update_data["updated_at"] = datetime.utcnow()
        
        stmt = update(ImportJobTable).where(ImportJobTable.id == job_id).values(**update_data)
        await self.db.execute(stmt)
        await self.db.commit()

class FileProcessor:
    """Service for processing uploaded files"""
    
    def detect_file_format(self, filename: str, content_type: str) -> str:
        """Detect file format based on filename and content type"""
        if filename.endswith('.csv'):
            return 'csv'
        elif filename.endswith(('.xlsx', '.xls')):
            return 'excel'
        elif filename.endswith('.json'):
            return 'json'
        else:
            return 'unknown'
    
    def parse_csv_file(self, content: bytes) -> List[Dict[str, Any]]:
        """Parse CSV file content"""
        try:
            # Convert bytes to string
            content_str = content.decode('utf-8')
            
            # Parse CSV
            reader = csv.DictReader(io.StringIO(content_str))
            return list(reader)
        except Exception as e:
            logger.error(f"Error parsing CSV file: {e}")
            return []
    
    def parse_excel_file(self, content: bytes) -> List[Dict[str, Any]]:
        """Parse Excel file content"""
        try:
            # Use pandas to read Excel file
            df = pd.read_excel(io.BytesIO(content))
            return df.to_dict('records')
        except Exception as e:
            logger.error(f"Error parsing Excel file: {e}")
            return []
    
    def parse_json_file(self, content: bytes) -> List[Dict[str, Any]]:
        """Parse JSON file content"""
        try:
            # Convert bytes to string and parse JSON
            content_str = content.decode('utf-8')
            data = json.loads(content_str)
            
            # Ensure data is a list
            if isinstance(data, dict):
                return [data]
            elif isinstance(data, list):
                return data
            else:
                return []
        except Exception as e:
            logger.error(f"Error parsing JSON file: {e}")
            return []

class DataValidator:
    """Service for validating import data"""
    
    def validate_links_data(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate links import data"""
        errors = []
        warnings = []
        valid_records = 0
        
        for i, record in enumerate(data):
            # Check required fields
            if not record.get('original_url'):
                errors.append({
                    "row": i + 1,
                    "field": "original_url",
                    "error": "Original URL is required"
                })
            else:
                valid_records += 1
            
            # Check URL format
            if record.get('original_url') and not record['original_url'].startswith(('http://', 'https://')):
                warnings.append({
                    "row": i + 1,
                    "field": "original_url",
                    "error": "URL should start with http:// or https://"
                })
        
        return {
            "is_valid": len(errors) == 0,
            "total_records": len(data),
            "valid_records": valid_records,
            "errors": errors,
            "warnings": warnings
        }
    
    def validate_users_data(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate users import data"""
        errors = []
        warnings = []
        valid_records = 0
        
        for i, record in enumerate(data):
            # Check required fields
            if not record.get('email'):
                errors.append({
                    "row": i + 1,
                    "field": "email",
                    "error": "Email is required"
                })
            elif '@' not in record['email']:
                errors.append({
                    "row": i + 1,
                    "field": "email",
                    "error": "Invalid email format"
                })
            else:
                valid_records += 1
            
            if not record.get('name'):
                errors.append({
                    "row": i + 1,
                    "field": "name",
                    "error": "Name is required"
                })
        
        return {
            "is_valid": len(errors) == 0,
            "total_records": len(data),
            "valid_records": valid_records,
            "errors": errors,
            "warnings": warnings
        }
    
    def validate_analytics_data(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate analytics import data"""
        errors = []
        warnings = []
        valid_records = 0
        
        for i, record in enumerate(data):
            # Check required fields
            if not record.get('click_date'):
                errors.append({
                    "row": i + 1,
                    "field": "click_date",
                    "error": "Click date is required"
                })
            else:
                valid_records += 1
        
        return {
            "is_valid": len(errors) == 0,
            "total_records": len(data),
            "valid_records": valid_records,
            "errors": errors,
            "warnings": warnings
        }

class DataProcessor:
    """Service for processing import data"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def process_links_import(
        self,
        data: List[Dict[str, Any]],
        job_id: str,
        skip_duplicates: bool = True
    ) -> Dict[str, Any]:
        """Process links import data"""
        success_count = 0
        error_count = 0
        
        for record in data:
            try:
                # Create link record
                link_data = {
                    "id": str(uuid.uuid4()),
                    "original_url": record.get('original_url'),
                    "short_url": record.get('short_url'),
                    "title": record.get('title'),
                    "description": record.get('description'),
                    "category": record.get('category', 'General'),
                    "tags": record.get('tags', []),
                    "is_active": record.get('is_active', True),
                    "clicks": record.get('clicks', 0),
                    "user_id": record.get('user_id'),
                    "user_email": record.get('user_email'),
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                
                # Insert link
                stmt = insert(LinkTable).values(**link_data)
                await self.db.execute(stmt)
                success_count += 1
                
            except Exception as e:
                logger.error(f"Error processing link record: {e}")
                error_count += 1
        
        await self.db.commit()
        
        return {
            "processed_count": len(data),
            "success_count": success_count,
            "error_count": error_count
        }
    
    async def process_users_import(
        self,
        data: List[Dict[str, Any]],
        job_id: str,
        auto_generate_passwords: bool = True
    ) -> Dict[str, Any]:
        """Process users import data"""
        success_count = 0
        error_count = 0
        
        for record in data:
            try:
                # Create user record
                user_data = {
                    "id": str(uuid.uuid4()),
                    "email": record.get('email'),
                    "name": record.get('name'),
                    "user_type": record.get('user_type', 'customer'),
                    "plan_type": record.get('plan', 'basic').lower(),
                    "is_active": record.get('status', 'active') == 'active',
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                
                # Insert user
                stmt = insert(UserTable).values(**user_data)
                await self.db.execute(stmt)
                success_count += 1
                
            except Exception as e:
                logger.error(f"Error processing user record: {e}")
                error_count += 1
        
        await self.db.commit()
        
        return {
            "processed_count": len(data),
            "success_count": success_count,
            "error_count": error_count
        }
    
    async def process_analytics_import(
        self,
        data: List[Dict[str, Any]],
        job_id: str
    ) -> Dict[str, Any]:
        """Process analytics import data"""
        success_count = 0
        error_count = 0
        
        for record in data:
            try:
                # Create analytics record
                analytics_data = {
                    "id": str(uuid.uuid4()),
                    "link_id": record.get('link_id'),
                    "short_url": record.get('short_url'),
                    "original_url": record.get('original_url'),
                    "clicks": record.get('clicks', 0),
                    "unique_clicks": record.get('unique_clicks', 0),
                    "click_date": record.get('click_date'),
                    "country": record.get('country'),
                    "city": record.get('city'),
                    "device_type": record.get('device_type'),
                    "browser": record.get('browser'),
                    "os": record.get('os'),
                    "referrer": record.get('referrer'),
                    "user_agent": record.get('user_agent'),
                    "ip_address": record.get('ip_address'),
                    "created_at": datetime.utcnow()
                }
                
                # Insert analytics
                stmt = insert(AnalyticsTable).values(**analytics_data)
                await self.db.execute(stmt)
                success_count += 1
                
            except Exception as e:
                logger.error(f"Error processing analytics record: {e}")
                error_count += 1
        
        await self.db.commit()
        
        return {
            "processed_count": len(data),
            "success_count": success_count,
            "error_count": error_count
        }

class PlatformMigrationService:
    """Service for migrating data from other platforms"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def migrate_from_bitly(self, migration_data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate data from Bitly"""
        # Placeholder for Bitly migration
        return {
            "success": False,
            "error": "Bitly migration not yet implemented"
        }
    
    async def migrate_from_rebrandly(self, migration_data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate data from Rebrandly"""
        # Placeholder for Rebrandly migration
        return {
            "success": False,
            "error": "Rebrandly migration not yet implemented"
        }