import pandas as pd
import json
import csv
import io
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import uuid
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import logging
from models import (
    ImportJob, ImportType, ImportStatus, LinkImportData, UserImportData,
    AnalyticsImportData, DomainImportData, ContactImportData,
    ImportError, ImportValidationResult, PlatformMigrationData
)
import requests
from passlib.context import CryptContext
import re

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class ImportService:
    def __init__(self, db):
        self.db = db
        self.collection_mappings = {
            ImportType.LINKS: "links",
            ImportType.USERS: "users", 
            ImportType.ANALYTICS: "analytics",
            ImportType.DOMAINS: "domains",
            ImportType.CONTACTS: "contacts"
        }
    
    async def create_import_job(self, import_type: ImportType, filename: str, 
                              original_filename: str, created_by: str) -> ImportJob:
        """Create a new import job"""
        job = ImportJob(
            import_type=import_type,
            filename=filename,
            original_filename=original_filename,
            created_by=created_by
        )
        
        await self.db.import_jobs.insert_one(job.dict())
        return job
    
    async def update_import_job(self, job_id: str, updates: Dict[str, Any]):
        """Update import job status and metadata"""
        updates["updated_at"] = datetime.utcnow()
        await self.db.import_jobs.update_one(
            {"id": job_id},
            {"$set": updates}
        )
    
    async def get_import_job(self, job_id: str) -> Optional[ImportJob]:
        """Get import job by ID"""
        job_data = await self.db.import_jobs.find_one({"id": job_id})
        if job_data:
            return ImportJob(**job_data)
        return None
    
    async def get_import_jobs(self, created_by: str = None, 
                            import_type: ImportType = None,
                            limit: int = 100) -> List[ImportJob]:
        """Get import jobs with optional filters"""
        filter_query = {}
        if created_by:
            filter_query["created_by"] = created_by
        if import_type:
            filter_query["import_type"] = import_type
        
        jobs = await self.db.import_jobs.find(filter_query).sort("created_at", -1).limit(limit).to_list(length=limit)
        return [ImportJob(**job) for job in jobs]

class FileProcessor:
    """Handles file processing and validation"""
    
    @staticmethod
    def parse_csv_file(file_content: bytes) -> List[Dict[str, Any]]:
        """Parse CSV file content"""
        try:
            content = file_content.decode('utf-8')
            csv_reader = csv.DictReader(io.StringIO(content))
            return list(csv_reader)
        except Exception as e:
            logger.error(f"Error parsing CSV file: {e}")
            raise ValueError(f"Invalid CSV format: {e}")
    
    @staticmethod
    def parse_excel_file(file_content: bytes) -> List[Dict[str, Any]]:
        """Parse Excel file content"""
        try:
            df = pd.read_excel(io.BytesIO(file_content))
            return df.to_dict('records')
        except Exception as e:
            logger.error(f"Error parsing Excel file: {e}")
            raise ValueError(f"Invalid Excel format: {e}")
    
    @staticmethod
    def parse_json_file(file_content: bytes) -> List[Dict[str, Any]]:
        """Parse JSON file content"""
        try:
            content = file_content.decode('utf-8')
            data = json.loads(content)
            if isinstance(data, dict):
                # If it's a single object, wrap in list
                return [data]
            return data
        except Exception as e:
            logger.error(f"Error parsing JSON file: {e}")
            raise ValueError(f"Invalid JSON format: {e}")
    
    @staticmethod
    def detect_file_format(filename: str, content_type: str) -> str:
        """Detect file format from filename and content type"""
        filename_lower = filename.lower()
        if filename_lower.endswith('.csv') or 'csv' in content_type:
            return 'csv'
        elif filename_lower.endswith(('.xlsx', '.xls')) or 'excel' in content_type:
            return 'excel'
        elif filename_lower.endswith('.json') or 'json' in content_type:
            return 'json'
        else:
            raise ValueError(f"Unsupported file format: {filename}")

class DataValidator:
    """Validates import data based on type"""
    
    @staticmethod
    def validate_links_data(data: List[Dict[str, Any]]) -> ImportValidationResult:
        """Validate links import data"""
        errors = []
        warnings = []
        valid_records = 0
        
        for i, row in enumerate(data):
            row_errors = []
            
            # Required fields
            if not row.get('original_url'):
                row_errors.append(ImportError(
                    row_number=i+1,
                    field='original_url',
                    error='Original URL is required',
                    data=row
                ))
            elif not DataValidator._is_valid_url(row['original_url']):
                row_errors.append(ImportError(
                    row_number=i+1,
                    field='original_url',
                    error='Invalid URL format',
                    data=row
                ))
            
            # Optional validations
            if row.get('short_url') and not DataValidator._is_valid_short_url(row['short_url']):
                warnings.append(ImportError(
                    row_number=i+1,
                    field='short_url',
                    error='Invalid short URL format',
                    data=row,
                    severity='warning'
                ))
            
            if not row_errors:
                valid_records += 1
            else:
                errors.extend(row_errors)
        
        return ImportValidationResult(
            is_valid=len(errors) == 0,
            total_records=len(data),
            valid_records=valid_records,
            errors=errors,
            warnings=warnings
        )
    
    @staticmethod
    def validate_users_data(data: List[Dict[str, Any]]) -> ImportValidationResult:
        """Validate users import data"""
        errors = []
        warnings = []
        valid_records = 0
        
        for i, row in enumerate(data):
            row_errors = []
            
            # Required fields
            if not row.get('name'):
                row_errors.append(ImportError(
                    row_number=i+1,
                    field='name',
                    error='Name is required',
                    data=row
                ))
            
            if not row.get('email'):
                row_errors.append(ImportError(
                    row_number=i+1,
                    field='email',
                    error='Email is required',
                    data=row
                ))
            elif not DataValidator._is_valid_email(row['email']):
                row_errors.append(ImportError(
                    row_number=i+1,
                    field='email',
                    error='Invalid email format',
                    data=row
                ))
            
            if not row_errors:
                valid_records += 1
            else:
                errors.extend(row_errors)
        
        return ImportValidationResult(
            is_valid=len(errors) == 0,
            total_records=len(data),
            valid_records=valid_records,
            errors=errors,
            warnings=warnings
        )
    
    @staticmethod
    def validate_analytics_data(data: List[Dict[str, Any]]) -> ImportValidationResult:
        """Validate analytics import data"""
        errors = []
        warnings = []
        valid_records = 0
        
        for i, row in enumerate(data):
            row_errors = []
            
            # At least one identifier required
            if not any([row.get('link_id'), row.get('short_url'), row.get('original_url')]):
                row_errors.append(ImportError(
                    row_number=i+1,
                    field='link_identifier',
                    error='At least one of link_id, short_url, or original_url is required',
                    data=row
                ))
            
            # Date validation
            if not row.get('click_date'):
                row_errors.append(ImportError(
                    row_number=i+1,
                    field='click_date',
                    error='Click date is required',
                    data=row
                ))
            
            if not row_errors:
                valid_records += 1
            else:
                errors.extend(row_errors)
        
        return ImportValidationResult(
            is_valid=len(errors) == 0,
            total_records=len(data),
            valid_records=valid_records,
            errors=errors,
            warnings=warnings
        )
    
    @staticmethod
    def _is_valid_url(url: str) -> bool:
        """Check if URL is valid"""
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return url_pattern.match(url) is not None
    
    @staticmethod
    def _is_valid_short_url(short_url: str) -> bool:
        """Check if short URL is valid"""
        # Basic validation for short URL format
        return len(short_url) > 0 and '.' in short_url
    
    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """Check if email is valid"""
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        return email_pattern.match(email) is not None

class DataProcessor:
    """Processes and imports validated data"""
    
    def __init__(self, db):
        self.db = db
    
    async def process_links_import(self, data: List[Dict[str, Any]], 
                                 job_id: str, skip_duplicates: bool = True) -> Dict[str, int]:
        """Process links import"""
        success_count = 0
        error_count = 0
        processed_count = 0
        
        for row in data:
            try:
                # Transform data
                link_data = {
                    "id": str(uuid.uuid4()),
                    "original_url": row["original_url"],
                    "short_url": row.get("short_url", f"lab.et/{str(uuid.uuid4())[:8]}"),
                    "title": row.get("title", "Imported Link"),
                    "description": row.get("description", ""),
                    "category": row.get("category", "General"),
                    "tags": row.get("tags", []) if isinstance(row.get("tags"), list) else [],
                    "custom_domain": row.get("custom_domain", ""),
                    "is_active": row.get("is_active", True),
                    "created_at": row.get("created_at", datetime.utcnow()),
                    "clicks": int(row.get("clicks", 0)),
                    "user_id": row.get("user_id", "1"),  # Default user
                    "metadata": {"imported": True, "import_job_id": job_id}
                }
                
                # Check for duplicates
                if skip_duplicates:
                    existing = await self.db.links.find_one({"original_url": link_data["original_url"]})
                    if existing:
                        processed_count += 1
                        continue
                
                # Insert link
                await self.db.links.insert_one(link_data)
                success_count += 1
                processed_count += 1
                
            except Exception as e:
                logger.error(f"Error processing link row: {e}")
                error_count += 1
                processed_count += 1
        
        return {
            "success_count": success_count,
            "error_count": error_count,
            "processed_count": processed_count
        }
    
    async def process_users_import(self, data: List[Dict[str, Any]], 
                                 job_id: str, auto_generate_passwords: bool = True) -> Dict[str, int]:
        """Process users import"""
        success_count = 0
        error_count = 0
        processed_count = 0
        
        for row in data:
            try:
                # Generate password if needed
                password = row.get("password")
                if not password and auto_generate_passwords:
                    password = str(uuid.uuid4())[:12]
                
                # Hash password
                hashed_password = pwd_context.hash(password) if password else None
                
                # Transform data
                user_data = {
                    "id": str(uuid.uuid4()),
                    "name": row["name"],
                    "email": row["email"],
                    "password": hashed_password,
                    "user_type": row.get("user_type", "customer"),
                    "plan": row.get("plan", "Basic"),
                    "status": row.get("status", "active"),
                    "phone": row.get("phone", ""),
                    "company": row.get("company", ""),
                    "created_at": row.get("created_at", datetime.utcnow()),
                    "custom_domains": row.get("custom_domains", []),
                    "metadata": {"imported": True, "import_job_id": job_id}
                }
                
                # Check for duplicates
                existing = await self.db.users.find_one({"email": user_data["email"]})
                if existing:
                    processed_count += 1
                    continue
                
                # Insert user
                await self.db.users.insert_one(user_data)
                success_count += 1
                processed_count += 1
                
            except Exception as e:
                logger.error(f"Error processing user row: {e}")
                error_count += 1
                processed_count += 1
        
        return {
            "success_count": success_count,
            "error_count": error_count,
            "processed_count": processed_count
        }
    
    async def process_analytics_import(self, data: List[Dict[str, Any]], 
                                     job_id: str) -> Dict[str, int]:
        """Process analytics import"""
        success_count = 0
        error_count = 0
        processed_count = 0
        
        for row in data:
            try:
                # Transform data
                analytics_data = {
                    "id": str(uuid.uuid4()),
                    "link_id": row.get("link_id"),
                    "short_url": row.get("short_url"),
                    "original_url": row.get("original_url"),
                    "clicks": int(row.get("clicks", 0)),
                    "unique_clicks": int(row.get("unique_clicks", 0)),
                    "click_date": row["click_date"],
                    "country": row.get("country", ""),
                    "city": row.get("city", ""),
                    "device_type": row.get("device_type", ""),
                    "browser": row.get("browser", ""),
                    "os": row.get("os", ""),
                    "referrer": row.get("referrer", ""),
                    "user_agent": row.get("user_agent", ""),
                    "ip_address": row.get("ip_address", ""),
                    "metadata": {"imported": True, "import_job_id": job_id}
                }
                
                # Insert analytics data
                await self.db.analytics.insert_one(analytics_data)
                success_count += 1
                processed_count += 1
                
            except Exception as e:
                logger.error(f"Error processing analytics row: {e}")
                error_count += 1
                processed_count += 1
        
        return {
            "success_count": success_count,
            "error_count": error_count,
            "processed_count": processed_count
        }

class PlatformMigrationService:
    """Handles migration from other platforms"""
    
    def __init__(self, db):
        self.db = db
    
    async def migrate_from_bitly(self, migration_data: PlatformMigrationData) -> Dict[str, Any]:
        """Migrate links from Bit.ly"""
        try:
            headers = {
                'Authorization': f'Bearer {migration_data.access_token}',
                'Content-Type': 'application/json'
            }
            
            # Get links from Bit.ly API
            response = requests.get(
                'https://api-ssl.bitly.com/v4/links',
                headers=headers,
                params={'size': 50}
            )
            
            if response.status_code == 200:
                bitly_links = response.json().get('links', [])
                
                # Transform to our format
                transformed_links = []
                for link in bitly_links:
                    transformed_links.append({
                        'original_url': link.get('long_url', ''),
                        'short_url': link.get('link', ''),
                        'title': link.get('title', ''),
                        'created_at': link.get('created_at', ''),
                        'clicks': link.get('clicks', 0),
                        'tags': link.get('tags', [])
                    })
                
                return {
                    'success': True,
                    'links': transformed_links,
                    'total_count': len(transformed_links)
                }
            else:
                return {
                    'success': False,
                    'error': f'Bit.ly API error: {response.status_code}'
                }
                
        except Exception as e:
            logger.error(f"Error migrating from Bit.ly: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def migrate_from_tinyurl(self, migration_data: PlatformMigrationData) -> Dict[str, Any]:
        """Migrate links from TinyURL"""
        # TinyURL doesn't have a public API, so this would need to be implemented
        # based on export files or custom solutions
        return {
            'success': False,
            'error': 'TinyURL migration not implemented yet'
        }
    
    async def migrate_from_rebrandly(self, migration_data: PlatformMigrationData) -> Dict[str, Any]:
        """Migrate links from Rebrandly"""
        try:
            headers = {
                'apikey': migration_data.api_key,
                'Content-Type': 'application/json'
            }
            
            # Get links from Rebrandly API
            response = requests.get(
                'https://api.rebrandly.com/v1/links',
                headers=headers,
                params={'limit': 25}
            )
            
            if response.status_code == 200:
                rebrandly_links = response.json()
                
                # Transform to our format
                transformed_links = []
                for link in rebrandly_links:
                    transformed_links.append({
                        'original_url': link.get('destination', ''),
                        'short_url': f"https://{link.get('domainName', '')}/{link.get('slashtag', '')}",
                        'title': link.get('title', ''),
                        'created_at': link.get('createdAt', ''),
                        'clicks': link.get('clicks', 0)
                    })
                
                return {
                    'success': True,
                    'links': transformed_links,
                    'total_count': len(transformed_links)
                }
            else:
                return {
                    'success': False,
                    'error': f'Rebrandly API error: {response.status_code}'
                }
                
        except Exception as e:
            logger.error(f"Error migrating from Rebrandly: {e}")
            return {
                'success': False,
                'error': str(e)
            }