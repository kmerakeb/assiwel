"""
Permission Service for the AI-driven learning platform.
Handles Role-Based Access Control (RBAC) and object-level access.
"""

from typing import List, Dict, Any, Optional
from enum import Enum


class PermissionAction(Enum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    EXECUTE = "execute"


class PermissionTarget(Enum):
    USER = "user"
    ORGANIZATION = "organization"
    LEARNING_ITEM = "learning_item"
    SESSION = "session"
    PROGRESS = "progress"
    CATEGORY = "category"


class PermissionService:
    def __init__(self):
        # In a real implementation, this would be loaded from a database
        self.role_permissions = {
            "admin": [
                {"action": PermissionAction.READ, "target": PermissionTarget.USER},
                {"action": PermissionAction.WRITE, "target": PermissionTarget.USER},
                {"action": PermissionAction.DELETE, "target": PermissionTarget.USER},
                {"action": PermissionAction.READ, "target": PermissionTarget.ORGANIZATION},
                {"action": PermissionAction.WRITE, "target": PermissionTarget.ORGANIZATION},
                {"action": PermissionAction.READ, "target": PermissionTarget.LEARNING_ITEM},
                {"action": PermissionAction.WRITE, "target": PermissionTarget.LEARNING_ITEM},
                {"action": PermissionAction.DELETE, "target": PermissionTarget.LEARNING_ITEM},
                {"action": PermissionAction.READ, "target": PermissionTarget.SESSION},
                {"action": PermissionAction.WRITE, "target": PermissionTarget.SESSION},
                {"action": PermissionAction.READ, "target": PermissionTarget.PROGRESS},
                {"action": PermissionAction.WRITE, "target": PermissionTarget.PROGRESS},
                {"action": PermissionAction.READ, "target": PermissionTarget.CATEGORY},
                {"action": PermissionAction.WRITE, "target": PermissionTarget.CATEGORY},
                {"action": PermissionAction.DELETE, "target": PermissionTarget.CATEGORY},
            ],
            "instructor": [
                {"action": PermissionAction.READ, "target": PermissionTarget.USER},
                {"action": PermissionAction.READ, "target": PermissionTarget.ORGANIZATION},
                {"action": PermissionAction.READ, "target": PermissionTarget.LEARNING_ITEM},
                {"action": PermissionAction.WRITE, "target": PermissionTarget.LEARNING_ITEM},
                {"action": PermissionAction.READ, "target": PermissionTarget.SESSION},
                {"action": PermissionAction.WRITE, "target": PermissionTarget.SESSION},
                {"action": PermissionAction.READ, "target": PermissionTarget.PROGRESS},
                {"action": PermissionAction.READ, "target": PermissionTarget.CATEGORY},
                {"action": PermissionAction.WRITE, "target": PermissionTarget.CATEGORY},
            ],
            "learner": [
                {"action": PermissionAction.READ, "target": PermissionTarget.LEARNING_ITEM},
                {"action": PermissionAction.READ, "target": PermissionTarget.SESSION},
                {"action": PermissionAction.WRITE, "target": PermissionTarget.SESSION},
                {"action": PermissionAction.READ, "target": PermissionTarget.PROGRESS},
                {"action": PermissionAction.WRITE, "target": PermissionTarget.PROGRESS},
                {"action": PermissionAction.READ, "target": PermissionTarget.CATEGORY},
            ]
        }
        
    def has_permission(self, user_id: str, role: str, action: PermissionAction, target: PermissionTarget, 
                      resource_id: Optional[str] = None, org_id: Optional[str] = None) -> bool:
        """
        Check if user has permission to perform action on target resource.
        """
        if role not in self.role_permissions:
            return False
            
        permissions = self.role_permissions[role]
        
        # Check basic role-based permission
        has_basic_permission = any(
            perm["action"] == action and perm["target"] == target
            for perm in permissions
        )
        
        if not has_basic_permission:
            return False
            
        # Additional checks could be added here for:
        # - Organization boundaries
        # - Object ownership
        # - Resource-specific rules
        # - Time-based restrictions
        
        return self._check_resource_specific_rules(user_id, role, action, target, resource_id, org_id)
    
    def _check_resource_specific_rules(self, user_id: str, role: str, action: PermissionAction, 
                                     target: PermissionTarget, resource_id: Optional[str], 
                                     org_id: Optional[str]) -> bool:
        """
        Apply resource-specific access rules beyond basic RBAC.
        """
        # Placeholder for object-level permissions
        # In real implementation, this would check ownership, sharing settings, etc.
        
        # For example, learners can only modify their own progress
        if role == "learner" and target == PermissionTarget.PROGRESS and action == PermissionAction.WRITE:
            # Learner can only update their own progress
            return resource_id == user_id or resource_id.startswith(f"user_{user_id}")
            
        # All other checks pass for now
        return True
    
    def get_available_actions(self, role: str, target: PermissionTarget) -> List[PermissionAction]:
        """
        Get all actions available for a role on a specific target.
        """
        if role not in self.role_permissions:
            return []
            
        return [
            perm["action"] for perm in self.role_permissions[role]
            if perm["target"] == target
        ]
    
    def validate_role_assignment(self, assigner_role: str, target_role: str, 
                               assigner_org: str, target_org: str) -> bool:
        """
        Validate if a role can be assigned to another user in the same organization.
        """
        # Admins can assign any role within their organization
        if assigner_role == "admin":
            return assigner_org == target_org
            
        # Instructors can assign learner role within their organization
        if assigner_role == "instructor" and target_role == "learner":
            return assigner_org == target_org
            
        return False