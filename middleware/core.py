"""
Middleware layer for the AI-driven learning platform.
Implements organization and tenant resolution, request authentication and role injection,
rate limiting, idempotency handling, request correlation IDs, locale and timezone detection,
AI usage metering, audit logging, and global error normalization.
"""

from typing import Dict, Any, Optional, Callable
from datetime import datetime, timezone
import uuid
import time
import hashlib
import json
from functools import wraps


class MiddlewareException(Exception):
    """Custom exception for middleware errors."""
    pass


class OrganizationTenantMiddleware:
    """Handles organization and tenant resolution."""
    
    def __init__(self, org_resolver_func: Callable = None):
        self.org_resolver_func = org_resolver_func or self._default_org_resolver
    
    def _default_org_resolver(self, request_headers: Dict[str, str]) -> Optional[str]:
        """Default organization resolver using header."""
        return request_headers.get('X-Organization-ID') or request_headers.get('X-Tenant-ID')
    
    def resolve_organization(self, request_headers: Dict[str, str]) -> Optional[str]:
        """Resolve organization from request headers."""
        return self.org_resolver_func(request_headers)


class AuthenticationMiddleware:
    """Handles request authentication and role injection."""
    
    def __init__(self, auth_service):
        self.auth_service = auth_service
    
    def authenticate_request(self, request_headers: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Authenticate request using token from headers."""
        auth_header = request_headers.get('Authorization', '')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header[7:]  # Remove 'Bearer ' prefix
        token_payload = self.auth_service.validate_token(token)
        
        if not token_payload:
            return None
        
        return token_payload


class RateLimitingMiddleware:
    """Implements rate limiting functionality."""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 3600):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.request_counts = {}
    
    def is_rate_limited(self, client_id: str) -> bool:
        """Check if client is rate limited."""
        now = time.time()
        window_start = now - self.window_seconds
        
        # Clean up old entries
        self.request_counts = {
            key: (count, timestamp) 
            for key, (count, timestamp) in self.request_counts.items() 
            if timestamp > window_start
        }
        
        # Check if client exists in current window
        if client_id in self.request_counts:
            count, timestamp = self.request_counts[client_id]
            if now - timestamp < self.window_seconds:
                if count >= self.max_requests:
                    return True
                else:
                    self.request_counts[client_id] = (count + 1, now)
            else:
                self.request_counts[client_id] = (1, now)
        else:
            self.request_counts[client_id] = (1, now)
        
        return False


class IdempotencyMiddleware:
    """Handles idempotency for safe request replay."""
    
    def __init__(self):
        self.idempotency_store = {}
    
    def check_idempotency(self, idempotency_key: str) -> Optional[Dict[str, Any]]:
        """Check if request with this idempotency key was already processed."""
        return self.idempotency_store.get(idempotency_key)
    
    def store_result(self, idempotency_key: str, result: Dict[str, Any]):
        """Store result for idempotency key."""
        self.idempotency_store[idempotency_key] = result


class CorrelationMiddleware:
    """Handles request correlation IDs for tracing."""
    
    def generate_correlation_id(self) -> str:
        """Generate a unique correlation ID for request tracing."""
        return str(uuid.uuid4())


class LocaleTimezoneMiddleware:
    """Detects locale and timezone from request."""
    
    def detect_locale(self, request_headers: Dict[str, str]) -> str:
        """Detect locale from request headers."""
        return request_headers.get('Accept-Language', 'en-US')
    
    def detect_timezone(self, request_headers: Dict[str, str]) -> str:
        """Detect timezone from request headers or parameters."""
        return request_headers.get('X-Timezone', 'UTC')


class AIUsageMeteringMiddleware:
    """Tracks and meters AI usage."""
    
    def __init__(self):
        self.usage_stats = {}
    
    def record_ai_usage(self, user_id: str, model: str, input_tokens: int, 
                       output_tokens: int, processing_time: float):
        """Record AI usage for metering."""
        if user_id not in self.usage_stats:
            self.usage_stats[user_id] = {}
        
        if model not in self.usage_stats[user_id]:
            self.usage_stats[user_id][model] = {
                "requests_count": 0,
                "input_tokens_total": 0,
                "output_tokens_total": 0,
                "total_processing_time": 0.0,
                "last_used": datetime.now(timezone.utc)
            }
        
        stats = self.usage_stats[user_id][model]
        stats["requests_count"] += 1
        stats["input_tokens_total"] += input_tokens
        stats["output_tokens_total"] += output_tokens
        stats["total_processing_time"] += processing_time
        stats["last_used"] = datetime.now(timezone.utc)
    
    def get_usage_summary(self, user_id: str, model: str = None) -> Dict[str, Any]:
        """Get AI usage summary for user or specific model."""
        if user_id not in self.usage_stats:
            return {}
        
        if model:
            return self.usage_stats[user_id].get(model, {})
        
        return self.usage_stats[user_id]


class AuditLoggingMiddleware:
    """Implements audit logging for compliance and security."""
    
    def __init__(self):
        self.audit_log = []
    
    def log_request(self, request_data: Dict[str, Any], user_id: str = None, 
                   org_id: str = None, action: str = None):
        """Log request for audit purposes."""
        audit_entry = {
            "timestamp": datetime.now(timezone.utc),
            "correlation_id": request_data.get("correlation_id"),
            "user_id": user_id,
            "org_id": org_id,
            "action": action,
            "endpoint": request_data.get("endpoint"),
            "method": request_data.get("method"),
            "ip_address": request_data.get("ip_address"),
            "user_agent": request_data.get("user_agent"),
            "request_size": len(json.dumps(request_data.get("body", {}))),
            "status_code": request_data.get("status_code", 200)
        }
        
        self.audit_log.append(audit_entry)
    
    def get_audit_trail(self, user_id: str = None, org_id: str = None, 
                       days_back: int = 30) -> list:
        """Get audit trail filtered by user or organization."""
        cutoff_date = datetime.now(timezone.utc) - datetime.timedelta(days=days_back)
        
        filtered_logs = [
            log for log in self.audit_log
            if log["timestamp"] >= cutoff_date
            and (not user_id or log["user_id"] == user_id)
            and (not org_id or log["org_id"] == org_id)
        ]
        
        return filtered_logs


class GlobalErrorNormalizationMiddleware:
    """Normalizes errors across the application."""
    
    def normalize_error(self, error: Exception, context: str = "") -> Dict[str, Any]:
        """Normalize error to standard format."""
        error_type = type(error).__name__
        error_message = str(error)
        
        # Categorize error
        if isinstance(error, MiddlewareException):
            error_category = "middleware_error"
            status_code = 400
        elif isinstance(error, ValueError):
            error_category = "validation_error"
            status_code = 400
        elif isinstance(error, PermissionError):
            error_category = "authorization_error"
            status_code = 403
        elif isinstance(error, FileNotFoundError):
            error_category = "resource_not_found"
            status_code = 404
        else:
            error_category = "system_error"
            status_code = 500
        
        return {
            "error_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": error_type,
            "category": error_category,
            "message": error_message,
            "context": context,
            "status_code": status_code,
            "details": {
                "args": error.args,
                "str": str(error)
            }
        }


class RequestProcessor:
    """Main request processor that combines all middleware."""
    
    def __init__(self, auth_service, permission_service):
        self.org_middleware = OrganizationTenantMiddleware()
        self.auth_middleware = AuthenticationMiddleware(auth_service)
        self.rate_limit_middleware = RateLimitingMiddleware()
        self.idempotency_middleware = IdempotencyMiddleware()
        self.correlation_middleware = CorrelationMiddleware()
        self.locale_middleware = LocaleTimezoneMiddleware()
        self.ai_metering_middleware = AIUsageMeteringMiddleware()
        self.audit_middleware = AuditLoggingMiddleware()
        self.error_middleware = GlobalErrorNormalizationMiddleware()
        
        self.auth_service = auth_service
        self.permission_service = permission_service
    
    def process_request(self, raw_request: Dict[str, Any]) -> Dict[str, Any]:
        """Process request through all middleware layers."""
        try:
            # Add correlation ID if not present
            correlation_id = raw_request.get('headers', {}).get('X-Correlation-ID')
            if not correlation_id:
                correlation_id = self.correlation_middleware.generate_correlation_id()
            
            # Create enriched request context
            request_context = {
                "correlation_id": correlation_id,
                "headers": raw_request.get('headers', {}),
                "body": raw_request.get('body', {}),
                "method": raw_request.get('method', 'GET'),
                "endpoint": raw_request.get('endpoint', ''),
                "ip_address": raw_request.get('ip_address', ''),
                "user_agent": raw_request.get('user_agent', ''),
            }
            
            # 1. Organization/Tenant resolution
            org_id = self.org_middleware.resolve_organization(request_context["headers"])
            if not org_id:
                raise MiddlewareException("Organization ID is required")
            
            # 2. Authentication
            auth_payload = self.auth_middleware.authenticate_request(request_context["headers"])
            if not auth_payload:
                raise MiddlewareException("Authentication required")
            
            user_id = auth_payload.get("user_id")
            user_roles = auth_payload.get("roles", [])
            
            # 3. Rate limiting
            client_id = f"{user_id}:{request_context['ip_address']}"
            if self.rate_limit_middleware.is_rate_limited(client_id):
                raise MiddlewareException("Rate limit exceeded")
            
            # 4. Idempotency check
            idempotency_key = request_context["headers"].get("Idempotency-Key")
            if idempotency_key:
                cached_result = self.idempotency_middleware.check_idempotency(idempotency_key)
                if cached_result:
                    return cached_result
            
            # 5. Locale and timezone detection
            locale = self.locale_middleware.detect_locale(request_context["headers"])
            timezone = self.locale_middleware.detect_timezone(request_context["headers"])
            
            # 6. Enhanced request context with middleware data
            enriched_context = {
                **request_context,
                "user_id": user_id,
                "org_id": org_id,
                "roles": user_roles,
                "locale": locale,
                "timezone": timezone,
                "authenticated": True
            }
            
            # Log the request for audit
            self.audit_middleware.log_request(
                request_data={
                    "correlation_id": correlation_id,
                    "endpoint": request_context["endpoint"],
                    "method": request_context["method"],
                    "ip_address": request_context["ip_address"],
                    "user_agent": request_context["user_agent"],
                    "body": request_context["body"],
                    "status_code": 200
                },
                user_id=user_id,
                org_id=org_id,
                action=f"{request_context['method']} {request_context['endpoint']}"
            )
            
            # Store idempotency result if key was provided
            if idempotency_key:
                self.idempotency_middleware.store_result(idempotency_key, enriched_context)
            
            return {
                "success": True,
                "context": enriched_context,
                "message": "Request processed successfully through all middleware"
            }
            
        except Exception as e:
            # Normalize error through error middleware
            error_response = self.error_middleware.normalize_error(e, "Request Processing")
            
            # Log failed request for audit
            self.audit_middleware.log_request(
                request_data={
                    "correlation_id": correlation_id if 'correlation_id' in locals() else None,
                    "endpoint": raw_request.get('endpoint', ''),
                    "method": raw_request.get('method', ''),
                    "ip_address": raw_request.get('ip_address', ''),
                    "user_agent": raw_request.get('user_agent', ''),
                    "status_code": error_response["status_code"]
                },
                user_id=auth_payload.get("user_id") if 'auth_payload' in locals() else None,
                org_id=org_id if 'org_id' in locals() else None,
                action=f"{raw_request.get('method', 'UNKNOWN')} {raw_request.get('endpoint', 'UNKNOWN')}"
            )
            
            return {
                "success": False,
                "error": error_response,
                "message": "Request failed middleware processing"
            }
    
    def check_permission(self, user_id: str, role: str, action: str, 
                        resource: str, org_id: str) -> bool:
        """Check user permissions using permission service."""
        # Convert string action/resource to appropriate enum values
        # This is a simplified implementation - in real system, map to proper enums
        from services.permission.service import PermissionAction, PermissionTarget
        
        action_map = {
            "read": PermissionAction.READ,
            "write": PermissionAction.WRITE,
            "delete": PermissionAction.DELETE,
            "execute": PermissionAction.EXECUTE
        }
        
        resource_map = {
            "user": PermissionTarget.USER,
            "organization": PermissionTarget.ORGANIZATION,
            "learning_item": PermissionTarget.LEARNING_ITEM,
            "session": PermissionTarget.SESSION,
            "progress": PermissionTarget.PROGRESS,
            "category": PermissionTarget.CATEGORY
        }
        
        perm_action = action_map.get(action.lower(), PermissionAction.READ)
        perm_target = resource_map.get(resource.lower(), PermissionTarget.USER)
        
        return self.permission_service.has_permission(
            user_id, role, perm_action, perm_target, org_id=org_id
        )


# Decorator for easy middleware integration
def apply_middleware(processor: RequestProcessor):
    """Decorator to apply middleware processing to functions."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract request from kwargs or args
            request = kwargs.get('request') or (args[0] if args else None)
            
            if request:
                # Process request through middleware
                result = processor.process_request(request)
                
                if not result["success"]:
                    return result  # Return error
                
                # Update request with enriched context
                enriched_request = result["context"]
                # Update the request object with enriched data
                if 'request' in kwargs:
                    kwargs['request'].update(enriched_request)
                elif args:
                    # If request is first argument, we need to handle differently
                    # This is a simplified approach - in real framework, this would be more sophisticated
                    pass
                
                # Add enriched context as additional parameter
                kwargs['enriched_context'] = enriched_request
            
            return func(*args, **kwargs)
        return wrapper
    return decorator