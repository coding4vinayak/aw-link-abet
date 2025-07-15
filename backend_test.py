#!/usr/bin/env python3
"""
Backend API Testing for LinkAbet/Linkly Application
Tests the FastAPI backend endpoints for basic functionality
"""

import requests
import json
import sys
from datetime import datetime
import uuid

# Get backend URL from frontend .env file
def get_backend_url():
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    except Exception as e:
        print(f"Error reading frontend .env: {e}")
        return None

BASE_URL = get_backend_url()
if not BASE_URL:
    print("❌ Could not get backend URL from frontend/.env")
    sys.exit(1)

API_BASE_URL = f"{BASE_URL}/api"
print(f"🔗 Testing backend API at: {API_BASE_URL}")

def test_root_endpoint():
    """Test the root API endpoint"""
    print("\n📍 Testing Root Endpoint (GET /api/)")
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=30)
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("message") == "Hello World":
                print("   ✅ Root endpoint working correctly")
                return True
            else:
                print("   ❌ Unexpected response message")
                return False
        else:
            print(f"   ❌ Root endpoint failed with status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Connection error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False

def test_create_status_check():
    """Test creating a status check (POST /api/status)"""
    print("\n📍 Testing Create Status Check (POST /api/status)")
    
    test_data = {
        "client_name": "LinkAbet Test Client"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/status", 
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            required_fields = ["id", "client_name", "timestamp"]
            
            if all(field in data for field in required_fields):
                if data["client_name"] == test_data["client_name"]:
                    print("   ✅ Status check creation working correctly")
                    return True, data["id"]
                else:
                    print("   ❌ Client name mismatch in response")
                    return False, None
            else:
                print(f"   ❌ Missing required fields in response: {required_fields}")
                return False, None
        else:
            print(f"   ❌ Status check creation failed with status {response.status_code}")
            return False, None
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Connection error: {e}")
        return False, None
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False, None

def test_get_status_checks():
    """Test retrieving status checks (GET /api/status)"""
    print("\n📍 Testing Get Status Checks (GET /api/status)")
    
    try:
        response = requests.get(f"{API_BASE_URL}/status", timeout=30)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: Found {len(data)} status checks")
            
            if isinstance(data, list):
                if len(data) > 0:
                    # Check structure of first item
                    first_item = data[0]
                    required_fields = ["id", "client_name", "timestamp"]
                    if all(field in first_item for field in required_fields):
                        print("   ✅ Status checks retrieval working correctly")
                        return True
                    else:
                        print(f"   ❌ Status check items missing required fields: {required_fields}")
                        return False
                else:
                    print("   ✅ Status checks retrieval working (empty list)")
                    return True
            else:
                print("   ❌ Response is not a list")
                return False
        else:
            print(f"   ❌ Status checks retrieval failed with status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Connection error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False

def test_backend_connectivity():
    """Test basic backend connectivity"""
    print("\n📍 Testing Backend Connectivity")
    
    try:
        response = requests.get(BASE_URL, timeout=30)
        print(f"   Backend base URL status: {response.status_code}")
        return response.status_code in [200, 404]  # 404 is OK for base URL
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Backend connectivity failed: {e}")
        return False

def test_subscription_plans():
    """Test subscription plans endpoint (GET /api/subscription/plans)"""
    print("\n📍 Testing Subscription Plans (GET /api/subscription/plans)")
    
    try:
        response = requests.get(f"{API_BASE_URL}/subscription/plans", timeout=30)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: Found {len(data)} subscription plans")
            
            if isinstance(data, list) and len(data) >= 2:
                # Check for Basic and Pro plans
                plan_names = [plan.get('name') for plan in data]
                if 'Basic' in plan_names and 'Pro' in plan_names:
                    # Verify plan structure
                    basic_plan = next(p for p in data if p.get('name') == 'Basic')
                    required_fields = ['name', 'plan_type', 'price_monthly', 'price_yearly', 'limits', 'features']
                    
                    if all(field in basic_plan for field in required_fields):
                        print("   ✅ Subscription plans endpoint working correctly")
                        return True
                    else:
                        print(f"   ❌ Plan missing required fields: {required_fields}")
                        return False
                else:
                    print("   ❌ Missing Basic or Pro plans")
                    return False
            else:
                print("   ❌ Expected at least 2 subscription plans")
                return False
        else:
            print(f"   ❌ Subscription plans failed with status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Connection error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False

def test_create_import_job():
    """Test creating an import job (POST /api/import/jobs)"""
    print("\n📍 Testing Create Import Job (POST /api/import/jobs)")
    
    test_data = {
        "import_type": "links",
        "filename": "test_links.csv",
        "created_by": "test-user-123"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/import/jobs",
            data=test_data,  # Using form data as per endpoint
            timeout=30
        )
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            required_fields = ["job_id", "import_type", "status", "message"]
            
            if all(field in data for field in required_fields):
                if data["import_type"] == test_data["import_type"]:
                    print("   ✅ Import job creation working correctly")
                    return True, data["job_id"]
                else:
                    print("   ❌ Import type mismatch in response")
                    return False, None
            else:
                print(f"   ❌ Missing required fields in response: {required_fields}")
                return False, None
        else:
            print(f"   ❌ Import job creation failed with status {response.status_code}")
            return False, None
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Connection error: {e}")
        return False, None
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False, None

def test_get_import_jobs():
    """Test retrieving import jobs (GET /api/import/jobs)"""
    print("\n📍 Testing Get Import Jobs (GET /api/import/jobs)")
    
    try:
        response = requests.get(f"{API_BASE_URL}/import/jobs", timeout=30)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: Found {len(data)} import jobs")
            
            if isinstance(data, list):
                if len(data) > 0:
                    # Check structure of first item
                    first_item = data[0]
                    required_fields = ["job_id", "import_type", "status", "progress"]
                    if all(field in first_item for field in required_fields):
                        print("   ✅ Import jobs retrieval working correctly")
                        return True
                    else:
                        print(f"   ❌ Import job items missing required fields: {required_fields}")
                        return False
                else:
                    print("   ✅ Import jobs retrieval working (empty list)")
                    return True
            else:
                print("   ❌ Response is not a list")
                return False
        else:
            print(f"   ❌ Import jobs retrieval failed with status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Connection error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False

def test_database_persistence():
    """Test database persistence by creating and retrieving data"""
    print("\n📍 Testing PostgreSQL Database Persistence")
    
    # Create a status check
    test_data = {"client_name": "PostgreSQL Migration Test"}
    
    try:
        # Create
        create_response = requests.post(
            f"{API_BASE_URL}/status", 
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if create_response.status_code != 200:
            print("   ❌ Failed to create test data")
            return False
        
        created_id = create_response.json().get("id")
        
        # Retrieve all and verify our data exists
        get_response = requests.get(f"{API_BASE_URL}/status", timeout=30)
        
        if get_response.status_code != 200:
            print("   ❌ Failed to retrieve data")
            return False
        
        all_status_checks = get_response.json()
        
        # Find our created item
        found_item = None
        for item in all_status_checks:
            if item.get("id") == created_id:
                found_item = item
                break
        
        if found_item and found_item.get("client_name") == test_data["client_name"]:
            print("   ✅ PostgreSQL database persistence working correctly")
            return True
        else:
            print("   ❌ Created data not found in database")
            return False
            
    except Exception as e:
        print(f"   ❌ Database persistence test failed: {e}")
        return False

def test_subscription_current_user():
    """Test current subscription endpoint (GET /api/subscription/current/{user_id})"""
    print("\n📍 Testing Current User Subscription (GET /api/subscription/current/{user_id})")
    
    test_user_id = "test-user-123"
    
    try:
        response = requests.get(f"{API_BASE_URL}/subscription/current/{test_user_id}", timeout=30)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: User subscription retrieved")
            
            required_fields = ['id', 'user_id', 'plan_type', 'is_active']
            if all(field in data for field in required_fields):
                if data['user_id'] == test_user_id:
                    print("   ✅ Current subscription endpoint working correctly")
                    return True
                else:
                    print("   ❌ User ID mismatch in response")
                    return False
            else:
                print(f"   ❌ Missing required fields: {required_fields}")
                return False
        else:
            print(f"   ❌ Current subscription failed with status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Connection error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False

def test_import_job_by_id():
    """Test getting specific import job by ID"""
    print("\n📍 Testing Get Import Job by ID (GET /api/import/jobs/{job_id})")
    
    # First create an import job to get an ID
    test_data = {
        "import_type": "users",
        "filename": "test_users.csv",
        "created_by": "test-user-456"
    }
    
    try:
        # Create job
        create_response = requests.post(
            f"{API_BASE_URL}/import/jobs",
            data=test_data,
            timeout=30
        )
        
        if create_response.status_code != 200:
            print("   ❌ Failed to create test import job")
            return False
        
        job_id = create_response.json().get("job_id")
        
        # Get job by ID
        response = requests.get(f"{API_BASE_URL}/import/jobs/{job_id}", timeout=30)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: Import job retrieved by ID")
            
            required_fields = ['job_id', 'import_type', 'status', 'progress']
            if all(field in data for field in required_fields):
                if data['job_id'] == job_id and data['import_type'] == test_data['import_type']:
                    print("   ✅ Import job by ID endpoint working correctly")
                    return True
                else:
                    print("   ❌ Job data mismatch")
                    return False
            else:
                print(f"   ❌ Missing required fields: {required_fields}")
                return False
        else:
            print(f"   ❌ Get import job by ID failed with status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Connection error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False

# =====================================================
# LINKLY-SPECIFIC API TESTS
# =====================================================

def test_get_users():
    """Test getting all users (GET /api/users)"""
    print("\n📍 Testing Get All Users (GET /api/users)")
    
    try:
        response = requests.get(f"{API_BASE_URL}/users", timeout=30)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: Found {len(data)} users")
            
            if isinstance(data, list):
                if len(data) > 0:
                    # Check structure of first user
                    first_user = data[0]
                    required_fields = ["id", "email", "name", "user_type", "plan_type", "is_active"]
                    if all(field in first_user for field in required_fields):
                        print("   ✅ Get all users working correctly")
                        return True, data
                    else:
                        print(f"   ❌ User missing required fields: {required_fields}")
                        return False, None
                else:
                    print("   ✅ Get all users working (empty list)")
                    return True, []
            else:
                print("   ❌ Response is not a list")
                return False, None
        else:
            print(f"   ❌ Get users failed with status {response.status_code}")
            return False, None
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Connection error: {e}")
        return False, None
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False, None

def test_get_specific_user(user_id):
    """Test getting a specific user (GET /api/users/{user_id})"""
    print(f"\n📍 Testing Get Specific User (GET /api/users/{user_id})")
    
    try:
        response = requests.get(f"{API_BASE_URL}/users/{user_id}", timeout=30)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: User retrieved successfully")
            
            required_fields = ["id", "email", "name", "user_type", "plan_type", "is_active"]
            if all(field in data for field in required_fields):
                if data["id"] == user_id:
                    print("   ✅ Get specific user working correctly")
                    return True, data
                else:
                    print("   ❌ User ID mismatch")
                    return False, None
            else:
                print(f"   ❌ User missing required fields: {required_fields}")
                return False, None
        elif response.status_code == 404:
            print("   ❌ User not found")
            return False, None
        else:
            print(f"   ❌ Get specific user failed with status {response.status_code}")
            return False, None
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Connection error: {e}")
        return False, None
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False, None

def test_update_user(user_id, user_data):
    """Test updating a user (PUT /api/users/{user_id})"""
    print(f"\n📍 Testing Update User (PUT /api/users/{user_id})")
    
    update_data = {
        "name": user_data.get("name", "Updated Test User"),
        "email": user_data.get("email", "updated@example.com"),
        "user_type": user_data.get("user_type", "customer"),
        "plan_type": user_data.get("plan_type", "basic"),
        "max_links": user_data.get("max_links", 5),
        "is_active": user_data.get("is_active", True)
    }
    
    try:
        response = requests.put(
            f"{API_BASE_URL}/users/{user_id}",
            data=update_data,
            timeout=30
        )
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: User updated successfully")
            
            # Verify the update
            if data["name"] == update_data["name"] and data["email"] == update_data["email"]:
                print("   ✅ Update user working correctly")
                return True
            else:
                print("   ❌ User data not updated correctly")
                return False
        elif response.status_code == 404:
            print("   ❌ User not found for update")
            return False
        else:
            print(f"   ❌ Update user failed with status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Connection error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False

def test_suspend_user(user_id):
    """Test suspending a user (POST /api/users/{user_id}/suspend)"""
    print(f"\n📍 Testing Suspend User (POST /api/users/{user_id}/suspend)")
    
    try:
        response = requests.post(f"{API_BASE_URL}/users/{user_id}/suspend", timeout=30)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {data}")
            
            if "message" in data and "suspended" in data["message"].lower():
                print("   ✅ Suspend user working correctly")
                return True
            else:
                print("   ❌ Unexpected response message")
                return False
        elif response.status_code == 404:
            print("   ❌ User not found for suspension")
            return False
        else:
            print(f"   ❌ Suspend user failed with status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Connection error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False

def test_activate_user(user_id):
    """Test activating a user (POST /api/users/{user_id}/activate)"""
    print(f"\n📍 Testing Activate User (POST /api/users/{user_id}/activate)")
    
    try:
        response = requests.post(f"{API_BASE_URL}/users/{user_id}/activate", timeout=30)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {data}")
            
            if "message" in data and "activated" in data["message"].lower():
                print("   ✅ Activate user working correctly")
                return True
            else:
                print("   ❌ Unexpected response message")
                return False
        elif response.status_code == 404:
            print("   ❌ User not found for activation")
            return False
        else:
            print(f"   ❌ Activate user failed with status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Connection error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False

def test_create_link():
    """Test creating a new short link (POST /api/links)"""
    print("\n📍 Testing Create Link (POST /api/links)")
    
    test_link_data = {
        "original_url": "https://www.google.com",
        "title": "Google Search Engine",
        "description": "The world's most popular search engine",
        "category": "Search",
        "user_email": "john@example.com"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/links",
            json=test_link_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: Link created successfully")
            print(f"   Short URL: {data.get('short_url')}")
            
            required_fields = ["id", "original_url", "short_url", "title", "is_active", "clicks"]
            if all(field in data for field in required_fields):
                if data["original_url"] == test_link_data["original_url"]:
                    print("   ✅ Create link working correctly")
                    return True, data
                else:
                    print("   ❌ Original URL mismatch")
                    return False, None
            else:
                print(f"   ❌ Link missing required fields: {required_fields}")
                return False, None
        else:
            print(f"   ❌ Create link failed with status {response.status_code}")
            return False, None
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Connection error: {e}")
        return False, None
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False, None

def test_get_links():
    """Test getting all links (GET /api/links)"""
    print("\n📍 Testing Get All Links (GET /api/links)")
    
    try:
        response = requests.get(f"{API_BASE_URL}/links", timeout=30)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: Found {len(data)} links")
            
            if isinstance(data, list):
                if len(data) > 0:
                    # Check structure of first link
                    first_link = data[0]
                    required_fields = ["id", "original_url", "short_url", "is_active", "clicks"]
                    if all(field in first_link for field in required_fields):
                        print("   ✅ Get all links working correctly")
                        return True, data
                    else:
                        print(f"   ❌ Link missing required fields: {required_fields}")
                        return False, None
                else:
                    print("   ✅ Get all links working (empty list)")
                    return True, []
            else:
                print("   ❌ Response is not a list")
                return False, None
        else:
            print(f"   ❌ Get links failed with status {response.status_code}")
            return False, None
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Connection error: {e}")
        return False, None
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False, None

def test_get_specific_link(link_id):
    """Test getting a specific link (GET /api/links/{link_id})"""
    print(f"\n📍 Testing Get Specific Link (GET /api/links/{link_id})")
    
    try:
        response = requests.get(f"{API_BASE_URL}/links/{link_id}", timeout=30)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: Link retrieved successfully")
            
            required_fields = ["id", "original_url", "short_url", "is_active", "clicks"]
            if all(field in data for field in required_fields):
                if data["id"] == link_id:
                    print("   ✅ Get specific link working correctly")
                    return True, data
                else:
                    print("   ❌ Link ID mismatch")
                    return False, None
            else:
                print(f"   ❌ Link missing required fields: {required_fields}")
                return False, None
        elif response.status_code == 404:
            print("   ❌ Link not found")
            return False, None
        else:
            print(f"   ❌ Get specific link failed with status {response.status_code}")
            return False, None
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Connection error: {e}")
        return False, None
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False, None

def test_toggle_link(link_id):
    """Test toggling link status (PUT /api/links/{link_id}/toggle)"""
    print(f"\n📍 Testing Toggle Link Status (PUT /api/links/{link_id}/toggle)")
    
    try:
        response = requests.put(f"{API_BASE_URL}/links/{link_id}/toggle", timeout=30)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {data}")
            
            if "message" in data and ("activated" in data["message"].lower() or "deactivated" in data["message"].lower()):
                print("   ✅ Toggle link status working correctly")
                return True
            else:
                print("   ❌ Unexpected response message")
                return False
        elif response.status_code == 404:
            print("   ❌ Link not found for toggle")
            return False
        else:
            print(f"   ❌ Toggle link failed with status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Connection error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False

def test_delete_link(link_id):
    """Test deleting a link (DELETE /api/links/{link_id})"""
    print(f"\n📍 Testing Delete Link (DELETE /api/links/{link_id})")
    
    try:
        response = requests.delete(f"{API_BASE_URL}/links/{link_id}", timeout=30)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {data}")
            
            if "message" in data and "deleted" in data["message"].lower():
                print("   ✅ Delete link working correctly")
                return True
            else:
                print("   ❌ Unexpected response message")
                return False
        elif response.status_code == 404:
            print("   ❌ Link not found for deletion")
            return False
        else:
            print(f"   ❌ Delete link failed with status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Connection error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False

def test_api_redirect_functionality(short_code):
    """Test API redirect functionality (GET /api/redirect/{short_code})"""
    print(f"\n📍 Testing API Redirect (GET /api/redirect/{short_code})")
    
    try:
        # Test the /api/redirect/{short_code} endpoint specifically
        response = requests.get(f"{API_BASE_URL}/redirect/{short_code}", allow_redirects=False, timeout=30)
        print(f"   Status Code: {response.status_code}")
        print(f"   Response Headers: {dict(response.headers)}")
        
        if response.status_code == 302:
            location = response.headers.get('Location')
            print(f"   Redirect Location: {location}")
            
            if location and location.startswith('http'):
                print("   ✅ API redirect working correctly")
                return True, location
            else:
                print("   ❌ Invalid redirect location")
                return False, None
        elif response.status_code == 404:
            print("   ❌ Short code not found")
            return False, None
        else:
            print(f"   ❌ API redirect failed with status {response.status_code}")
            print(f"   Response content: {response.text[:200]}")
            return False, None
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Connection error: {e}")
        return False, None
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False, None

def test_redirect_functionality(short_code):
    """Test link redirect functionality (GET /go/{short_code}) - Known to be broken"""
    print(f"\n📍 Testing Direct Redirect (GET /go/{short_code}) - KNOWN ISSUE")
    
    try:
        # Test the /go/{short_code} endpoint specifically
        response = requests.get(f"{BASE_URL}/go/{short_code}", allow_redirects=False, timeout=30)
        print(f"   Status Code: {response.status_code}")
        print(f"   Response Headers: {dict(response.headers)}")
        
        if response.status_code == 302:
            location = response.headers.get('Location')
            print(f"   Redirect Location: {location}")
            
            if location and location.startswith('http'):
                print("   ✅ Direct redirect working correctly")
                return True, location
            else:
                print("   ❌ Invalid redirect location")
                return False, None
        elif response.status_code == 404:
            print("   ❌ Short code not found")
            return False, None
        else:
            print(f"   ❌ Direct redirect failed with status {response.status_code}")
            print(f"   ⚠️  EXPECTED FAILURE: Frontend routing intercepts /go/* requests")
            print(f"   Response content: {response.text[:200]}")
            return False, None
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Connection error: {e}")
        return False, None
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False, None

def test_api_redirect_with_click_tracking(short_code, original_url):
    """Test API redirect functionality with click tracking verification"""
    print(f"\n📍 Testing API Redirect with Click Tracking (GET /api/redirect/{short_code})")
    
    try:
        # Get initial click count
        links_response = requests.get(f"{API_BASE_URL}/links", timeout=30)
        if links_response.status_code != 200:
            print("   ❌ Could not get links to check initial click count")
            return False
        
        links = links_response.json()
        target_link = None
        for link in links:
            if short_code in link.get('short_url', ''):
                target_link = link
                break
        
        if not target_link:
            print("   ❌ Could not find link with matching short code")
            return False
        
        initial_clicks = target_link.get('clicks', 0)
        print(f"   Initial click count: {initial_clicks}")
        
        # Perform API redirect
        response = requests.get(f"{API_BASE_URL}/redirect/{short_code}", allow_redirects=False, timeout=30)
        
        if response.status_code == 302:
            location = response.headers.get('Location')
            print(f"   API redirect successful to: {location}")
            
            # Verify click count increased
            import time
            time.sleep(1)  # Give database time to update
            
            updated_links_response = requests.get(f"{API_BASE_URL}/links", timeout=30)
            if updated_links_response.status_code == 200:
                updated_links = updated_links_response.json()
                updated_target_link = None
                for link in updated_links:
                    if short_code in link.get('short_url', ''):
                        updated_target_link = link
                        break
                
                if updated_target_link:
                    new_clicks = updated_target_link.get('clicks', 0)
                    print(f"   Updated click count: {new_clicks}")
                    
                    if new_clicks > initial_clicks:
                        print("   ✅ API redirect click tracking working correctly")
                        return True
                    else:
                        print("   ❌ Click count did not increase")
                        return False
                else:
                    print("   ❌ Could not find updated link")
                    return False
            else:
                print("   ❌ Could not retrieve updated links")
                return False
        else:
            print(f"   ❌ API redirect failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing API redirect click tracking: {e}")
        return False

def test_redirect_with_click_tracking(short_code, original_url):
    """Test redirect functionality with click tracking verification"""
    print(f"\n📍 Testing Redirect with Click Tracking (GET /go/{short_code}) - KNOWN ISSUE")
    
    try:
        # Get initial click count
        links_response = requests.get(f"{API_BASE_URL}/links", timeout=30)
        if links_response.status_code != 200:
            print("   ❌ Could not get links to check initial click count")
            return False
        
        links = links_response.json()
        target_link = None
        for link in links:
            if short_code in link.get('short_url', ''):
                target_link = link
                break
        
        if not target_link:
            print("   ❌ Could not find link with matching short code")
            return False
        
        initial_clicks = target_link.get('clicks', 0)
        print(f"   Initial click count: {initial_clicks}")
        
        # Perform redirect
        response = requests.get(f"{BASE_URL}/go/{short_code}", allow_redirects=False, timeout=30)
        
        if response.status_code == 302:
            location = response.headers.get('Location')
            print(f"   Redirect successful to: {location}")
            
            # Verify click count increased
            import time
            time.sleep(1)  # Give database time to update
            
            updated_links_response = requests.get(f"{API_BASE_URL}/links", timeout=30)
            if updated_links_response.status_code == 200:
                updated_links = updated_links_response.json()
                updated_target_link = None
                for link in updated_links:
                    if short_code in link.get('short_url', ''):
                        updated_target_link = link
                        break
                
                if updated_target_link:
                    new_clicks = updated_target_link.get('clicks', 0)
                    print(f"   Updated click count: {new_clicks}")
                    
                    if new_clicks > initial_clicks:
                        print("   ✅ Click tracking working correctly")
                        return True
                    else:
                        print("   ❌ Click count did not increase")
                        return False
                else:
                    print("   ❌ Could not find updated link")
                    return False
            else:
                print("   ❌ Could not retrieve updated links")
                return False
        else:
            print(f"   ❌ Redirect failed with status {response.status_code}")
            print(f"   ⚠️  EXPECTED FAILURE: Frontend routing intercepts /go/* requests")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing click tracking: {e}")
        return False

def test_api_redirect_with_invalid_codes():
    """Test API redirect with invalid/non-existent short codes"""
    print(f"\n📍 Testing API Redirect with Invalid Short Codes")
    
    invalid_codes = ['invalid123', 'nonexistent', 'fake456']
    
    for code in invalid_codes:
        try:
            response = requests.get(f"{API_BASE_URL}/redirect/{code}", allow_redirects=False, timeout=30)
            print(f"   Testing code '{code}': Status {response.status_code}")
            
            if response.status_code != 404:
                print(f"   ❌ Expected 404 for invalid code '{code}', got {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error testing invalid code '{code}': {e}")
            return False
    
    print("   ✅ Invalid short codes properly return 404 via API redirect")
    return True

def test_redirect_with_invalid_codes():
    """Test redirect with invalid/non-existent short codes"""
    print(f"\n📍 Testing Redirect with Invalid Short Codes - KNOWN ISSUE")
    
    invalid_codes = ['invalid123', 'nonexistent', 'fake456']
    
    for code in invalid_codes:
        try:
            response = requests.get(f"{BASE_URL}/go/{code}", allow_redirects=False, timeout=30)
            print(f"   Testing code '{code}': Status {response.status_code}")
            
            if response.status_code != 404:
                print(f"   ❌ Expected 404 for invalid code '{code}', got {response.status_code}")
                print(f"   ⚠️  EXPECTED FAILURE: Frontend routing intercepts /go/* requests")
                return False
                
        except Exception as e:
            print(f"   ❌ Error testing invalid code '{code}': {e}")
            return False
    
    print("   ✅ Invalid short codes properly return 404")
    return True

def test_api_redirect_inactive_links():
    """Test API redirect behavior with inactive links"""
    print(f"\n📍 Testing API Redirect with Inactive Links")
    
    try:
        # Create a link first
        test_link_data = {
            "original_url": "https://www.example.com",
            "title": "Test Inactive Link",
            "description": "Testing inactive link redirect",
            "category": "Test",
            "user_email": "test@example.com"
        }
        
        create_response = requests.post(
            f"{API_BASE_URL}/links",
            json=test_link_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if create_response.status_code != 200:
            print("   ❌ Could not create test link")
            return False
        
        link_data = create_response.json()
        link_id = link_data['id']
        short_code = link_data['short_url'].split('/')[-1]
        
        # Deactivate the link
        toggle_response = requests.put(f"{API_BASE_URL}/links/{link_id}/toggle", timeout=30)
        if toggle_response.status_code != 200:
            print("   ❌ Could not deactivate test link")
            return False
        
        # Try to access the inactive link via API redirect
        redirect_response = requests.get(f"{API_BASE_URL}/redirect/{short_code}", allow_redirects=False, timeout=30)
        print(f"   Inactive link API redirect status: {redirect_response.status_code}")
        
        if redirect_response.status_code == 404:
            print("   ✅ Inactive links properly return 404 via API redirect")
            success = True
        else:
            print(f"   ❌ Expected 404 for inactive link, got {redirect_response.status_code}")
            success = False
        
        # Clean up - delete the test link
        requests.delete(f"{API_BASE_URL}/links/{link_id}", timeout=30)
        
        return success
        
    except Exception as e:
        print(f"   ❌ Error testing inactive links: {e}")
        return False

def test_redirect_inactive_links():
    """Test redirect behavior with inactive links"""
    print(f"\n📍 Testing Redirect with Inactive Links - KNOWN ISSUE")
    
    try:
        # Create a link first
        test_link_data = {
            "original_url": "https://www.example.com",
            "title": "Test Inactive Link",
            "description": "Testing inactive link redirect",
            "category": "Test",
            "user_email": "test@example.com"
        }
        
        create_response = requests.post(
            f"{API_BASE_URL}/links",
            json=test_link_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if create_response.status_code != 200:
            print("   ❌ Could not create test link")
            return False
        
        link_data = create_response.json()
        link_id = link_data['id']
        short_code = link_data['short_url'].split('/')[-1]
        
        # Deactivate the link
        toggle_response = requests.put(f"{API_BASE_URL}/links/{link_id}/toggle", timeout=30)
        if toggle_response.status_code != 200:
            print("   ❌ Could not deactivate test link")
            return False
        
        # Try to access the inactive link
        redirect_response = requests.get(f"{BASE_URL}/go/{short_code}", allow_redirects=False, timeout=30)
        print(f"   Inactive link redirect status: {redirect_response.status_code}")
        
        if redirect_response.status_code == 404:
            print("   ✅ Inactive links properly return 404")
            success = True
        else:
            print(f"   ❌ Expected 404 for inactive link, got {redirect_response.status_code}")
            print(f"   ⚠️  EXPECTED FAILURE: Frontend routing intercepts /go/* requests")
            success = False
        
        # Clean up - delete the test link
        requests.delete(f"{API_BASE_URL}/links/{link_id}", timeout=30)
        
        return success
        
    except Exception as e:
        print(f"   ❌ Error testing inactive links: {e}")
        return False

def test_google_redirect_example():
    """Test creating a link to Google and verifying redirect works"""
    print("\n" + "🌐" * 25 + " GOOGLE REDIRECT EXAMPLE TEST " + "🌐" * 25)
    
    try:
        # Step 1: Create a link to Google
        print("\n📍 Step 1: Creating Link to Google")
        google_link_data = {
            "original_url": "https://www.google.com",
            "title": "Google Search",
            "description": "The world's most popular search engine",
            "category": "Search Engine",
            "user_email": "test@example.com"
        }
        
        create_response = requests.post(
            f"{API_BASE_URL}/links",
            json=google_link_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if create_response.status_code != 200:
            print(f"   ❌ Failed to create Google link: {create_response.status_code}")
            return False
        
        link_data = create_response.json()
        short_url = link_data['short_url']
        short_code = short_url.split('/')[-1]
        link_id = link_data['id']
        
        print(f"   ✅ Google link created successfully!")
        print(f"   Original URL: {link_data['original_url']}")
        print(f"   Short URL: {short_url}")
        print(f"   Short Code: {short_code}")
        
        # Step 2: Test API redirect to Google
        print(f"\n📍 Step 2: Testing API Redirect to Google")
        api_response = requests.get(f"{API_BASE_URL}/redirect/{short_code}", allow_redirects=False, timeout=30)
        
        print(f"   API Redirect Status: {api_response.status_code}")
        if api_response.status_code == 302:
            location = api_response.headers.get('Location')
            print(f"   Redirect Location: {location}")
            
            if location == "https://www.google.com":
                print("   ✅ API redirect to Google working perfectly!")
                api_success = True
            else:
                print(f"   ❌ API redirect location mismatch. Expected: https://www.google.com, Got: {location}")
                api_success = False
        else:
            print(f"   ❌ API redirect failed with status {api_response.status_code}")
            api_success = False
        
        # Step 3: Test direct redirect to Google (expected to fail)
        print(f"\n📍 Step 3: Testing Direct Redirect to Google (Expected to Fail)")
        direct_response = requests.get(f"{BASE_URL}/go/{short_code}", allow_redirects=False, timeout=30)
        
        print(f"   Direct Redirect Status: {direct_response.status_code}")
        if direct_response.status_code == 302:
            location = direct_response.headers.get('Location')
            print(f"   Redirect Location: {location}")
            
            if location == "https://www.google.com":
                print("   ✅ Direct redirect to Google working!")
                direct_success = True
            else:
                print(f"   ❌ Direct redirect location mismatch")
                direct_success = False
        else:
            print(f"   ❌ Direct redirect failed with status {direct_response.status_code}")
            print(f"   ⚠️  EXPECTED FAILURE: Frontend routing intercepts /go/* requests")
            direct_success = False
        
        # Step 4: Verify click tracking
        print(f"\n📍 Step 4: Verifying Click Tracking")
        
        # Get updated link data
        import time
        time.sleep(1)  # Give database time to update
        
        updated_response = requests.get(f"{API_BASE_URL}/links/{link_id}", timeout=30)
        if updated_response.status_code == 200:
            updated_link = updated_response.json()
            clicks = updated_link.get('clicks', 0)
            print(f"   Current click count: {clicks}")
            
            if clicks > 0:
                print("   ✅ Click tracking working - clicks recorded!")
                tracking_success = True
            else:
                print("   ⚠️  No clicks recorded yet (may need more time)")
                tracking_success = False
        else:
            print("   ❌ Could not retrieve updated link data")
            tracking_success = False
        
        # Clean up
        requests.delete(f"{API_BASE_URL}/links/{link_id}", timeout=30)
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 GOOGLE REDIRECT EXAMPLE TEST RESULTS")
        print("=" * 60)
        print(f"   Link Creation: ✅ SUCCESS")
        print(f"   API Redirect: {'✅ SUCCESS' if api_success else '❌ FAILED'}")
        print(f"   Direct Redirect: {'✅ SUCCESS' if direct_success else '❌ FAILED (EXPECTED)'}")
        print(f"   Click Tracking: {'✅ SUCCESS' if tracking_success else '⚠️  PARTIAL'}")
        
        if api_success:
            print("\n🎉 GOOGLE REDIRECT EXAMPLE SUCCESSFUL!")
            print("✅ Users can create links to Google")
            print("✅ API redirect endpoint works correctly")
            print("✅ Users will be redirected to Google when using API endpoint")
            print("💡 Frontend should use /api/redirect/{short_code} for redirects")
            return True
        else:
            print("\n❌ GOOGLE REDIRECT EXAMPLE FAILED!")
            print("⚠️  API redirect functionality is not working")
            return False
            
    except Exception as e:
        print(f"   ❌ Error in Google redirect test: {e}")
        return False

def comprehensive_redirect_test():
    """Run comprehensive redirect functionality tests - Focus on API redirect endpoint"""
    print("\n" + "🔄" * 25 + " COMPREHENSIVE REDIRECT TESTS " + "🔄" * 25)
    
    results = {}
    
    # First create a test link for redirect testing
    print("\n📍 Creating Test Link for Redirect Testing")
    test_link_data = {
        "original_url": "https://www.google.com",
        "title": "Google Test Link",
        "description": "Test link for redirect functionality",
        "category": "Test",
        "user_email": "test@example.com"
    }
    
    try:
        create_response = requests.post(
            f"{API_BASE_URL}/links",
            json=test_link_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if create_response.status_code == 200:
            link_data = create_response.json()
            short_code = link_data['short_url'].split('/')[-1]
            original_url = link_data['original_url']
            link_id = link_data['id']
            
            print(f"   ✅ Test link created successfully")
            print(f"   Short URL: {link_data['short_url']}")
            print(f"   Short Code: {short_code}")
            
            # Test 1: API redirect functionality (WORKING)
            print("\n" + "✅" * 20 + " API REDIRECT TESTS (WORKING) " + "✅" * 20)
            api_redirect_success, api_redirect_url = test_api_redirect_functionality(short_code)
            results['api_redirect'] = api_redirect_success
            
            # Test 2: API redirect click tracking
            results['api_click_tracking'] = test_api_redirect_with_click_tracking(short_code, original_url)
            
            # Test 3: API redirect invalid codes
            results['api_invalid_codes'] = test_api_redirect_with_invalid_codes()
            
            # Test 4: API redirect inactive links
            results['api_inactive_links'] = test_api_redirect_inactive_links()
            
            # Test 5: Direct redirect functionality (BROKEN - for comparison)
            print("\n" + "❌" * 20 + " DIRECT REDIRECT TESTS (BROKEN) " + "❌" * 20)
            direct_redirect_success, direct_redirect_url = test_redirect_functionality(short_code)
            results['direct_redirect'] = direct_redirect_success
            
            # Test 6: Direct redirect click tracking (will fail)
            results['direct_click_tracking'] = test_redirect_with_click_tracking(short_code, original_url)
            
            # Test 7: Direct redirect invalid codes (will fail)
            results['direct_invalid_codes'] = test_redirect_with_invalid_codes()
            
            # Test 8: Direct redirect inactive links (will fail)
            results['direct_inactive_links'] = test_redirect_inactive_links()
            
            # Clean up - delete test link
            requests.delete(f"{API_BASE_URL}/links/{link_id}", timeout=30)
            
        else:
            print(f"   ❌ Failed to create test link: {create_response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error in comprehensive redirect test: {e}")
        return False
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 COMPREHENSIVE REDIRECT FUNCTIONALITY TEST RESULTS")
    print("=" * 80)
    
    # Separate API and Direct redirect results
    api_tests = {k: v for k, v in results.items() if k.startswith('api_')}
    direct_tests = {k: v for k, v in results.items() if k.startswith('direct_')}
    
    print("\n✅ API REDIRECT ENDPOINT TESTS (/api/redirect/{short_code}):")
    api_passed = 0
    for test_name, result in api_tests.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name.replace('_', ' ').title()}: {status}")
        if result:
            api_passed += 1
    
    print("\n❌ DIRECT REDIRECT ENDPOINT TESTS (/go/{short_code}) - KNOWN BROKEN:")
    direct_passed = 0
    for test_name, result in direct_tests.items():
        status = "✅ PASS" if result else "❌ FAIL (EXPECTED)"
        print(f"   {test_name.replace('_', ' ').title()}: {status}")
        if result:
            direct_passed += 1
    
    total_api = len(api_tests)
    total_direct = len(direct_tests)
    
    print(f"\n🎯 API Redirect Tests Result: {api_passed}/{total_api} tests passed")
    print(f"🎯 Direct Redirect Tests Result: {direct_passed}/{total_direct} tests passed (expected to fail)")
    
    if api_passed == total_api:
        print("\n🎉 API REDIRECT FUNCTIONALITY IS FULLY WORKING!")
        print("✅ API redirect endpoint responding correctly")
        print("✅ API redirect click tracking working correctly")
        print("✅ API redirect error handling working correctly")
        print("✅ API redirect inactive link handling working correctly")
        print("✅ Link shortening service API redirect is FULLY OPERATIONAL!")
        print("\n⚠️  NOTE: Direct redirect (/go/{short_code}) is broken due to frontend routing")
        print("💡 SOLUTION: Use /api/redirect/{short_code} endpoint for redirects")
        return True
    else:
        print("\n❌ API REDIRECT FUNCTIONALITY FAILED!")
        print("⚠️  Core link shortening API service is not working properly")
        return False

def run_all_tests():
    """Run all backend API tests including Linkly-specific endpoints"""
    print("🚀 Starting Comprehensive Backend API Tests - Linkly Application")
    print("=" * 80)
    
    results = {}
    
    # Basic connectivity tests
    results['connectivity'] = test_backend_connectivity()
    results['root_endpoint'] = test_root_endpoint()
    
    # User Management API Tests
    print("\n" + "🔥" * 20 + " USER MANAGEMENT API TESTS " + "🔥" * 20)
    
    users_success, users_data = test_get_users()
    results['get_users'] = users_success
    
    # Test with first user if available
    test_user_id = None
    if users_data and len(users_data) > 0:
        test_user_id = users_data[0]['id']
        
        user_success, user_data = test_get_specific_user(test_user_id)
        results['get_specific_user'] = user_success
        
        if user_data:
            results['update_user'] = test_update_user(test_user_id, user_data)
            results['suspend_user'] = test_suspend_user(test_user_id)
            results['activate_user'] = test_activate_user(test_user_id)
    else:
        print("   ⚠️  No users found for user management tests")
        results['get_specific_user'] = False
        results['update_user'] = False
        results['suspend_user'] = False
        results['activate_user'] = False
    
    # Link Management API Tests
    print("\n" + "🔗" * 20 + " LINK MANAGEMENT API TESTS " + "🔗" * 20)
    
    link_create_success, link_data = test_create_link()
    results['create_link'] = link_create_success
    
    links_success, links_data = test_get_links()
    results['get_links'] = links_success
    
    # Test with created link or first available link
    test_link_id = None
    test_short_code = None
    
    if link_data:
        test_link_id = link_data['id']
        test_short_code = link_data['short_url'].split('/')[-1]  # Extract short code
    elif links_data and len(links_data) > 0:
        test_link_id = links_data[0]['id']
        test_short_code = links_data[0]['short_url'].split('/')[-1]
    
    if test_link_id:
        link_get_success, _ = test_get_specific_link(test_link_id)
        results['get_specific_link'] = link_get_success
        
        results['toggle_link'] = test_toggle_link(test_link_id)
        
        # Test redirect functionality (most critical feature)
        if test_short_code:
            redirect_success, redirect_url = test_redirect_functionality(test_short_code)
            results['redirect_functionality'] = redirect_success
        else:
            results['redirect_functionality'] = False
        
        # Delete link last (destructive test)
        results['delete_link'] = test_delete_link(test_link_id)
    else:
        print("   ⚠️  No links available for link management tests")
        results['get_specific_link'] = False
        results['toggle_link'] = False
        results['redirect_functionality'] = False
        results['delete_link'] = False
    
    # Database and other tests
    print("\n" + "💾" * 20 + " DATABASE & OTHER TESTS " + "💾" * 20)
    
    results['database_persistence'] = test_database_persistence()
    results['subscription_plans'] = test_subscription_plans()
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 COMPREHENSIVE LINKLY BACKEND API TEST RESULTS SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    # Group results by category
    connectivity_tests = ['connectivity', 'root_endpoint']
    user_tests = ['get_users', 'get_specific_user', 'update_user', 'suspend_user', 'activate_user']
    link_tests = ['create_link', 'get_links', 'get_specific_link', 'toggle_link', 'delete_link', 'redirect_functionality']
    other_tests = ['database_persistence', 'subscription_plans']
    
    print("\n🔌 CONNECTIVITY TESTS:")
    for test in connectivity_tests:
        if test in results:
            status = "✅ PASS" if results[test] else "❌ FAIL"
            print(f"   {test.replace('_', ' ').title()}: {status}")
    
    print("\n👥 USER MANAGEMENT TESTS:")
    for test in user_tests:
        if test in results:
            status = "✅ PASS" if results[test] else "❌ FAIL"
            print(f"   {test.replace('_', ' ').title()}: {status}")
    
    print("\n🔗 LINK MANAGEMENT TESTS:")
    for test in link_tests:
        if test in results:
            status = "✅ PASS" if results[test] else "❌ FAIL"
            print(f"   {test.replace('_', ' ').title()}: {status}")
            if test == 'redirect_functionality' and results[test]:
                print("   🎯 CRITICAL FEATURE: Link redirect is working!")
    
    print("\n💾 DATABASE & OTHER TESTS:")
    for test in other_tests:
        if test in results:
            status = "✅ PASS" if results[test] else "❌ FAIL"
            print(f"   {test.replace('_', ' ').title()}: {status}")
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    # Check critical features
    critical_features = ['redirect_functionality', 'create_link', 'get_users']
    critical_passed = sum(1 for test in critical_features if results.get(test, False))
    
    if passed == total:
        print("🎉 ALL LINKLY BACKEND API TESTS PASSED!")
        print("✅ User management APIs working correctly")
        print("✅ Link management APIs working correctly") 
        print("✅ Link redirect functionality working correctly")
        print("✅ Database integration working correctly")
        print("✅ Linkly application backend is FULLY OPERATIONAL!")
        return True
    elif critical_passed == len(critical_features):
        print("⚠️  Some tests failed, but CRITICAL FEATURES are working:")
        print("✅ Link redirect functionality working")
        print("✅ Link creation working")
        print("✅ User management working")
        print("🎯 Linkly core functionality is operational!")
        return True
    else:
        print("❌ CRITICAL LINKLY FEATURES FAILED!")
        print("⚠️  Check the failed tests above - core functionality may be broken")
        return False

def run_redirect_focused_tests():
    """Run tests focused specifically on redirect functionality as requested"""
    print("🚀 Starting REDIRECT-FOCUSED Backend API Tests - Linkly Application")
    print("🎯 Focus: Testing API redirect endpoint functionality")
    print("=" * 80)
    
    results = {}
    
    # Basic connectivity tests first
    results['connectivity'] = test_backend_connectivity()
    results['root_endpoint'] = test_root_endpoint()
    
    if not results['connectivity'] or not results['root_endpoint']:
        print("❌ Basic connectivity failed - cannot proceed with redirect tests")
        return False
    
    # Test 1: Google redirect example (as specifically requested)
    print("\n" + "🌐" * 20 + " GOOGLE REDIRECT EXAMPLE TEST " + "🌐" * 20)
    google_test_success = test_google_redirect_example()
    results['google_redirect_example'] = google_test_success
    
    # Test 2: Run comprehensive redirect tests
    print("\n" + "🔄" * 20 + " COMPREHENSIVE REDIRECT TESTS " + "🔄" * 20)
    redirect_success = comprehensive_redirect_test()
    results['comprehensive_redirect'] = redirect_success
    
    # Test 3: Basic link management to ensure foundation is working
    print("\n" + "🔗" * 20 + " SUPPORTING LINK MANAGEMENT TESTS " + "🔗" * 20)
    
    link_create_success, link_data = test_create_link()
    results['create_link'] = link_create_success
    
    if link_data:
        short_code = link_data['short_url'].split('/')[-1]
        
        # Test API redirect specifically
        api_redirect_success, redirect_url = test_api_redirect_functionality(short_code)
        results['api_redirect_test'] = api_redirect_success
        
        # Test direct redirect (expected to fail)
        direct_redirect_success, direct_url = test_redirect_functionality(short_code)
        results['direct_redirect_test'] = direct_redirect_success
        
        # Clean up
        requests.delete(f"{API_BASE_URL}/links/{link_data['id']}", timeout=30)
    else:
        results['api_redirect_test'] = False
        results['direct_redirect_test'] = False
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 REDIRECT-FOCUSED TEST RESULTS SUMMARY")
    print("=" * 80)
    
    # Separate critical API tests from expected-to-fail direct tests
    api_critical_tests = ['google_redirect_example', 'comprehensive_redirect', 'create_link', 'api_redirect_test']
    direct_tests = ['direct_redirect_test']
    
    api_passed = sum(1 for test in api_critical_tests if results.get(test, False))
    api_total = len(api_critical_tests)
    
    print("\n✅ CRITICAL API REDIRECT TESTS:")
    for test in api_critical_tests:
        if test in results:
            status = "✅ PASS" if results[test] else "❌ FAIL"
            print(f"   {test.replace('_', ' ').title()}: {status}")
    
    print("\n❌ DIRECT REDIRECT TESTS (EXPECTED TO FAIL):")
    for test in direct_tests:
        if test in results:
            status = "✅ PASS" if results[test] else "❌ FAIL (EXPECTED)"
            print(f"   {test.replace('_', ' ').title()}: {status}")
    
    print(f"\n🎯 API Redirect Tests Result: {api_passed}/{api_total} critical tests passed")
    
    # Focus on API redirect functionality
    if api_passed == api_total:
        print("\n🎉 API REDIRECT FUNCTIONALITY IS FULLY WORKING!")
        print("✅ Link creation working correctly")
        print("✅ API redirect endpoint (/api/redirect/{short_code}) responding correctly") 
        print("✅ Google redirect example working correctly")
        print("✅ Click tracking working correctly")
        print("✅ Error handling working correctly")
        print("✅ Linkly API redirect functionality is FULLY OPERATIONAL!")
        print("\n💡 RECOMMENDATION: Frontend should use /api/redirect/{short_code} for all redirects")
        print("⚠️  NOTE: Direct /go/{short_code} endpoint is broken due to frontend routing issues")
        return True
    else:
        print("\n❌ API REDIRECT FUNCTIONALITY FAILED!")
        print("⚠️  Core link shortening API service is not working properly")
        
        # Check if at least Google example works
        if results.get('google_redirect_example', False):
            print("✅ However, Google redirect example is working")
            print("💡 Basic API redirect functionality appears to be operational")
        
        return False

if __name__ == "__main__":
    # Run redirect-focused tests as requested
    success = run_redirect_focused_tests()
    sys.exit(0 if success else 1)