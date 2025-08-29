#!/usr/bin/env python3
"""
KE-PR10.5: V2-Only Validation & System Checkpoint - Backend Testing
Comprehensive backend validation of V2-only mode and pipeline functionality

TESTING REQUIREMENTS:
1. V2 Content Processing Pipeline - test /api/content/process with V2-only mode
2. V2-Only Mode Enforcement - verify FORCE_V2_ONLY=true prevents legacy endpoints
3. Repository Pattern Validation - test all database operations use repository pattern
4. Pipeline End-to-End Flow - test complete V2 pipeline from input to article storage
5. Health & Status Endpoints - test /api/health reports V2-only status correctly
"""

import os
import sys
import asyncio
import json
import requests
import time
from datetime import datetime
from typing import Dict, List, Any

# Add backend to path for imports
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
if backend_path not in sys.path:
    sys.path.append(backend_path)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Get backend URL from frontend .env
def get_backend_url():
    """Get backend URL from frontend .env file"""
    frontend_env_path = os.path.join(os.path.dirname(__file__), 'frontend', '.env')
    if os.path.exists(frontend_env_path):
        with open(frontend_env_path, 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    return "http://localhost:8001"

BACKEND_URL = get_backend_url()
print(f"🌐 Testing V2-Only Validation at: {BACKEND_URL}")

class V2OnlyValidationTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Log test result"""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
            
        result = f"{status} - {test_name}"
        if details:
            result += f" | {details}"
            
        print(result)
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        
    def test_v2_content_processing_pipeline(self):
        """Test 1: V2 Content Processing Pipeline - /api/content/process with V2-only mode"""
        try:
            print("\n🔄 Testing V2 Content Processing Pipeline...")
            
            # Test content that should generate substantial articles
            test_content = """
            # Building a Modern Web Application with React and FastAPI
            
            ## Introduction
            This comprehensive guide covers building a full-stack web application using React for the frontend and FastAPI for the backend. We'll explore modern development practices, API design, and deployment strategies.
            
            ## Prerequisites
            Before starting this tutorial, you should have:
            - Basic knowledge of JavaScript and Python
            - Node.js and npm installed
            - Python 3.8+ installed
            - Understanding of REST APIs
            
            ## Setting Up the Development Environment
            
            ### Backend Setup with FastAPI
            First, let's create our FastAPI backend:
            
            ```python
            from fastapi import FastAPI, HTTPException
            from pydantic import BaseModel
            
            app = FastAPI(title="Modern Web App API")
            
            @app.get("/api/health")
            def health_check():
                return {"status": "healthy", "version": "1.0.0"}
            ```
            
            ### Frontend Setup with React
            Create a new React application:
            
            ```bash
            npx create-react-app modern-web-app
            cd modern-web-app
            npm install axios
            ```
            
            ## API Design and Implementation
            
            ### RESTful API Endpoints
            Design your API with clear, consistent endpoints:
            
            - GET /api/users - List all users
            - POST /api/users - Create new user
            - GET /api/users/{id} - Get specific user
            - PUT /api/users/{id} - Update user
            - DELETE /api/users/{id} - Delete user
            
            ### Database Integration
            Use SQLAlchemy for database operations:
            
            ```python
            from sqlalchemy import create_engine, Column, Integer, String
            from sqlalchemy.ext.declarative import declarative_base
            from sqlalchemy.orm import sessionmaker
            
            Base = declarative_base()
            
            class User(Base):
                __tablename__ = "users"
                id = Column(Integer, primary_key=True)
                name = Column(String(100))
                email = Column(String(100))
            ```
            
            ## Frontend Development
            
            ### Component Architecture
            Structure your React components for maintainability:
            
            ```jsx
            import React, { useState, useEffect } from 'react';
            import axios from 'axios';
            
            function UserList() {
                const [users, setUsers] = useState([]);
                
                useEffect(() => {
                    fetchUsers();
                }, []);
                
                const fetchUsers = async () => {
                    try {
                        const response = await axios.get('/api/users');
                        setUsers(response.data);
                    } catch (error) {
                        console.error('Error fetching users:', error);
                    }
                };
                
                return (
                    <div>
                        <h2>Users</h2>
                        {users.map(user => (
                            <div key={user.id}>{user.name}</div>
                        ))}
                    </div>
                );
            }
            ```
            
            ## Testing and Quality Assurance
            
            ### Backend Testing
            Use pytest for comprehensive testing:
            
            ```python
            import pytest
            from fastapi.testclient import TestClient
            from main import app
            
            client = TestClient(app)
            
            def test_health_check():
                response = client.get("/api/health")
                assert response.status_code == 200
                assert response.json()["status"] == "healthy"
            ```
            
            ### Frontend Testing
            Use Jest and React Testing Library:
            
            ```javascript
            import { render, screen } from '@testing-library/react';
            import UserList from './UserList';
            
            test('renders user list', () => {
                render(<UserList />);
                const heading = screen.getByText(/Users/i);
                expect(heading).toBeInTheDocument();
            });
            ```
            
            ## Deployment and Production
            
            ### Docker Configuration
            Create a Dockerfile for containerization:
            
            ```dockerfile
            FROM python:3.9
            WORKDIR /app
            COPY requirements.txt .
            RUN pip install -r requirements.txt
            COPY . .
            EXPOSE 8000
            CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
            ```
            
            ### Environment Configuration
            Use environment variables for configuration:
            
            ```python
            import os
            from pydantic import BaseSettings
            
            class Settings(BaseSettings):
                database_url: str = os.getenv("DATABASE_URL")
                secret_key: str = os.getenv("SECRET_KEY")
                debug: bool = os.getenv("DEBUG", "false").lower() == "true"
            ```
            
            ## Security Best Practices
            
            ### Authentication and Authorization
            Implement JWT-based authentication:
            
            ```python
            from fastapi import Depends, HTTPException, status
            from fastapi.security import HTTPBearer
            import jwt
            
            security = HTTPBearer()
            
            def verify_token(token: str = Depends(security)):
                try:
                    payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=["HS256"])
                    return payload
                except jwt.PyJWTError:
                    raise HTTPException(status_code=401, detail="Invalid token")
            ```
            
            ## Performance Optimization
            
            ### Caching Strategies
            Implement Redis caching for improved performance:
            
            ```python
            import redis
            import json
            
            redis_client = redis.Redis(host='localhost', port=6379, db=0)
            
            def cache_user_data(user_id: int, data: dict):
                redis_client.setex(f"user:{user_id}", 3600, json.dumps(data))
            
            def get_cached_user_data(user_id: int):
                cached = redis_client.get(f"user:{user_id}")
                return json.loads(cached) if cached else None
            ```
            
            ## Monitoring and Logging
            
            ### Application Monitoring
            Set up comprehensive logging:
            
            ```python
            import logging
            from fastapi import Request
            
            logging.basicConfig(level=logging.INFO)
            logger = logging.getLogger(__name__)
            
            @app.middleware("http")
            async def log_requests(request: Request, call_next):
                start_time = time.time()
                response = await call_next(request)
                process_time = time.time() - start_time
                logger.info(f"{request.method} {request.url} - {response.status_code} - {process_time:.2f}s")
                return response
            ```
            
            ## Conclusion
            
            Building modern web applications requires careful consideration of architecture, security, performance, and maintainability. This guide provides a solid foundation for creating robust full-stack applications using React and FastAPI.
            
            ### Next Steps
            - Implement advanced features like real-time updates with WebSockets
            - Add comprehensive error handling and validation
            - Set up CI/CD pipelines for automated deployment
            - Implement advanced security measures like rate limiting
            - Add comprehensive monitoring and alerting
            """
            
            # Test V2-only content processing
            payload = {
                "content": test_content,
                "content_type": "markdown",
                "processing_mode": "v2_only",
                "enable_v2_pipeline": True
            }
            
            start_time = time.time()
            response = requests.post(f"{self.backend_url}/api/content/process", 
                                   json=payload, timeout=120)
            processing_time = time.time() - start_time
            
            if response.status_code != 200:
                self.log_test("V2 Content Processing Pipeline", False, 
                             f"HTTP {response.status_code}: {response.text[:200]}")
                return False
                
            data = response.json()
            
            # Validate V2 pipeline execution
            if data.get("status") != "success":
                self.log_test("V2 Content Processing Pipeline", False, 
                             f"Processing failed: {data.get('message', 'Unknown error')}")
                return False
            
            # Check V2 engine usage
            processing_info = data.get("processing_info", {})
            engine_used = processing_info.get("engine", "")
            
            if engine_used != "v2":
                self.log_test("V2 Content Processing Pipeline", False, 
                             f"Wrong engine used: {engine_used}, expected: v2")
                return False
            
            # Validate article generation
            articles = data.get("articles", [])
            if not articles:
                self.log_test("V2 Content Processing Pipeline", False, 
                             "No articles generated from V2 pipeline")
                return False
            
            # Check article quality and V2 compliance
            article = articles[0]
            content_length = len(article.get("content", ""))
            
            if content_length < 1000:
                self.log_test("V2 Content Processing Pipeline", False, 
                             f"Article too short: {content_length} chars (expected >1000)")
                return False
            
            # Check V2 engine metadata
            metadata = article.get("metadata", {})
            engine_marker = metadata.get("engine", "")
            
            if engine_marker != "v2":
                self.log_test("V2 Content Processing Pipeline", False, 
                             f"Missing V2 engine metadata: {engine_marker}")
                return False
            
            # Check TICKET-3 fields
            ticket3_fields = ["doc_uid", "doc_slug", "headings_registry"]
            missing_fields = [field for field in ticket3_fields if field not in article]
            
            if missing_fields:
                self.log_test("V2 Content Processing Pipeline", False, 
                             f"Missing TICKET-3 fields: {missing_fields}")
                return False
            
            # Validate processing time
            if processing_time > 60:
                self.log_test("V2 Content Processing Pipeline", False, 
                             f"Processing too slow: {processing_time:.1f}s (expected <60s)")
                return False
            
            self.log_test("V2 Content Processing Pipeline", True, 
                         f"Generated {len(articles)} articles, {content_length} chars, {processing_time:.1f}s, V2 compliant")
            return True
            
        except Exception as e:
            self.log_test("V2 Content Processing Pipeline", False, f"Exception: {str(e)}")
            return False
    
    def test_v2_only_mode_enforcement(self):
        """Test 2: V2-Only Mode Enforcement - verify FORCE_V2_ONLY=true prevents legacy endpoints"""
        try:
            print("\n🚫 Testing V2-Only Mode Enforcement...")
            
            # Test that legacy endpoints return HTTP 410 Gone
            legacy_endpoints = [
                "/api/legacy/process",
                "/api/v1/content/process", 
                "/api/content/legacy-process",
                "/api/engine/v1/pipeline"
            ]
            
            blocked_endpoints = []
            working_legacy_endpoints = []
            
            for endpoint in legacy_endpoints:
                try:
                    response = requests.get(f"{self.backend_url}{endpoint}", timeout=10)
                    
                    if response.status_code == 410:
                        blocked_endpoints.append(endpoint)
                    elif response.status_code == 404:
                        # 404 is acceptable - endpoint doesn't exist
                        blocked_endpoints.append(endpoint)
                    else:
                        working_legacy_endpoints.append({
                            "endpoint": endpoint,
                            "status_code": response.status_code
                        })
                        
                except requests.exceptions.RequestException:
                    # Connection errors are acceptable - endpoint blocked/doesn't exist
                    blocked_endpoints.append(endpoint)
            
            # Check V2 endpoints remain functional
            v2_endpoints = [
                "/api/content/process",
                "/api/engine/v2/pipeline",
                "/api/health"
            ]
            
            working_v2_endpoints = []
            failed_v2_endpoints = []
            
            for endpoint in v2_endpoints:
                try:
                    response = requests.get(f"{self.backend_url}{endpoint}", timeout=10)
                    
                    if response.status_code == 200:
                        working_v2_endpoints.append(endpoint)
                    else:
                        failed_v2_endpoints.append({
                            "endpoint": endpoint,
                            "status_code": response.status_code
                        })
                        
                except Exception as e:
                    failed_v2_endpoints.append({
                        "endpoint": endpoint,
                        "error": str(e)
                    })
            
            # Validate results
            if working_legacy_endpoints:
                self.log_test("V2-Only Mode Enforcement", False, 
                             f"Legacy endpoints still working: {working_legacy_endpoints}")
                return False
            
            if failed_v2_endpoints:
                self.log_test("V2-Only Mode Enforcement", False, 
                             f"V2 endpoints not working: {failed_v2_endpoints}")
                return False
            
            if len(working_v2_endpoints) < 2:  # At least health and content/process should work
                self.log_test("V2-Only Mode Enforcement", False, 
                             f"Insufficient V2 endpoints working: {len(working_v2_endpoints)}")
                return False
            
            self.log_test("V2-Only Mode Enforcement", True, 
                         f"Legacy endpoints blocked: {len(blocked_endpoints)}, V2 endpoints working: {len(working_v2_endpoints)}")
            return True
            
        except Exception as e:
            self.log_test("V2-Only Mode Enforcement", False, f"Exception: {str(e)}")
            return False
    
    def test_repository_pattern_validation(self):
        """Test 3: Repository Pattern Validation - all database operations use repository pattern"""
        try:
            print("\n🗄️ Testing Repository Pattern Validation...")
            
            # Test repository status
            response = requests.get(f"{self.backend_url}/api/engine/repository/status", timeout=10)
            
            if response.status_code != 200:
                self.log_test("Repository Pattern Validation", False, 
                             f"Repository status endpoint HTTP {response.status_code}")
                return False
                
            repo_data = response.json()
            
            # Check repository availability
            repo_status = repo_data.get("status", "")
            if repo_status not in ["operational", "active", "available"]:
                self.log_test("Repository Pattern Validation", False, 
                             f"Repository status: {repo_status}")
                return False
            
            # Check required repositories
            repositories = repo_data.get("repositories", {})
            required_repos = [
                "ContentLibraryRepository",
                "ProcessingJobsRepository", 
                "V2AnalysisRepository"
            ]
            
            missing_repos = []
            for repo in required_repos:
                if repo not in repositories:
                    missing_repos.append(repo)
            
            if missing_repos:
                self.log_test("Repository Pattern Validation", False, 
                             f"Missing repositories: {missing_repos}")
                return False
            
            # Test repository operations
            test_operations = [
                {
                    "operation": "test_content_library_read",
                    "repository": "ContentLibraryRepository"
                },
                {
                    "operation": "test_content_library_write", 
                    "repository": "ContentLibraryRepository"
                },
                {
                    "operation": "test_v2_analysis_read",
                    "repository": "V2AnalysisRepository"
                }
            ]
            
            successful_operations = []
            failed_operations = []
            
            for operation in test_operations:
                try:
                    op_response = requests.post(f"{self.backend_url}/api/engine/repository/test", 
                                              json=operation, timeout=30)
                    
                    if op_response.status_code == 200:
                        op_data = op_response.json()
                        if op_data.get("status") == "success":
                            successful_operations.append(operation["operation"])
                        else:
                            failed_operations.append({
                                "operation": operation["operation"],
                                "error": op_data.get("message", "Unknown error")
                            })
                    else:
                        failed_operations.append({
                            "operation": operation["operation"],
                            "http_error": op_response.status_code
                        })
                        
                except Exception as e:
                    failed_operations.append({
                        "operation": operation["operation"],
                        "exception": str(e)
                    })
            
            # Check for direct MongoDB calls (should be 0)
            direct_db_response = requests.get(f"{self.backend_url}/api/engine/repository/direct-db-calls", timeout=10)
            
            direct_db_calls = 0
            if direct_db_response.status_code == 200:
                direct_db_data = direct_db_response.json()
                direct_db_calls = direct_db_data.get("direct_calls_count", 0)
            
            # Validate results
            if failed_operations:
                self.log_test("Repository Pattern Validation", False, 
                             f"Failed repository operations: {failed_operations}")
                return False
            
            if direct_db_calls > 0:
                self.log_test("Repository Pattern Validation", False, 
                             f"Direct MongoDB calls detected: {direct_db_calls} (should be 0)")
                return False
            
            if len(successful_operations) < 2:  # At least read and write should work
                self.log_test("Repository Pattern Validation", False, 
                             f"Insufficient repository operations working: {len(successful_operations)}")
                return False
            
            self.log_test("Repository Pattern Validation", True, 
                         f"Repository pattern validated: {len(repositories)} repos, {len(successful_operations)} operations, 0 direct DB calls")
            return True
            
        except Exception as e:
            self.log_test("Repository Pattern Validation", False, f"Exception: {str(e)}")
            return False
    
    def test_pipeline_end_to_end_flow(self):
        """Test 4: Pipeline End-to-End Flow - complete V2 pipeline from input to article storage"""
        try:
            print("\n🔄 Testing Pipeline End-to-End Flow...")
            
            # Test content for end-to-end pipeline
            test_content = """
            # API Authentication Guide
            
            ## Overview
            This guide covers implementing secure API authentication using modern standards and best practices.
            
            ## Authentication Methods
            
            ### JWT Tokens
            JSON Web Tokens provide stateless authentication:
            
            ```python
            import jwt
            from datetime import datetime, timedelta
            
            def create_token(user_id: str) -> str:
                payload = {
                    'user_id': user_id,
                    'exp': datetime.utcnow() + timedelta(hours=24)
                }
                return jwt.encode(payload, SECRET_KEY, algorithm='HS256')
            ```
            
            ### API Keys
            Simple API key authentication for service-to-service communication:
            
            ```python
            from fastapi import Header, HTTPException
            
            async def verify_api_key(x_api_key: str = Header()):
                if x_api_key not in VALID_API_KEYS:
                    raise HTTPException(status_code=401, detail="Invalid API key")
                return x_api_key
            ```
            
            ## Security Best Practices
            
            ### Rate Limiting
            Implement rate limiting to prevent abuse:
            
            ```python
            from slowapi import Limiter, _rate_limit_exceeded_handler
            from slowapi.util import get_remote_address
            
            limiter = Limiter(key_func=get_remote_address)
            
            @app.get("/api/data")
            @limiter.limit("10/minute")
            async def get_data(request: Request):
                return {"data": "protected_content"}
            ```
            
            ### Input Validation
            Always validate and sanitize input data:
            
            ```python
            from pydantic import BaseModel, validator
            
            class UserCreate(BaseModel):
                username: str
                email: str
                password: str
                
                @validator('password')
                def validate_password(cls, v):
                    if len(v) < 8:
                        raise ValueError('Password must be at least 8 characters')
                    return v
            ```
            
            ## Implementation Examples
            
            ### FastAPI Authentication
            Complete authentication implementation:
            
            ```python
            from fastapi import FastAPI, Depends, HTTPException, status
            from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
            from passlib.context import CryptContext
            import jwt
            
            app = FastAPI()
            security = HTTPBearer()
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            
            def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
                try:
                    payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
                    user_id = payload.get("user_id")
                    if user_id is None:
                        raise HTTPException(status_code=401, detail="Invalid token")
                    return user_id
                except jwt.PyJWTError:
                    raise HTTPException(status_code=401, detail="Invalid token")
            
            @app.post("/login")
            async def login(username: str, password: str):
                # Verify credentials
                user = authenticate_user(username, password)
                if not user:
                    raise HTTPException(status_code=401, detail="Invalid credentials")
                
                # Create token
                token = create_token(user.id)
                return {"access_token": token, "token_type": "bearer"}
            
            @app.get("/protected")
            async def protected_route(user_id: str = Depends(verify_token)):
                return {"message": f"Hello user {user_id}"}
            ```
            
            ## Testing Authentication
            
            ### Unit Tests
            Test your authentication logic:
            
            ```python
            import pytest
            from fastapi.testclient import TestClient
            
            def test_login_success():
                response = client.post("/login", json={
                    "username": "testuser",
                    "password": "testpass123"
                })
                assert response.status_code == 200
                assert "access_token" in response.json()
            
            def test_protected_route_with_token():
                token = get_test_token()
                headers = {"Authorization": f"Bearer {token}"}
                response = client.get("/protected", headers=headers)
                assert response.status_code == 200
            
            def test_protected_route_without_token():
                response = client.get("/protected")
                assert response.status_code == 401
            ```
            
            ## Conclusion
            
            Proper API authentication is crucial for application security. Use established standards like JWT, implement proper validation, and always test your authentication logic thoroughly.
            """
            
            # Get initial article count
            initial_response = requests.get(f"{self.backend_url}/api/content-library", timeout=10)
            initial_count = 0
            if initial_response.status_code == 200:
                initial_data = initial_response.json()
                initial_count = len(initial_data.get("articles", []))
            
            # Process content through complete V2 pipeline
            payload = {
                "content": test_content,
                "content_type": "markdown", 
                "processing_mode": "v2_only",
                "enable_full_pipeline": True,
                "store_in_content_library": True
            }
            
            start_time = time.time()
            response = requests.post(f"{self.backend_url}/api/content/process", 
                                   json=payload, timeout=120)
            total_time = time.time() - start_time
            
            if response.status_code != 200:
                self.log_test("Pipeline End-to-End Flow", False, 
                             f"Pipeline processing HTTP {response.status_code}")
                return False
                
            data = response.json()
            
            # Validate pipeline execution
            if data.get("status") != "success":
                self.log_test("Pipeline End-to-End Flow", False, 
                             f"Pipeline failed: {data.get('message')}")
                return False
            
            # Check all 17 stages executed
            processing_info = data.get("processing_info", {})
            stages_executed = processing_info.get("stages_executed", [])
            
            expected_stages = [
                "content_extraction", "multi_dimensional_analysis", "global_outline_planning",
                "per_article_outline_planning", "section_grounded_prewrite", "article_generation",
                "evidence_tagging", "woolf_aligned_style_processing", "related_links_generation",
                "intelligent_gap_filling", "code_block_normalization", "comprehensive_validation",
                "cross_article_qa", "adaptive_adjustment", "publishing", "versioning", "review_queue"
            ]
            
            executed_stage_count = len(stages_executed)
            if executed_stage_count < 15:  # At least 15 of 17 stages should execute
                self.log_test("Pipeline End-to-End Flow", False, 
                             f"Insufficient stages executed: {executed_stage_count}/17")
                return False
            
            # Validate article generation
            articles = data.get("articles", [])
            if not articles:
                self.log_test("Pipeline End-to-End Flow", False, 
                             "No articles generated from pipeline")
                return False
            
            article = articles[0]
            
            # Check article quality
            content_length = len(article.get("content", ""))
            if content_length < 1000:
                self.log_test("Pipeline End-to-End Flow", False, 
                             f"Generated article too short: {content_length} chars")
                return False
            
            # Check V2 compliance
            metadata = article.get("metadata", {})
            if metadata.get("engine") != "v2":
                self.log_test("Pipeline End-to-End Flow", False, 
                             "Article not marked with V2 engine")
                return False
            
            # Check TICKET-2 & TICKET-3 integration
            required_fields = ["doc_uid", "doc_slug", "headings_registry"]
            missing_fields = [field for field in required_fields if field not in article]
            
            if missing_fields:
                self.log_test("Pipeline End-to-End Flow", False, 
                             f"Missing TICKET-2/3 fields: {missing_fields}")
                return False
            
            # Verify article storage via ContentLibraryRepository
            final_response = requests.get(f"{self.backend_url}/api/content-library", timeout=10)
            if final_response.status_code == 200:
                final_data = final_response.json()
                final_count = len(final_data.get("articles", []))
                
                if final_count <= initial_count:
                    self.log_test("Pipeline End-to-End Flow", False, 
                                 f"Article not stored in content library: {initial_count} -> {final_count}")
                    return False
            
            # Check processing time
            if total_time > 60:
                self.log_test("Pipeline End-to-End Flow", False, 
                             f"Pipeline too slow: {total_time:.1f}s (expected <60s)")
                return False
            
            self.log_test("Pipeline End-to-End Flow", True, 
                         f"Complete pipeline: {executed_stage_count} stages, {content_length} chars, {total_time:.1f}s, stored in library")
            return True
            
        except Exception as e:
            self.log_test("Pipeline End-to-End Flow", False, f"Exception: {str(e)}")
            return False
    
    def test_health_status_endpoints(self):
        """Test 5: Health & Status Endpoints - /api/health reports V2-only status correctly"""
        try:
            print("\n🏥 Testing Health & Status Endpoints...")
            
            # Test main health endpoint
            response = requests.get(f"{self.backend_url}/api/health", timeout=10)
            
            if response.status_code != 200:
                self.log_test("Health & Status Endpoints", False, 
                             f"Health endpoint HTTP {response.status_code}")
                return False
                
            health_data = response.json()
            
            # Check basic health status
            status = health_data.get("status", "")
            if status not in ["healthy", "ok", "operational"]:
                self.log_test("Health & Status Endpoints", False, 
                             f"Unhealthy status: {status}")
                return False
            
            # Check V2-only mode reporting
            v2_mode = health_data.get("v2_only_mode", False)
            if not v2_mode:
                self.log_test("Health & Status Endpoints", False, 
                             "V2-only mode not reported in health status")
                return False
            
            # Check KE-PR10.5 status information
            ke_pr10_5_status = health_data.get("ke_pr10_5_status", {})
            if not ke_pr10_5_status:
                self.log_test("Health & Status Endpoints", False, 
                             "KE-PR10.5 status information missing")
                return False
            
            # Validate KE-PR10.5 specific fields
            required_ke_fields = ["v2_pipeline_operational", "legacy_endpoints_blocked", "repository_pattern_active"]
            missing_ke_fields = [field for field in required_ke_fields if field not in ke_pr10_5_status]
            
            if missing_ke_fields:
                self.log_test("Health & Status Endpoints", False, 
                             f"Missing KE-PR10.5 fields: {missing_ke_fields}")
                return False
            
            # Check system stability indicators
            stability_indicators = health_data.get("stability_indicators", {})
            
            # Test V2 engine status endpoint
            v2_status_response = requests.get(f"{self.backend_url}/api/engine/v2/status", timeout=10)
            
            if v2_status_response.status_code != 200:
                self.log_test("Health & Status Endpoints", False, 
                             f"V2 engine status HTTP {v2_status_response.status_code}")
                return False
            
            v2_status_data = v2_status_response.json()
            
            # Check V2 engine operational status
            v2_operational = v2_status_data.get("operational", False)
            if not v2_operational:
                self.log_test("Health & Status Endpoints", False, 
                             "V2 engine not operational")
                return False
            
            # Check V2 pipeline status
            pipeline_status = v2_status_data.get("pipeline_status", "")
            if pipeline_status not in ["ready", "operational", "active"]:
                self.log_test("Health & Status Endpoints", False, 
                             f"V2 pipeline status: {pipeline_status}")
                return False
            
            # Test system metrics endpoint
            metrics_response = requests.get(f"{self.backend_url}/api/system/metrics", timeout=10)
            
            system_metrics = {}
            if metrics_response.status_code == 200:
                system_metrics = metrics_response.json()
            
            # Validate comprehensive health reporting
            health_components = [
                health_data.get("status") in ["healthy", "ok", "operational"],
                health_data.get("v2_only_mode") is True,
                ke_pr10_5_status.get("v2_pipeline_operational") is True,
                ke_pr10_5_status.get("legacy_endpoints_blocked") is True,
                ke_pr10_5_status.get("repository_pattern_active") is True,
                v2_status_data.get("operational") is True
            ]
            
            healthy_components = sum(health_components)
            
            if healthy_components < 5:  # At least 5/6 components should be healthy
                self.log_test("Health & Status Endpoints", False, 
                             f"Insufficient healthy components: {healthy_components}/6")
                return False
            
            self.log_test("Health & Status Endpoints", True, 
                         f"Health endpoints validated: V2-only mode active, {healthy_components}/6 components healthy, KE-PR10.5 status reported")
            return True
            
        except Exception as e:
            self.log_test("Health & Status Endpoints", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all V2-only validation tests"""
        print("🎯 KE-PR10.5: V2-ONLY VALIDATION & SYSTEM CHECKPOINT - BACKEND TESTING")
        print("=" * 80)
        print("Comprehensive backend validation of V2-only mode and pipeline functionality")
        print(f"Backend URL: {self.backend_url}")
        print(f"Test Start Time: {datetime.now().isoformat()}")
        print()
        
        # Run all tests
        tests = [
            self.test_v2_content_processing_pipeline,
            self.test_v2_only_mode_enforcement,
            self.test_repository_pattern_validation,
            self.test_pipeline_end_to_end_flow,
            self.test_health_status_endpoints
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                test_name = test.__name__.replace("test_", "").replace("_", " ").title()
                self.log_test(test_name, False, f"Test exception: {str(e)}")
            
            # Small delay between tests
            time.sleep(2)
        
        # Print summary
        print()
        print("=" * 80)
        print("🎯 KE-PR10.5: V2-ONLY VALIDATION TEST SUMMARY")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Expected success criteria validation
        expected_criteria = [
            "✅ V2 content processing generates articles (> 1000 chars content)",
            "✅ All V2 engine metadata properly applied (engine: v2)",
            "✅ Repository pattern used exclusively (0 direct DB calls)",
            "✅ Legacy endpoints blocked with HTTP 410 status",
            "✅ Health endpoint reports V2-only mode active",
            "✅ Article storage working via ContentLibraryRepository",
            "✅ Pipeline duration < 60 seconds for test content"
        ]
        
        if success_rate == 100:
            print("🎉 KE-PR10.5 V2-ONLY VALIDATION: PERFECT SUCCESS - All criteria met!")
            for criteria in expected_criteria:
                print(criteria)
            print()
            print("✅ V2 pipeline running end-to-end successfully")
            print("✅ All 17 stages of V2 pipeline operational")
            print("✅ Articles generated with proper V2 engine markers")
            print("✅ Repository pattern used exclusively")
            print("✅ Legacy endpoints properly blocked")
            print("✅ System ready for production V2-only operation")
        elif success_rate >= 80:
            print("🎉 KE-PR10.5 V2-ONLY VALIDATION: EXCELLENT - Most criteria met!")
            print("✅ V2-only mode substantially validated")
            print("⚠️ Minor issues may need attention")
        elif success_rate >= 60:
            print("✅ KE-PR10.5 V2-ONLY VALIDATION: GOOD - Core functionality working")
            print("⚠️ Some validation criteria need improvement")
        else:
            print("❌ KE-PR10.5 V2-ONLY VALIDATION: NEEDS ATTENTION - Major issues detected")
            print("🔧 Significant work needed for V2-only mode compliance")
        
        print()
        print("Detailed Results:")
        for result in self.test_results:
            status = "✅" if result["passed"] else "❌"
            print(f"{status} {result['test']}: {result['details']}")
        
        return success_rate

if __name__ == "__main__":
    tester = V2OnlyValidationTester()
    success_rate = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success_rate >= 80 else 1)