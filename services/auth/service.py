"""
Authentication Service for the AI-driven learning platform.
Handles authentication, token lifecycle, role and organization resolution.
"""

import jwt
import datetime
from typing import Optional, Dict, Any
from enum import Enum


class TokenType(Enum):
    ACCESS = "access"
    REFRESH = "refresh"
    ORGANIZATION = "organization"


class AuthService:
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
        
    def generate_token(self, user_id: str, roles: list, org_id: str, token_type: TokenType = TokenType.ACCESS) -> str:
        """
        Generate JWT token with user information, roles, and organization.
        """
        payload = {
            "user_id": user_id,
            "roles": roles,
            "org_id": org_id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(
                hours=24 if token_type == TokenType.ACCESS else 168  # 24h for access, 7 days for refresh
            ),
            "iat": datetime.datetime.utcnow(),
            "type": token_type.value
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Validate JWT token and return payload if valid.
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def refresh_token(self, refresh_token: str) -> Optional[str]:
        """
        Refresh access token using refresh token.
        """
        payload = self.validate_token(refresh_token)
        if not payload or payload.get("type") != TokenType.REFRESH.value:
            return None
            
        # Generate new access token
        return self.generate_token(
            user_id=payload["user_id"],
            roles=payload["roles"],
            org_id=payload["org_id"],
            token_type=TokenType.ACCESS
        )
    
    def resolve_user_organization(self, user_id: str) -> Optional[str]:
        """
        Resolve user's organization based on user ID.
        In a real implementation, this would query a database.
        """
        # Placeholder implementation
        # In real system, this would fetch from user-org mapping table
        return f"org_{user_id[:3]}"
    
    def get_user_roles(self, user_id: str, org_id: str) -> list:
        """
        Get user roles within specific organization.
        """
        # Placeholder implementation
        # In real system, this would fetch from user-role-permission tables
        return ["learner"]  # Default role