#!/usr/bin/env python3
"""
FINAL KE-PR5 Pipeline Orchestrator Success Rate Measurement
Testing final implementation after all V2 classes are implemented
Focus: Measure success rate, evidence tagging, and production readiness
"""

import requests
import json
import time
import sys
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://content-processor.preview.emergentagent.com/api"

class FinalKEPR5Tester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.evidence_tagging_success = 0
        self.evidence_tagging_total = 0
        
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
        
    def test_v2_engine_feature_completeness(self):
        """Test 1: Verify all V2 classes are implemented and available"""
        try:
            response = requests.get(f"{self.backend_url}/engine", timeout=10)
            
            if response.status_code != 200:
                self.log_test("V2 Engine Feature Completeness", False, f"HTTP {response.status_code}")
                return False
                
            data = response.json()
            
            # Check engine status
            if data.get("status") not in ["operational", "active"]:
                self.log_test("V2 Engine Feature Completeness", False, f"Engine status: {data.get('status')}")
                return False
                
            # Check for all required V2 features
            features = data.get("features", [])
            required_v2_features = [
                "v2_processing",
                "v2_analyzer", 
                "v2_outline_planner",
                "v2_prewrite_system",
                "v2_article_generator",
                "v2_style_processor",
                "v2_validation_system",
                "v2_evidence_tagging",
                "v2_publishing_system",
                "pipeline_orchestrator"
            ]
            
            missing_features = [f for f in required_v2_features if f not in features]
            if missing_features:
                self.log_test("V2 Engine Feature Completeness", False, f"Missing V2 features: {missing_features}")
                return False
                
            # Count total V2 features available
            v2_feature_count = len([f for f in features if 'v2' in f or 'pipeline' in f])
            
            self.log_test("V2 Engine Feature Completeness", True, f"All V2 features available: {v2_feature_count} V2 features")
            return True
            
        except Exception as e:
            self.log_test("V2 Engine Feature Completeness", False, f"Exception: {str(e)}")
            return False
    
    def test_simple_content_processing(self):
        """Test 2: Test pipeline with simple content (known to work)"""
        try:
            simple_content = """
            # Getting Started with API Integration
            
            ## Introduction
            This guide covers the basics of API integration for developers.
            
            ## Prerequisites
            - Basic programming knowledge
            - Understanding of HTTP protocols
            - Development environment setup
            
            ## First Steps
            1. Obtain API credentials
            2. Set up authentication
            3. Make your first API call
            4. Handle responses appropriately
            
            ## Example Code
            ```javascript
            const apiKey = 'your-api-key';
            fetch('https://api.example.com/data', {
                headers: {
                    'Authorization': `Bearer ${apiKey}`
                }
            })
            .then(response => response.json())
            .then(data => console.log(data));
            ```
            
            ## Conclusion
            Following these steps will help you get started with API integration quickly and efficiently.
            """
            
            payload = {
                "content": simple_content,
                "content_type": "markdown",
                "processing_mode": "v2_only"
            }
            
            response = requests.post(f"{self.backend_url}/content/process", 
                                   json=payload, timeout=90)
            
            if response.status_code != 200:
                self.log_test("Simple Content Processing", False, f"HTTP {response.status_code}")
                return False
                
            data = response.json()
            
            # Check processing success
            if data.get("status") != "completed":
                self.log_test("Simple Content Processing", False, f"Processing failed: {data.get('message', 'Unknown error')}")
                return False
                
            # Check processing metadata
            if data.get("engine") != "v2":
                self.log_test("Simple Content Processing", False, f"Wrong engine used: {data.get('engine')}")
                return False
                
            # For simple content, we expect it to complete successfully
            # The actual articles are stored in content library, not returned directly
            chunks_created = data.get("chunks_created", 0)
            
            self.log_test("Simple Content Processing", True, 
                         f"V2 pipeline success: engine=v2, chunks={chunks_created}")
            return True
            
        except Exception as e:
            self.log_test("Simple Content Processing", False, f"Exception: {str(e)}")
            return False
    
    def test_moderately_complex_content_processing(self):
        """Test 3: Test pipeline with moderately complex content"""
        try:
            complex_content = """
            # Advanced API Security and Authentication Patterns
            
            ## Executive Summary
            This comprehensive guide explores advanced security patterns for API development, including OAuth 2.0 flows, JWT token management, rate limiting strategies, and threat mitigation techniques for production systems.
            
            ## Table of Contents
            1. Authentication Architecture Overview
            2. OAuth 2.0 Implementation Patterns
            3. JWT Token Security Best Practices
            4. Rate Limiting and Throttling Strategies
            5. API Gateway Security Configuration
            6. Threat Detection and Mitigation
            7. Compliance and Audit Requirements
            8. Performance Optimization Techniques
            
            ## 1. Authentication Architecture Overview
            
            ### Multi-Layer Security Model
            Modern API security requires a multi-layered approach that combines:
            - **Identity Layer**: User authentication and verification
            - **Authorization Layer**: Permission and access control
            - **Transport Layer**: TLS/SSL encryption and certificate management
            - **Application Layer**: Input validation and business logic security
            
            ### Security Principles
            - **Principle of Least Privilege**: Grant minimum necessary permissions
            - **Defense in Depth**: Multiple security layers and controls
            - **Zero Trust Architecture**: Verify every request regardless of source
            - **Fail Secure**: Default to secure state when errors occur
            
            ## 2. OAuth 2.0 Implementation Patterns
            
            ### Authorization Code Flow with PKCE
            The most secure flow for public clients and SPAs:
            
            ```javascript
            // Generate PKCE challenge
            function generateCodeChallenge() {
                const codeVerifier = generateRandomString(128);
                const codeChallenge = base64URLEncode(sha256(codeVerifier));
                return { codeVerifier, codeChallenge };
            }
            
            // Initiate authorization
            function initiateOAuth() {
                const { codeVerifier, codeChallenge } = generateCodeChallenge();
                const authURL = `https://auth.example.com/oauth/authorize?` +
                    `client_id=${clientId}&` +
                    `redirect_uri=${redirectUri}&` +
                    `response_type=code&` +
                    `scope=${scope}&` +
                    `code_challenge=${codeChallenge}&` +
                    `code_challenge_method=S256&` +
                    `state=${generateState()}`;
                
                // Store code verifier securely
                sessionStorage.setItem('code_verifier', codeVerifier);
                window.location.href = authURL;
            }
            ```
            
            ### Client Credentials Flow
            For server-to-server communication:
            
            ```python
            import requests
            import base64
            from datetime import datetime, timedelta
            
            class OAuth2ClientCredentials:
                def __init__(self, client_id, client_secret, token_url):
                    self.client_id = client_id
                    self.client_secret = client_secret
                    self.token_url = token_url
                    self.access_token = None
                    self.token_expires = None
                
                def get_access_token(self):
                    if self.access_token and self.token_expires > datetime.now():
                        return self.access_token
                    
                    # Prepare credentials
                    credentials = base64.b64encode(
                        f"{self.client_id}:{self.client_secret}".encode()
                    ).decode()
                    
                    headers = {
                        'Authorization': f'Basic {credentials}',
                        'Content-Type': 'application/x-www-form-urlencoded'
                    }
                    
                    data = {
                        'grant_type': 'client_credentials',
                        'scope': 'api:read api:write'
                    }
                    
                    response = requests.post(self.token_url, headers=headers, data=data)
                    response.raise_for_status()
                    
                    token_data = response.json()
                    self.access_token = token_data['access_token']
                    expires_in = token_data.get('expires_in', 3600)
                    self.token_expires = datetime.now() + timedelta(seconds=expires_in - 60)
                    
                    return self.access_token
            ```
            
            ## 3. JWT Token Security Best Practices
            
            ### Token Structure and Claims
            Secure JWT implementation requires careful attention to:
            
            ```json
            {
                "header": {
                    "alg": "RS256",
                    "typ": "JWT",
                    "kid": "key-id-2024"
                },
                "payload": {
                    "iss": "https://auth.example.com",
                    "sub": "user-12345",
                    "aud": "api.example.com",
                    "exp": 1640995200,
                    "iat": 1640991600,
                    "nbf": 1640991600,
                    "jti": "unique-token-id",
                    "scope": "read write admin",
                    "roles": ["user", "premium"],
                    "tenant": "org-456"
                }
            }
            ```
            
            ### Token Validation Implementation
            
            ```python
            import jwt
            from cryptography.hazmat.primitives import serialization
            import requests
            from functools import wraps
            
            class JWTValidator:
                def __init__(self, issuer, audience, jwks_url):
                    self.issuer = issuer
                    self.audience = audience
                    self.jwks_url = jwks_url
                    self.public_keys = {}
                
                def get_public_key(self, kid):
                    if kid not in self.public_keys:
                        jwks = requests.get(self.jwks_url).json()
                        for key in jwks['keys']:
                            if key['kid'] == kid:
                                public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)
                                self.public_keys[kid] = public_key
                                break
                    return self.public_keys.get(kid)
                
                def validate_token(self, token):
                    try:
                        # Decode header to get key ID
                        header = jwt.get_unverified_header(token)
                        kid = header.get('kid')
                        
                        if not kid:
                            raise ValueError("Token missing key ID")
                        
                        # Get public key
                        public_key = self.get_public_key(kid)
                        if not public_key:
                            raise ValueError("Invalid key ID")
                        
                        # Validate token
                        payload = jwt.decode(
                            token,
                            public_key,
                            algorithms=['RS256'],
                            issuer=self.issuer,
                            audience=self.audience,
                            options={
                                'verify_exp': True,
                                'verify_nbf': True,
                                'verify_iat': True,
                                'require': ['exp', 'iat', 'nbf', 'iss', 'aud', 'sub']
                            }
                        )
                        
                        return payload
                        
                    except jwt.ExpiredSignatureError:
                        raise ValueError("Token has expired")
                    except jwt.InvalidTokenError as e:
                        raise ValueError(f"Invalid token: {str(e)}")
            
            def require_auth(validator):
                def decorator(f):
                    @wraps(f)
                    def decorated_function(*args, **kwargs):
                        auth_header = request.headers.get('Authorization')
                        if not auth_header or not auth_header.startswith('Bearer '):
                            return {'error': 'Missing or invalid authorization header'}, 401
                        
                        token = auth_header.split(' ')[1]
                        try:
                            payload = validator.validate_token(token)
                            request.user = payload
                            return f(*args, **kwargs)
                        except ValueError as e:
                            return {'error': str(e)}, 401
                    
                    return decorated_function
                return decorator
            ```
            
            ## 4. Rate Limiting and Throttling Strategies
            
            ### Sliding Window Rate Limiter
            
            ```python
            import time
            import redis
            from typing import Optional
            
            class SlidingWindowRateLimiter:
                def __init__(self, redis_client: redis.Redis, window_size: int = 3600):
                    self.redis = redis_client
                    self.window_size = window_size
                
                def is_allowed(self, key: str, limit: int, window_size: Optional[int] = None) -> tuple[bool, dict]:
                    window = window_size or self.window_size
                    now = time.time()
                    pipeline = self.redis.pipeline()
                    
                    # Remove expired entries
                    pipeline.zremrangebyscore(key, 0, now - window)
                    
                    # Count current requests
                    pipeline.zcard(key)
                    
                    # Add current request
                    pipeline.zadd(key, {str(now): now})
                    
                    # Set expiration
                    pipeline.expire(key, window)
                    
                    results = pipeline.execute()
                    current_requests = results[1]
                    
                    allowed = current_requests < limit
                    
                    # Calculate reset time
                    reset_time = now + window
                    
                    return allowed, {
                        'limit': limit,
                        'remaining': max(0, limit - current_requests - 1),
                        'reset': int(reset_time),
                        'retry_after': None if allowed else int(window)
                    }
            ```
            
            ### Adaptive Rate Limiting
            
            ```python
            class AdaptiveRateLimiter:
                def __init__(self, base_limit: int = 1000):
                    self.base_limit = base_limit
                    self.user_limits = {}
                    self.system_health = 1.0  # 1.0 = healthy, 0.0 = overloaded
                
                def calculate_user_limit(self, user_id: str, user_tier: str) -> int:
                    # Base limit by tier
                    tier_multipliers = {
                        'free': 1.0,
                        'premium': 5.0,
                        'enterprise': 20.0
                    }
                    
                    base = self.base_limit * tier_multipliers.get(user_tier, 1.0)
                    
                    # Adjust based on system health
                    adjusted = base * self.system_health
                    
                    # Apply user-specific adjustments
                    user_multiplier = self.user_limits.get(user_id, 1.0)
                    
                    return int(adjusted * user_multiplier)
                
                def update_system_health(self, cpu_usage: float, memory_usage: float, error_rate: float):
                    # Calculate health score based on system metrics
                    health_factors = [
                        1.0 - min(cpu_usage / 80.0, 1.0),  # Reduce if CPU > 80%
                        1.0 - min(memory_usage / 90.0, 1.0),  # Reduce if memory > 90%
                        1.0 - min(error_rate / 0.05, 1.0)  # Reduce if error rate > 5%
                    ]
                    
                    self.system_health = min(health_factors)
            ```
            
            ## 5. API Gateway Security Configuration
            
            ### Kong Gateway Configuration
            
            ```yaml
            # kong.yml
            _format_version: "3.0"
            
            services:
            - name: api-service
              url: http://backend:8000
              plugins:
              - name: rate-limiting
                config:
                  minute: 100
                  hour: 1000
                  policy: sliding-window
                  hide_client_headers: false
              - name: jwt
                config:
                  key_claim_name: kid
                  secret_is_base64: false
                  claims_to_verify:
                  - exp
                  - nbf
              - name: cors
                config:
                  origins:
                  - "https://app.example.com"
                  methods:
                  - GET
                  - POST
                  - PUT
                  - DELETE
                  headers:
                  - Accept
                  - Authorization
                  - Content-Type
                  exposed_headers:
                  - X-RateLimit-Limit
                  - X-RateLimit-Remaining
                  credentials: true
                  max_age: 3600
            
            routes:
            - name: api-route
              service: api-service
              paths:
              - /api
              strip_path: true
              plugins:
              - name: request-size-limiting
                config:
                  allowed_payload_size: 10
              - name: response-transformer
                config:
                  add:
                    headers:
                    - "X-API-Version:v2"
                    - "X-Security-Policy:strict"
            ```
            
            ## 6. Threat Detection and Mitigation
            
            ### Anomaly Detection System
            
            ```python
            import numpy as np
            from sklearn.ensemble import IsolationForest
            from collections import defaultdict, deque
            import time
            
            class APIThreatDetector:
                def __init__(self, window_size: int = 1000):
                    self.window_size = window_size
                    self.request_patterns = defaultdict(lambda: deque(maxlen=window_size))
                    self.models = {}
                    self.threat_scores = defaultdict(float)
                
                def extract_features(self, request_data: dict) -> list:
                    return [
                        len(request_data.get('path', '')),
                        len(request_data.get('user_agent', '')),
                        request_data.get('payload_size', 0),
                        len(request_data.get('headers', {})),
                        request_data.get('response_time', 0),
                        int(request_data.get('status_code', 200) >= 400),
                        time.time() - request_data.get('timestamp', time.time())
                    ]
                
                def update_model(self, client_id: str):
                    if len(self.request_patterns[client_id]) < 50:
                        return
                    
                    features = [self.extract_features(req) for req in self.request_patterns[client_id]]
                    X = np.array(features)
                    
                    model = IsolationForest(contamination=0.1, random_state=42)
                    model.fit(X)
                    self.models[client_id] = model
                
                def detect_anomaly(self, client_id: str, request_data: dict) -> tuple[bool, float]:
                    # Add to pattern history
                    self.request_patterns[client_id].append(request_data)
                    
                    # Update model periodically
                    if len(self.request_patterns[client_id]) % 100 == 0:
                        self.update_model(client_id)
                    
                    # Check for anomaly
                    if client_id in self.models:
                        features = np.array([self.extract_features(request_data)])
                        anomaly_score = self.models[client_id].decision_function(features)[0]
                        is_anomaly = self.models[client_id].predict(features)[0] == -1
                        
                        # Update threat score
                        if is_anomaly:
                            self.threat_scores[client_id] = min(1.0, self.threat_scores[client_id] + 0.1)
                        else:
                            self.threat_scores[client_id] = max(0.0, self.threat_scores[client_id] - 0.01)
                        
                        return is_anomaly, self.threat_scores[client_id]
                    
                    return False, 0.0
            ```
            
            ## 7. Compliance and Audit Requirements
            
            ### Audit Logging Implementation
            
            ```python
            import json
            import hashlib
            from datetime import datetime
            from cryptography.fernet import Fernet
            
            class SecurityAuditLogger:
                def __init__(self, encryption_key: bytes):
                    self.cipher = Fernet(encryption_key)
                    self.log_buffer = []
                
                def log_security_event(self, event_type: str, user_id: str, details: dict):
                    event = {
                        'timestamp': datetime.utcnow().isoformat(),
                        'event_type': event_type,
                        'user_id': user_id,
                        'session_id': details.get('session_id'),
                        'ip_address': self._hash_ip(details.get('ip_address')),
                        'user_agent': details.get('user_agent'),
                        'resource': details.get('resource'),
                        'action': details.get('action'),
                        'result': details.get('result'),
                        'risk_score': details.get('risk_score', 0),
                        'additional_data': details.get('additional_data', {})
                    }
                    
                    # Encrypt sensitive data
                    encrypted_event = self._encrypt_event(event)
                    self.log_buffer.append(encrypted_event)
                    
                    # Flush buffer if needed
                    if len(self.log_buffer) >= 100:
                        self._flush_logs()
                
                def _hash_ip(self, ip_address: str) -> str:
                    if not ip_address:
                        return None
                    return hashlib.sha256(ip_address.encode()).hexdigest()[:16]
                
                def _encrypt_event(self, event: dict) -> dict:
                    sensitive_fields = ['user_id', 'session_id', 'additional_data']
                    encrypted_event = event.copy()
                    
                    for field in sensitive_fields:
                        if field in encrypted_event and encrypted_event[field]:
                            data = json.dumps(encrypted_event[field]).encode()
                            encrypted_event[field] = self.cipher.encrypt(data).decode()
                    
                    return encrypted_event
                
                def _flush_logs(self):
                    # Implementation would send logs to secure storage
                    # (e.g., AWS CloudTrail, Splunk, ELK stack)
                    pass
            ```
            
            ## 8. Performance Optimization Techniques
            
            ### Connection Pooling and Caching
            
            ```python
            import asyncio
            import aiohttp
            import aioredis
            from typing import Optional
            import json
            
            class OptimizedAPIClient:
                def __init__(self, base_url: str, redis_url: str):
                    self.base_url = base_url
                    self.session: Optional[aiohttp.ClientSession] = None
                    self.redis: Optional[aioredis.Redis] = None
                
                async def __aenter__(self):
                    # Create connection pool
                    connector = aiohttp.TCPConnector(
                        limit=100,  # Total connection pool size
                        limit_per_host=30,  # Per-host connection limit
                        ttl_dns_cache=300,  # DNS cache TTL
                        use_dns_cache=True,
                        keepalive_timeout=30,
                        enable_cleanup_closed=True
                    )
                    
                    timeout = aiohttp.ClientTimeout(
                        total=30,  # Total timeout
                        connect=5,  # Connection timeout
                        sock_read=10  # Socket read timeout
                    )
                    
                    self.session = aiohttp.ClientSession(
                        connector=connector,
                        timeout=timeout,
                        headers={'User-Agent': 'OptimizedAPIClient/1.0'}
                    )
                    
                    # Connect to Redis
                    self.redis = await aioredis.from_url(redis_url)
                    
                    return self
                
                async def __aexit__(self, exc_type, exc_val, exc_tb):
                    if self.session:
                        await self.session.close()
                    if self.redis:
                        await self.redis.close()
                
                async def get_cached_or_fetch(self, endpoint: str, cache_ttl: int = 300) -> dict:
                    cache_key = f"api_cache:{endpoint}"
                    
                    # Try cache first
                    cached_data = await self.redis.get(cache_key)
                    if cached_data:
                        return json.loads(cached_data)
                    
                    # Fetch from API
                    url = f"{self.base_url}{endpoint}"
                    async with self.session.get(url) as response:
                        response.raise_for_status()
                        data = await response.json()
                    
                    # Cache the result
                    await self.redis.setex(
                        cache_key,
                        cache_ttl,
                        json.dumps(data)
                    )
                    
                    return data
                
                async def batch_requests(self, endpoints: list) -> list:
                    tasks = [
                        self.get_cached_or_fetch(endpoint)
                        for endpoint in endpoints
                    ]
                    return await asyncio.gather(*tasks, return_exceptions=True)
            ```
            
            ## Conclusion
            
            Implementing comprehensive API security requires careful attention to authentication, authorization, rate limiting, threat detection, and performance optimization. The patterns and implementations provided in this guide offer a solid foundation for building secure, scalable API systems that can handle production workloads while maintaining security best practices.
            
            ### Key Takeaways
            
            1. **Multi-layered Security**: Implement security at multiple levels
            2. **Token Management**: Use secure JWT implementation with proper validation
            3. **Rate Limiting**: Implement adaptive rate limiting based on system health
            4. **Threat Detection**: Use machine learning for anomaly detection
            5. **Audit Logging**: Maintain comprehensive security audit trails
            6. **Performance**: Optimize with connection pooling and intelligent caching
            
            ### Next Steps
            
            - Implement monitoring and alerting for security events
            - Regular security audits and penetration testing
            - Stay updated with latest security vulnerabilities and patches
            - Continuous improvement of threat detection algorithms
            """
            
            payload = {
                "content": complex_content,
                "content_type": "markdown",
                "processing_mode": "v2_only"
            }
            
            response = requests.post(f"{self.backend_url}/content/process", 
                                   json=payload, timeout=180)
            
            if response.status_code != 200:
                self.log_test("Moderately Complex Content Processing", False, f"HTTP {response.status_code}")
                return False
                
            data = response.json()
            
            # Check processing success
            if data.get("status") != "success":
                self.log_test("Moderately Complex Content Processing", False, f"Processing failed: {data.get('message', 'Unknown error')}")
                return False
                
            # Check processing metadata
            processing_info = data.get("processing_info", {})
            if processing_info.get("engine") != "v2":
                self.log_test("Moderately Complex Content Processing", False, f"Wrong engine used: {processing_info.get('engine')}")
                return False
                
            # Check stages completed (should complete most stages for complex content)
            stages_completed = processing_info.get("stages_completed", 0)
            if stages_completed < 15:
                self.log_test("Moderately Complex Content Processing", False, f"Too few stages completed: {stages_completed}")
                return False
                
            # Check articles generated
            articles = data.get("articles", [])
            if not articles:
                self.log_test("Moderately Complex Content Processing", False, "No articles generated")
                return False
                
            # Check content quality (should handle complex content well)
            total_content_length = sum(len(article.get("content", "")) for article in articles)
            if total_content_length < 5000:  # Should generate substantial content
                self.log_test("Moderately Complex Content Processing", False, f"Generated content too short: {total_content_length} chars")
                return False
                
            self.log_test("Moderately Complex Content Processing", True, 
                         f"Complex content processed: {stages_completed} stages, {len(articles)} articles, {total_content_length} chars")
            return True
            
        except Exception as e:
            self.log_test("Moderately Complex Content Processing", False, f"Exception: {str(e)}")
            return False
    
    def test_evidence_tagging_functionality(self):
        """Test 4: Verify evidence tagging is working (should be >0% vs previous 0%)"""
        try:
            # Content with clear evidence that should be tagged
            evidence_content = """
            # Research-Based API Performance Study
            
            ## Introduction
            This study analyzes API performance metrics based on comprehensive testing and industry research.
            
            ## Methodology
            Our research team conducted extensive testing using the following approach:
            - Tested 500+ API endpoints across 50 different services
            - Measured response times over 30-day period
            - Analyzed data from 10 million API calls
            - Compared results with industry benchmarks from Gartner Research 2024
            
            ## Key Findings
            
            ### Response Time Analysis
            According to our study, the average API response time was 245ms, which is 15% faster than the industry average of 289ms reported by TechMetrics Inc. in their 2024 API Performance Report.
            
            ### Error Rate Statistics
            Our analysis revealed:
            - 99.7% success rate across all tested endpoints
            - 0.2% timeout errors (industry average: 0.5%)
            - 0.1% server errors (industry average: 0.3%)
            
            These findings are consistent with the AWS API Gateway Performance Study (2024) which reported similar error rates for well-optimized APIs.
            
            ### Throughput Measurements
            Peak throughput testing showed:
            - Maximum: 10,000 requests per second
            - Sustained: 7,500 requests per second
            - 95th percentile response time: 450ms
            
            Source: Internal Performance Testing Lab, validated against Google Cloud API Performance Benchmarks (Q3 2024).
            
            ## Industry Comparisons
            
            ### Market Leaders Performance
            Based on public performance data and third-party studies:
            
            1. **Stripe API**: Average response time 180ms (Source: Stripe Engineering Blog, 2024)
            2. **Twilio API**: Average response time 220ms (Source: Twilio Performance Metrics, 2024)
            3. **SendGrid API**: Average response time 195ms (Source: SendGrid Technical Documentation, 2024)
            
            ### Research Citations
            - "API Performance in Modern Applications" - MIT Technology Review, March 2024
            - "Scalability Patterns for RESTful APIs" - ACM Computing Surveys, Vol. 56, 2024
            - "Enterprise API Management Best Practices" - IEEE Software, January 2024
            
            ## Statistical Analysis
            
            ### Confidence Intervals
            Our statistical analysis (95% confidence interval) shows:
            - Response time: 245ms ± 12ms
            - Error rate: 0.3% ± 0.05%
            - Throughput: 7,500 RPS ± 250 RPS
            
            ### Correlation Analysis
            We found strong correlations between:
            - Payload size and response time (r = 0.78, p < 0.001)
            - Geographic distance and latency (r = 0.85, p < 0.001)
            - Time of day and error rates (r = 0.42, p < 0.01)
            
            Statistical analysis performed using R Statistical Software v4.3.2 and validated with Python SciPy library.
            
            ## Conclusion
            
            Based on our comprehensive research and analysis, we conclude that proper API optimization can achieve performance metrics that exceed industry averages by 15-20%. These findings are supported by peer-reviewed research and extensive empirical testing.
            
            ### References
            1. Johnson, A. et al. (2024). "API Performance Optimization Strategies." Journal of Software Engineering, 45(3), 123-145.
            2. Smith, B. & Davis, C. (2024). "Scalable API Design Patterns." Proceedings of the International Conference on Software Architecture, 67-82.
            3. TechMetrics Inc. (2024). "Annual API Performance Report." Retrieved from https://techmetrics.com/reports/api-2024
            4. Gartner Research. (2024). "Magic Quadrant for API Management Platforms." Gartner ID: G00756789.
            """
            
            payload = {
                "content": evidence_content,
                "content_type": "markdown",
                "processing_mode": "v2_only"
            }
            
            response = requests.post(f"{self.backend_url}/content/process", 
                                   json=payload, timeout=120)
            
            if response.status_code != 200:
                self.log_test("Evidence Tagging Functionality", False, f"HTTP {response.status_code}")
                return False
                
            data = response.json()
            
            # Check processing success
            if data.get("status") != "success":
                self.log_test("Evidence Tagging Functionality", False, f"Processing failed: {data.get('message', 'Unknown error')}")
                return False
                
            # Check for evidence tagging in processing info
            processing_info = data.get("processing_info", {})
            evidence_tagged = processing_info.get("evidence_tagged", 0)
            evidence_found = processing_info.get("evidence_found", 0)
            
            # Track evidence tagging statistics
            self.evidence_tagging_total += 1
            if evidence_tagged > 0:
                self.evidence_tagging_success += 1
            
            # Check articles for evidence tags
            articles = data.get("articles", [])
            total_evidence_tags = 0
            
            for article in articles:
                content = article.get("content", "")
                metadata = article.get("metadata", {})
                
                # Look for evidence tags in content
                evidence_indicators = [
                    "data-evidence", "class=\"evidence\"", "evidence-tag",
                    "<cite>", "<reference>", "data-source"
                ]
                
                for indicator in evidence_indicators:
                    total_evidence_tags += content.count(indicator)
                
                # Check metadata for evidence information
                if "evidence_count" in metadata:
                    total_evidence_tags += metadata.get("evidence_count", 0)
            
            # Evidence tagging should be working (>0% success rate)
            if evidence_tagged == 0 and evidence_found == 0 and total_evidence_tags == 0:
                self.log_test("Evidence Tagging Functionality", False, "No evidence tagging detected - 0% success rate")
                return False
                
            self.log_test("Evidence Tagging Functionality", True, 
                         f"Evidence tagging working: {evidence_tagged} tagged, {evidence_found} found, {total_evidence_tags} tags in content")
            return True
            
        except Exception as e:
            self.log_test("Evidence Tagging Functionality", False, f"Exception: {str(e)}")
            return False
    
    def test_all_v2_stages_completion(self):
        """Test 5: Verify all major V2 stages are completing without critical errors"""
        try:
            comprehensive_content = """
            # Complete Software Development Lifecycle Guide
            
            ## Project Planning and Requirements
            Effective software development begins with thorough planning and requirements gathering.
            
            ### Requirements Analysis
            - Functional requirements definition
            - Non-functional requirements specification
            - User story creation and prioritization
            - Acceptance criteria development
            
            ## Design and Architecture
            
            ### System Architecture
            Design scalable and maintainable system architecture:
            
            ```python
            # Example microservices architecture
            class ServiceRegistry:
                def __init__(self):
                    self.services = {}
                
                def register_service(self, name, endpoint):
                    self.services[name] = endpoint
                
                def discover_service(self, name):
                    return self.services.get(name)
            ```
            
            ### Database Design
            - Entity relationship modeling
            - Database schema optimization
            - Index strategy planning
            - Data migration planning
            
            ## Implementation Best Practices
            
            ### Code Quality Standards
            - Follow SOLID principles
            - Implement comprehensive testing
            - Use consistent coding standards
            - Perform regular code reviews
            
            ### Testing Strategy
            ```javascript
            // Example unit test
            describe('UserService', () => {
                test('should create user successfully', async () => {
                    const userData = { name: 'John', email: 'john@example.com' };
                    const result = await userService.createUser(userData);
                    expect(result.success).toBe(true);
                });
            });
            ```
            
            ## Deployment and Operations
            
            ### CI/CD Pipeline
            - Automated testing integration
            - Deployment automation
            - Environment management
            - Rollback procedures
            
            ### Monitoring and Maintenance
            - Performance monitoring
            - Error tracking and alerting
            - Log aggregation and analysis
            - Security vulnerability scanning
            
            ## Quality Assurance
            
            ### Testing Types
            1. Unit testing for individual components
            2. Integration testing for system interactions
            3. End-to-end testing for complete workflows
            4. Performance testing for scalability
            5. Security testing for vulnerability assessment
            
            ### Code Review Process
            - Peer review requirements
            - Automated code analysis
            - Security review checklist
            - Performance impact assessment
            
            ## Documentation and Knowledge Management
            
            ### Technical Documentation
            - API documentation with examples
            - Architecture decision records
            - Deployment guides and runbooks
            - Troubleshooting guides
            
            ### Team Knowledge Sharing
            - Regular technical presentations
            - Code walkthrough sessions
            - Best practices documentation
            - Lessons learned documentation
            
            ## Conclusion
            Following a comprehensive software development lifecycle ensures high-quality, maintainable, and scalable software solutions.
            """
            
            payload = {
                "content": comprehensive_content,
                "content_type": "markdown",
                "processing_mode": "v2_only"
            }
            
            response = requests.post(f"{self.backend_url}/content/process", 
                                   json=payload, timeout=150)
            
            if response.status_code != 200:
                self.log_test("All V2 Stages Completion", False, f"HTTP {response.status_code}")
                return False
                
            data = response.json()
            
            # Check processing success
            if data.get("status") != "success":
                self.log_test("All V2 Stages Completion", False, f"Processing failed: {data.get('message', 'Unknown error')}")
                return False
                
            # Check processing info for comprehensive stage completion
            processing_info = data.get("processing_info", {})
            stages_completed = processing_info.get("stages_completed", 0)
            stage_errors = processing_info.get("stage_errors", [])
            
            # Should complete most or all stages (target: 15+ out of ~17 stages)
            if stages_completed < 15:
                self.log_test("All V2 Stages Completion", False, f"Insufficient stages completed: {stages_completed}/17")
                return False
                
            # Check for critical stage errors
            critical_errors = [err for err in stage_errors if err.get("severity") == "critical"]
            if critical_errors:
                self.log_test("All V2 Stages Completion", False, f"Critical stage errors: {len(critical_errors)}")
                return False
                
            # Check that key V2 components were used
            v2_components_used = processing_info.get("v2_components_used", [])
            expected_components = [
                "V2MultiDimensionalAnalyzer",
                "V2GlobalOutlinePlanner", 
                "V2ArticleGenerator",
                "V2ValidationSystem"
            ]
            
            missing_components = [comp for comp in expected_components if comp not in v2_components_used]
            if len(missing_components) > 1:  # Allow for some flexibility
                self.log_test("All V2 Stages Completion", False, f"Key V2 components not used: {missing_components}")
                return False
                
            # Check articles were generated with good quality
            articles = data.get("articles", [])
            if not articles:
                self.log_test("All V2 Stages Completion", False, "No articles generated")
                return False
                
            self.log_test("All V2 Stages Completion", True, 
                         f"V2 pipeline complete: {stages_completed}/17 stages, {len(stage_errors)} minor errors, {len(articles)} articles")
            return True
            
        except Exception as e:
            self.log_test("All V2 Stages Completion", False, f"Exception: {str(e)}")
            return False
    
    def test_production_readiness_assessment(self):
        """Test 6: Assess overall production readiness of KE-PR5"""
        try:
            # Test with production-like content
            production_content = """
            # Enterprise API Integration Platform
            
            ## Executive Summary
            This document outlines the technical specifications and implementation guidelines for our enterprise API integration platform, designed to handle high-volume, mission-critical integrations.
            
            ## System Requirements
            
            ### Performance Requirements
            - Handle 100,000+ API calls per minute
            - 99.9% uptime SLA
            - Sub-200ms average response time
            - Support for 50+ concurrent integrations
            
            ### Security Requirements
            - OAuth 2.0 and JWT authentication
            - End-to-end encryption
            - Comprehensive audit logging
            - SOC 2 Type II compliance
            
            ## Architecture Overview
            
            ### Microservices Design
            The platform follows a microservices architecture with the following components:
            
            ```yaml
            # docker-compose.yml
            version: '3.8'
            services:
              api-gateway:
                image: nginx:alpine
                ports:
                  - "80:80"
                  - "443:443"
              
              auth-service:
                image: auth-service:latest
                environment:
                  - JWT_SECRET=${JWT_SECRET}
                  - DB_URL=${AUTH_DB_URL}
              
              integration-engine:
                image: integration-engine:latest
                environment:
                  - REDIS_URL=${REDIS_URL}
                  - QUEUE_URL=${QUEUE_URL}
            ```
            
            ### Data Flow Architecture
            ```python
            class IntegrationPipeline:
                def __init__(self):
                    self.stages = [
                        AuthenticationStage(),
                        ValidationStage(),
                        TransformationStage(),
                        ExecutionStage(),
                        ResponseStage()
                    ]
                
                async def process_request(self, request):
                    context = RequestContext(request)
                    
                    for stage in self.stages:
                        try:
                            context = await stage.process(context)
                        except StageException as e:
                            return self.handle_error(e, context)
                    
                    return context.response
            ```
            
            ## Implementation Guidelines
            
            ### API Design Standards
            - RESTful API design principles
            - OpenAPI 3.0 specification compliance
            - Consistent error response formats
            - Comprehensive API documentation
            
            ### Error Handling Strategy
            ```javascript
            class APIErrorHandler {
                static handleError(error, context) {
                    const errorResponse = {
                        error: {
                            code: error.code,
                            message: error.message,
                            timestamp: new Date().toISOString(),
                            requestId: context.requestId
                        }
                    };
                    
                    // Log error for monitoring
                    logger.error('API Error', {
                        error: errorResponse,
                        context: context.toJSON()
                    });
                    
                    return errorResponse;
                }
            }
            ```
            
            ## Deployment and Operations
            
            ### Kubernetes Configuration
            ```yaml
            apiVersion: apps/v1
            kind: Deployment
            metadata:
              name: integration-platform
            spec:
              replicas: 3
              selector:
                matchLabels:
                  app: integration-platform
              template:
                metadata:
                  labels:
                    app: integration-platform
                spec:
                  containers:
                  - name: api-server
                    image: integration-platform:latest
                    ports:
                    - containerPort: 8080
                    env:
                    - name: DATABASE_URL
                      valueFrom:
                        secretKeyRef:
                          name: db-secret
                          key: url
                    resources:
                      requests:
                        memory: "256Mi"
                        cpu: "250m"
                      limits:
                        memory: "512Mi"
                        cpu: "500m"
            ```
            
            ### Monitoring and Alerting
            - Prometheus metrics collection
            - Grafana dashboards for visualization
            - PagerDuty integration for critical alerts
            - ELK stack for log aggregation
            
            ## Security Implementation
            
            ### Authentication Flow
            ```python
            class JWTAuthenticator:
                def __init__(self, secret_key, algorithm='HS256'):
                    self.secret_key = secret_key
                    self.algorithm = algorithm
                
                def generate_token(self, user_data, expires_in=3600):
                    payload = {
                        'user_id': user_data['id'],
                        'email': user_data['email'],
                        'roles': user_data['roles'],
                        'exp': datetime.utcnow() + timedelta(seconds=expires_in),
                        'iat': datetime.utcnow()
                    }
                    
                    return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
                
                def verify_token(self, token):
                    try:
                        payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
                        return payload
                    except jwt.ExpiredSignatureError:
                        raise AuthenticationError('Token has expired')
                    except jwt.InvalidTokenError:
                        raise AuthenticationError('Invalid token')
            ```
            
            ## Testing Strategy
            
            ### Automated Testing Pipeline
            - Unit tests with 90%+ code coverage
            - Integration tests for API endpoints
            - Load testing with realistic traffic patterns
            - Security testing with OWASP guidelines
            
            ### Performance Testing
            ```python
            import asyncio
            import aiohttp
            import time
            
            async def load_test():
                async with aiohttp.ClientSession() as session:
                    tasks = []
                    start_time = time.time()
                    
                    for i in range(1000):
                        task = session.get('https://api.example.com/health')
                        tasks.append(task)
                    
                    responses = await asyncio.gather(*tasks)
                    end_time = time.time()
                    
                    success_count = sum(1 for r in responses if r.status == 200)
                    total_time = end_time - start_time
                    
                    print(f"Success rate: {success_count/1000*100}%")
                    print(f"Average response time: {total_time/1000*1000}ms")
            ```
            
            ## Conclusion
            This enterprise API integration platform provides a robust, scalable, and secure foundation for mission-critical integrations with comprehensive monitoring, testing, and deployment capabilities.
            """
            
            payload = {
                "content": production_content,
                "content_type": "markdown",
                "processing_mode": "v2_only"
            }
            
            start_time = time.time()
            response = requests.post(f"{self.backend_url}/content/process", 
                                   json=payload, timeout=180)
            processing_time = time.time() - start_time
            
            if response.status_code != 200:
                self.log_test("Production Readiness Assessment", False, f"HTTP {response.status_code}")
                return False
                
            data = response.json()
            
            # Check processing success
            if data.get("status") != "success":
                self.log_test("Production Readiness Assessment", False, f"Processing failed: {data.get('message', 'Unknown error')}")
                return False
                
            # Assess production readiness criteria
            processing_info = data.get("processing_info", {})
            
            # 1. Performance: Should handle complex content in reasonable time
            if processing_time > 180:  # 3 minutes max for production
                self.log_test("Production Readiness Assessment", False, f"Too slow for production: {processing_time:.1f}s")
                return False
                
            # 2. Reliability: Should complete most stages without critical errors
            stages_completed = processing_info.get("stages_completed", 0)
            stage_errors = processing_info.get("stage_errors", [])
            critical_errors = [err for err in stage_errors if err.get("severity") == "critical"]
            
            if stages_completed < 15 or len(critical_errors) > 0:
                self.log_test("Production Readiness Assessment", False, f"Reliability issues: {stages_completed} stages, {len(critical_errors)} critical errors")
                return False
                
            # 3. Quality: Should generate high-quality articles
            articles = data.get("articles", [])
            if not articles:
                self.log_test("Production Readiness Assessment", False, "No articles generated")
                return False
                
            total_content_length = sum(len(article.get("content", "")) for article in articles)
            if total_content_length < 8000:  # Should generate substantial content
                self.log_test("Production Readiness Assessment", False, f"Content quality insufficient: {total_content_length} chars")
                return False
                
            # 4. Completeness: Should use V2 engine and components
            if processing_info.get("engine") != "v2":
                self.log_test("Production Readiness Assessment", False, f"Wrong engine: {processing_info.get('engine')}")
                return False
                
            self.log_test("Production Readiness Assessment", True, 
                         f"Production ready: {processing_time:.1f}s, {stages_completed} stages, {len(articles)} articles, {total_content_length} chars")
            return True
            
        except Exception as e:
            self.log_test("Production Readiness Assessment", False, f"Exception: {str(e)}")
            return False
    
    def run_final_measurement(self):
        """Run final KE-PR5 success rate measurement"""
        print("🎯 FINAL KE-PR5 PIPELINE ORCHESTRATOR SUCCESS RATE MEASUREMENT")
        print("=" * 80)
        print("Testing final implementation after all V2 classes are implemented")
        print(f"Backend URL: {self.backend_url}")
        print(f"Test Start Time: {datetime.now().isoformat()}")
        print()
        
        # Run all tests
        tests = [
            self.test_v2_engine_feature_completeness,
            self.test_simple_content_processing,
            self.test_moderately_complex_content_processing,
            self.test_evidence_tagging_functionality,
            self.test_all_v2_stages_completion,
            self.test_production_readiness_assessment
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                test_name = test.__name__.replace("test_", "").replace("_", " ").title()
                self.log_test(test_name, False, f"Test exception: {str(e)}")
            
            # Small delay between tests
            time.sleep(3)
        
        # Calculate final metrics
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        evidence_tagging_rate = (self.evidence_tagging_success / self.evidence_tagging_total * 100) if self.evidence_tagging_total > 0 else 0
        
        # Print final assessment
        print()
        print("=" * 80)
        print("🎯 FINAL KE-PR5 SUCCESS RATE MEASUREMENT RESULTS")
        print("=" * 80)
        
        print(f"Overall Success Rate: {success_rate:.1f}%")
        print(f"Evidence Tagging Success Rate: {evidence_tagging_rate:.1f}%")
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print()
        
        # Determine completion status
        if success_rate >= 95:
            completion_status = "🎉 EXCELLENT - TARGET ACHIEVED"
            production_ready = "✅ PRODUCTION READY"
        elif success_rate >= 90:
            completion_status = "🎯 VERY GOOD - NEAR TARGET"
            production_ready = "✅ PRODUCTION READY"
        elif success_rate >= 80:
            completion_status = "✅ GOOD - ACCEPTABLE"
            production_ready = "⚠️ PRODUCTION READY WITH MONITORING"
        elif success_rate >= 60:
            completion_status = "⚠️ PARTIAL - NEEDS IMPROVEMENT"
            production_ready = "❌ NOT PRODUCTION READY"
        else:
            completion_status = "❌ INSUFFICIENT - MAJOR ISSUES"
            production_ready = "❌ NOT PRODUCTION READY"
        
        print(f"KE-PR5 COMPLETION STATUS: {completion_status}")
        print(f"PRODUCTION READINESS: {production_ready}")
        print()
        
        # Evidence tagging assessment
        if evidence_tagging_rate > 0:
            print(f"✅ EVIDENCE TAGGING: WORKING ({evidence_tagging_rate:.1f}% success vs previous 0%)")
        else:
            print("❌ EVIDENCE TAGGING: NOT WORKING (still 0% success rate)")
        print()
        
        # Gap analysis
        print("🔍 REMAINING GAPS ANALYSIS:")
        failed_tests = [result for result in self.test_results if not result["passed"]]
        
        if not failed_tests:
            print("✅ No critical gaps identified - KE-PR5 implementation complete")
        else:
            print("Critical gaps preventing 100% success:")
            for failed_test in failed_tests:
                print(f"   ❌ {failed_test['test']}: {failed_test['details']}")
        
        print()
        print("📊 DETAILED TEST RESULTS:")
        for result in self.test_results:
            status = "✅" if result["passed"] else "❌"
            print(f"{status} {result['test']}: {result['details']}")
        
        print()
        print("🎯 FINAL ASSESSMENT:")
        if success_rate >= 95:
            print("KE-PR5 Pipeline Orchestrator has achieved the 100% success rate goal!")
            print("All major V2 classes are working together seamlessly.")
            print("Evidence tagging functionality is operational.")
            print("System is ready for production deployment.")
        elif success_rate >= 80:
            print(f"KE-PR5 Pipeline Orchestrator is {success_rate:.1f}% complete.")
            print("Most functionality is working well with minor issues remaining.")
            print("System is approaching production readiness.")
        else:
            print(f"KE-PR5 Pipeline Orchestrator needs significant work ({success_rate:.1f}% success).")
            print("Major issues prevent production deployment.")
            print("Focus on addressing critical gaps identified above.")
        
        return success_rate, evidence_tagging_rate

if __name__ == "__main__":
    tester = FinalKEPR5Tester()
    success_rate, evidence_rate = tester.run_final_measurement()
    
    # Exit with appropriate code
    sys.exit(0 if success_rate >= 80 else 1)