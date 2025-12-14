"""
Feature flags service for the AI-driven learning platform.
Implements feature flag management for controlled rollouts and experimentation.
"""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from enum import Enum
import json
import hashlib


class FeatureFlagStatus(Enum):
    ENABLED = "enabled"
    DISABLED = "disabled"
    ARCHIVED = "archived"


class RolloutStrategy(Enum):
    PERCENTAGE = "percentage"
    USER_LIST = "user_list"
    ORGANIZATION = "organization"
    GRADUAL = "gradual"


class FeatureFlag:
    """Represents a feature flag."""
    def __init__(self, name: str, description: str, status: FeatureFlagStatus,
                 rollout_percentage: float = 0.0, user_list: List[str] = None,
                 org_list: List[str] = None, created_at: datetime = None):
        self.name = name
        self.description = description
        self.status = status
        self.rollout_percentage = rollout_percentage
        self.user_list = user_list or []
        self.org_list = org_list or []
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.version = 1


class FeatureFlagService:
    def __init__(self):
        self.flags: Dict[str, FeatureFlag] = {}
        self.audit_log = []
    
    def create_flag(self, name: str, description: str, 
                   initial_status: FeatureFlagStatus = FeatureFlagStatus.DISABLED,
                   rollout_percentage: float = 0.0,
                   user_list: List[str] = None, org_list: List[str] = None) -> FeatureFlag:
        """
        Create a new feature flag.
        """
        if name in self.flags:
            raise ValueError(f"Feature flag '{name}' already exists")
        
        flag = FeatureFlag(
            name=name,
            description=description,
            status=initial_status,
            rollout_percentage=rollout_percentage,
            user_list=user_list,
            org_list=org_list
        )
        
        self.flags[name] = flag
        self._log_audit("create_flag", name, {"status": initial_status.value})
        
        return flag
    
    def update_flag(self, name: str, **updates) -> Optional[FeatureFlag]:
        """
        Update an existing feature flag.
        """
        if name not in self.flags:
            return None
        
        flag = self.flags[name]
        
        # Update fields if provided
        if "description" in updates:
            flag.description = updates["description"]
        if "status" in updates:
            flag.status = updates["status"]
        if "rollout_percentage" in updates:
            flag.rollout_percentage = updates["rollout_percentage"]
        if "user_list" in updates:
            flag.user_list = updates["user_list"]
        if "org_list" in updates:
            flag.org_list = updates["org_list"]
        
        flag.updated_at = datetime.utcnow()
        flag.version += 1
        
        self._log_audit("update_flag", name, updates)
        
        return flag
    
    def delete_flag(self, name: str) -> bool:
        """
        Delete a feature flag.
        """
        if name not in self.flags:
            return False
        
        # Archive instead of hard delete
        flag = self.flags[name]
        flag.status = FeatureFlagStatus.ARCHIVED
        flag.updated_at = datetime.utcnow()
        
        self._log_audit("archive_flag", name, {})
        
        return True
    
    def is_enabled(self, name: str, user_id: str = None, org_id: str = None,
                   context: Dict[str, Any] = None) -> bool:
        """
        Check if a feature flag is enabled for a specific user/org.
        """
        if name not in self.flags:
            return False
        
        flag = self.flags[name]
        
        # If flag is disabled or archived, return False
        if flag.status != FeatureFlagStatus.ENABLED:
            return False
        
        # Check if user is in allow list
        if user_id and flag.user_list and user_id in flag.user_list:
            return True
        
        # Check if org is in allow list
        if org_id and flag.org_list and org_id in flag.org_list:
            return True
        
        # Check percentage rollout
        if flag.rollout_percentage > 0:
            if user_id:
                # Use user_id to determine if enabled based on percentage
                user_hash = int(hashlib.md5(user_id.encode()).hexdigest(), 16)
                return (user_hash % 100) < flag.rollout_percentage
            elif org_id:
                # Use org_id to determine if enabled based on percentage
                org_hash = int(hashlib.md5(org_id.encode()).hexdigest(), 16)
                return (org_hash % 100) < flag.rollout_percentage
        
        # For gradual rollout, we can implement more sophisticated logic
        # based on time, user attributes, etc.
        if context and "rollout_strategy" in context:
            strategy = context["rollout_strategy"]
            if strategy == RolloutStrategy.GRADUAL:
                return self._evaluate_gradual_rollout(flag, user_id, org_id, context)
        
        # Default: not enabled
        return False
    
    def _evaluate_gradual_rollout(self, flag: FeatureFlag, user_id: str = None,
                                org_id: str = None, context: Dict[str, Any] = None) -> bool:
        """
        Evaluate gradual rollout strategy.
        """
        # This is a simplified implementation - in a real system, this would
        # consider various factors like time-based rollout, user segments, etc.
        if context and "rollout_schedule" in context:
            schedule = context["rollout_schedule"]
            current_time = datetime.utcnow()
            
            if "start_time" in schedule:
                start_time = datetime.fromisoformat(schedule["start_time"])
                if current_time < start_time:
                    return False
            
            if "end_time" in schedule:
                end_time = datetime.fromisoformat(schedule["end_time"])
                if current_time > end_time:
                    return True  # Fully rolled out after end time
            
            # Gradually increase percentage over time
            if "start_percentage" in schedule and "end_percentage" in schedule:
                start_pct = schedule["start_percentage"]
                end_pct = schedule["end_percentage"]
                
                if "duration_hours" in schedule:
                    duration = schedule["duration_hours"] * 3600  # Convert to seconds
                    elapsed = (current_time - start_time).total_seconds()
                    progress = min(elapsed / duration, 1.0)
                    current_percentage = start_pct + (end_pct - start_pct) * progress
                    
                    if user_id:
                        user_hash = int(hashlib.md5(user_id.encode()).hexdigest(), 16)
                        return (user_hash % 100) < current_percentage
                    elif org_id:
                        org_hash = int(hashlib.md5(org_id.encode()).hexdigest(), 16)
                        return (org_hash % 100) < current_percentage
        
        return False
    
    def list_flags(self, status: FeatureFlagStatus = None) -> List[FeatureFlag]:
        """
        List all feature flags with optional status filter.
        """
        flags = list(self.flags.values())
        
        if status:
            flags = [flag for flag in flags if flag.status == status]
        
        return flags
    
    def get_flag(self, name: str) -> Optional[FeatureFlag]:
        """
        Get a specific feature flag by name.
        """
        return self.flags.get(name)
    
    def enable_flag(self, name: str) -> bool:
        """
        Enable a feature flag.
        """
        if name not in self.flags:
            return False
        
        self.flags[name].status = FeatureFlagStatus.ENABLED
        self.flags[name].updated_at = datetime.utcnow()
        
        self._log_audit("enable_flag", name, {})
        
        return True
    
    def disable_flag(self, name: str) -> bool:
        """
        Disable a feature flag.
        """
        if name not in self.flags:
            return False
        
        self.flags[name].status = FeatureFlagStatus.DISABLED
        self.flags[name].updated_at = datetime.utcnow()
        
        self._log_audit("disable_flag", name, {})
        
        return True
    
    def set_rollout_percentage(self, name: str, percentage: float) -> bool:
        """
        Set rollout percentage for a feature flag.
        """
        if name not in self.flags:
            return False
        
        if not 0 <= percentage <= 100:
            raise ValueError("Rollout percentage must be between 0 and 100")
        
        self.flags[name].rollout_percentage = percentage
        self.flags[name].updated_at = datetime.utcnow()
        
        self._log_audit("set_rollout_percentage", name, {"percentage": percentage})
        
        return True
    
    def add_users_to_flag(self, name: str, user_ids: List[str]) -> bool:
        """
        Add users to a feature flag's allow list.
        """
        if name not in self.flags:
            return False
        
        flag = self.flags[name]
        for user_id in user_ids:
            if user_id not in flag.user_list:
                flag.user_list.append(user_id)
        
        flag.updated_at = datetime.utcnow()
        
        self._log_audit("add_users_to_flag", name, {"user_ids": user_ids})
        
        return True
    
    def remove_users_from_flag(self, name: str, user_ids: List[str]) -> bool:
        """
        Remove users from a feature flag's allow list.
        """
        if name not in self.flags:
            return False
        
        flag = self.flags[name]
        flag.user_list = [user_id for user_id in flag.user_list if user_id not in user_ids]
        flag.updated_at = datetime.utcnow()
        
        self._log_audit("remove_users_from_flag", name, {"user_ids": user_ids})
        
        return True
    
    def _log_audit(self, action: str, flag_name: str, details: Dict[str, Any]):
        """
        Log an audit entry for flag operations.
        """
        audit_entry = {
            "timestamp": datetime.utcnow(),
            "action": action,
            "flag_name": flag_name,
            "details": details,
            "actor": "system"  # In a real system, this would be the user/service that made the change
        }
        
        self.audit_log.append(audit_entry)
        
        # Keep only recent audit logs (last 1000 entries)
        if len(self.audit_log) > 1000:
            self.audit_log = self.audit_log[-1000:]
    
    def get_audit_log(self, flag_name: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get audit log with optional flag filter.
        """
        audit_entries = self.audit_log[-limit:]
        
        if flag_name:
            audit_entries = [entry for entry in audit_entries if entry["flag_name"] == flag_name]
        
        return audit_entries
    
    def get_rollout_status(self, name: str) -> Dict[str, Any]:
        """
        Get detailed rollout status for a feature flag.
        """
        if name not in self.flags:
            return None
        
        flag = self.flags[name]
        
        return {
            "name": flag.name,
            "status": flag.status.value,
            "rollout_percentage": flag.rollout_percentage,
            "user_list_count": len(flag.user_list),
            "org_list_count": len(flag.org_list),
            "created_at": flag.created_at,
            "updated_at": flag.updated_at,
            "version": flag.version
        }


class FeatureFlagMiddleware:
    """
    Middleware for feature flag evaluation.
    """
    def __init__(self, feature_flag_service: FeatureFlagService):
        self.feature_flag_service = feature_flag_service
    
    def feature_enabled(self, flag_name: str, user_id: str = None, 
                       org_id: str = None, context: Dict[str, Any] = None):
        """
        Decorator to conditionally execute code based on feature flag.
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                if self.feature_flag_service.is_enabled(flag_name, user_id, org_id, context):
                    return func(*args, **kwargs)
                else:
                    # Return default value or raise exception based on configuration
                    return None  # Or some default behavior
            return wrapper
        return decorator


# Global feature flag service instance
feature_flag_service = FeatureFlagService()