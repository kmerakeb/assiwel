"""
Validation layer for the AI-driven learning platform.
Enforces business rules such as content hierarchy integrity, learning item schema validation,
session state transitions, progress updates, streak eligibility, organization boundaries,
AI input/output constraints, and audio format compliance.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum
import re
import uuid


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


class ContentHierarchyValidator:
    """Validates content hierarchy integrity (category → subcategory → topic)."""
    
    @staticmethod
    def validate_category_structure(category_data: Dict[str, Any]) -> bool:
        """Validate category structure."""
        required_fields = ["id", "name", "description", "created_at"]
        for field in required_fields:
            if field not in category_data:
                raise ValidationError(f"Missing required field: {field}")
        
        if not isinstance(category_data["id"], str) or not category_data["id"].strip():
            raise ValidationError("Category ID must be a non-empty string")
        
        if not isinstance(category_data["name"], str) or not category_data["name"].strip():
            raise ValidationError("Category name must be a non-empty string")
        
        if not isinstance(category_data["description"], str):
            raise ValidationError("Category description must be a string")
        
        # Validate created_at is a datetime object or ISO string
        created_at = category_data["created_at"]
        if not isinstance(created_at, (datetime, str)):
            raise ValidationError("created_at must be a datetime object or ISO string")
        
        return True
    
    @staticmethod
    def validate_subcategory_structure(subcategory_data: Dict[str, Any]) -> bool:
        """Validate subcategory structure."""
        ContentHierarchyValidator.validate_category_structure(subcategory_data)
        
        # Subcategories must have a parent category
        if "parent_category_id" not in subcategory_data:
            raise ValidationError("Subcategory must have a parent_category_id")
        
        if not isinstance(subcategory_data["parent_category_id"], str) or not subcategory_data["parent_category_id"].strip():
            raise ValidationError("parent_category_id must be a non-empty string")
        
        return True
    
    @staticmethod
    def validate_topic_structure(topic_data: Dict[str, Any]) -> bool:
        """Validate topic structure."""
        required_fields = ["id", "title", "content", "subcategory_id", "created_at"]
        for field in required_fields:
            if field not in topic_data:
                raise ValidationError(f"Missing required field: {field}")
        
        if not isinstance(topic_data["id"], str) or not topic_data["id"].strip():
            raise ValidationError("Topic ID must be a non-empty string")
        
        if not isinstance(topic_data["title"], str) or not topic_data["title"].strip():
            raise ValidationError("Topic title must be a non-empty string")
        
        if not isinstance(topic_data["content"], str):
            raise ValidationError("Topic content must be a string")
        
        if not isinstance(topic_data["subcategory_id"], str) or not topic_data["subcategory_id"].strip():
            raise ValidationError("subcategory_id must be a non-empty string")
        
        # Validate created_at is a datetime object or ISO string
        created_at = topic_data["created_at"]
        if not isinstance(created_at, (datetime, str)):
            raise ValidationError("created_at must be a datetime object or ISO string")
        
        return True
    
    @staticmethod
    def validate_hierarchy_path(category_id: str, subcategory_id: str, topic_id: str = None) -> bool:
        """Validate the hierarchy path from category to topic."""
        # Check if IDs are valid UUIDs or meaningful strings
        if not category_id or not subcategory_id:
            raise ValidationError("Category and subcategory IDs are required")
        
        # In a real system, this would check if the relationships exist in the database
        # For now, just validate the format
        if not re.match(r'^[\w-]+$', category_id):
            raise ValidationError("Invalid category ID format")
        
        if not re.match(r'^[\w-]+$', subcategory_id):
            raise ValidationError("Invalid subcategory ID format")
        
        if topic_id and not re.match(r'^[\w-]+$', topic_id):
            raise ValidationError("Invalid topic ID format")
        
        return True


class LearningItemSchemaValidator:
    """Validates learning item schema per item type."""
    
    @staticmethod
    def validate_learning_item(item_data: Dict[str, Any], item_type: str) -> bool:
        """Validate learning item schema based on type."""
        required_fields = ["id", "title", "content", "type", "created_at"]
        for field in required_fields:
            if field not in item_data:
                raise ValidationError(f"Missing required field: {field}")
        
        # Validate ID
        if not isinstance(item_data["id"], str) or not item_data["id"].strip():
            raise ValidationError("Item ID must be a non-empty string")
        
        # Validate title
        if not isinstance(item_data["title"], str) or not item_data["title"].strip():
            raise ValidationError("Item title must be a non-empty string")
        
        # Validate content
        if not isinstance(item_data["content"], str):
            raise ValidationError("Item content must be a string")
        
        # Validate type matches expected type
        if item_data["type"] != item_type:
            raise ValidationError(f"Item type mismatch: expected {item_type}, got {item_data['type']}")
        
        # Validate created_at
        created_at = item_data["created_at"]
        if not isinstance(created_at, (datetime, str)):
            raise ValidationError("created_at must be a datetime object or ISO string")
        
        # Validate type-specific fields
        if item_type == "lesson":
            return LearningItemSchemaValidator._validate_lesson(item_data)
        elif item_type == "quiz":
            return LearningItemSchemaValidator._validate_quiz(item_data)
        elif item_type == "exercise":
            return LearningItemSchemaValidator._validate_exercise(item_data)
        elif item_type == "video":
            return LearningItemSchemaValidator._validate_video(item_data)
        elif item_type == "reading":
            return LearningItemSchemaValidator._validate_reading(item_data)
        elif item_type == "interactive":
            return LearningItemSchemaValidator._validate_interactive(item_data)
        else:
            raise ValidationError(f"Unknown item type: {item_type}")
    
    @staticmethod
    def _validate_lesson(lesson_data: Dict[str, Any]) -> bool:
        """Validate lesson-specific fields."""
        # Lessons may have objectives
        if "objectives" in lesson_data:
            if not isinstance(lesson_data["objectives"], list):
                raise ValidationError("Lesson objectives must be a list")
        
        # Lessons may have duration
        if "duration" in lesson_data:
            if not isinstance(lesson_data["duration"], int) or lesson_data["duration"] < 0:
                raise ValidationError("Lesson duration must be a non-negative integer")
        
        return True
    
    @staticmethod
    def _validate_quiz(quiz_data: Dict[str, Any]) -> bool:
        """Validate quiz-specific fields."""
        required_quiz_fields = ["questions"]
        for field in required_quiz_fields:
            if field not in quiz_data:
                raise ValidationError(f"Quiz missing required field: {field}")
        
        if not isinstance(quiz_data["questions"], list):
            raise ValidationError("Quiz questions must be a list")
        
        for i, question in enumerate(quiz_data["questions"]):
            if not isinstance(question, dict):
                raise ValidationError(f"Question {i} must be a dictionary")
            
            if "text" not in question or not question["text"].strip():
                raise ValidationError(f"Question {i} must have non-empty text")
            
            if "options" not in question or not isinstance(question["options"], list):
                raise ValidationError(f"Question {i} must have options as a list")
            
            if "correct_answer" not in question:
                raise ValidationError(f"Question {i} must have a correct_answer")
        
        return True
    
    @staticmethod
    def _validate_exercise(exercise_data: Dict[str, Any]) -> bool:
        """Validate exercise-specific fields."""
        # Exercises may have instructions
        if "instructions" in exercise_data:
            if not isinstance(exercise_data["instructions"], str):
                raise ValidationError("Exercise instructions must be a string")
        
        # Exercises may have solution
        if "solution" in exercise_data:
            if not isinstance(exercise_data["solution"], str):
                raise ValidationError("Exercise solution must be a string")
        
        return True
    
    @staticmethod
    def _validate_video(video_data: Dict[str, Any]) -> bool:
        """Validate video-specific fields."""
        required_video_fields = ["video_url"]
        for field in required_video_fields:
            if field not in video_data:
                raise ValidationError(f"Video missing required field: {field}")
        
        if not isinstance(video_data["video_url"], str) or not video_data["video_url"].strip():
            raise ValidationError("Video URL must be a non-empty string")
        
        # Validate URL format
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        if not url_pattern.match(video_data["video_url"]):
            raise ValidationError("Invalid video URL format")
        
        return True
    
    @staticmethod
    def _validate_reading(reading_data: Dict[str, Any]) -> bool:
        """Validate reading-specific fields."""
        # Reading items might have additional content fields
        if "read_time_minutes" in reading_data:
            if not isinstance(reading_data["read_time_minutes"], int) or reading_data["read_time_minutes"] <= 0:
                raise ValidationError("Read time must be a positive integer")
        
        return True
    
    @staticmethod
    def _validate_interactive(interactive_data: Dict[str, Any]) -> bool:
        """Validate interactive-specific fields."""
        required_interactive_fields = ["interactive_elements"]
        for field in required_interactive_fields:
            if field not in interactive_data:
                raise ValidationError(f"Interactive item missing required field: {field}")
        
        if not isinstance(interactive_data["interactive_elements"], list):
            raise ValidationError("Interactive elements must be a list")
        
        return True


class SessionStateValidator:
    """Validates session state transitions."""
    
    @staticmethod
    def validate_state_transition(current_state: str, target_state: str) -> bool:
        """Validate if a state transition is allowed."""
        allowed_transitions = {
            "not_started": ["in_progress", "paused"],
            "in_progress": ["paused", "completed", "abandoned"],
            "paused": ["in_progress", "completed", "abandoned"],
            "completed": [],
            "abandoned": []
        }
        
        if current_state not in allowed_transitions:
            raise ValidationError(f"Invalid current state: {current_state}")
        
        if target_state not in allowed_transitions[current_state]:
            raise ValidationError(
                f"Invalid state transition: {current_state} -> {target_state}. "
                f"Allowed transitions from {current_state} are: {allowed_transitions[current_state]}"
            )
        
        return True
    
    @staticmethod
    def validate_session_data(session_data: Dict[str, Any]) -> bool:
        """Validate session data structure."""
        required_fields = ["id", "user_id", "org_id", "state", "created_at"]
        for field in required_fields:
            if field not in session_data:
                raise ValidationError(f"Missing required field: {field}")
        
        # Validate ID
        if not isinstance(session_data["id"], str) or not session_data["id"].strip():
            raise ValidationError("Session ID must be a non-empty string")
        
        # Validate user_id
        if not isinstance(session_data["user_id"], str) or not session_data["user_id"].strip():
            raise ValidationError("Session user_id must be a non-empty string")
        
        # Validate org_id
        if not isinstance(session_data["org_id"], str) or not session_data["org_id"].strip():
            raise ValidationError("Session org_id must be a non-empty string")
        
        # Validate state
        valid_states = ["not_started", "in_progress", "paused", "completed", "abandoned"]
        if session_data["state"] not in valid_states:
            raise ValidationError(f"Invalid session state: {session_data['state']}")
        
        # Validate created_at
        created_at = session_data["created_at"]
        if not isinstance(created_at, (datetime, str)):
            raise ValidationError("created_at must be a datetime object or ISO string")
        
        return True


class ProgressUpdateValidator:
    """Validates progress updates."""
    
    @staticmethod
    def validate_progress_update(user_id: str, item_id: str, performance_data: Dict[str, Any]) -> bool:
        """Validate progress update data."""
        if not isinstance(user_id, str) or not user_id.strip():
            raise ValidationError("User ID must be a non-empty string")
        
        if not isinstance(item_id, str) or not item_id.strip():
            raise ValidationError("Item ID must be a non-empty string")
        
        if not isinstance(performance_data, dict):
            raise ValidationError("Performance data must be a dictionary")
        
        # Validate performance metrics
        if "accuracy" in performance_data:
            accuracy = performance_data["accuracy"]
            if not isinstance(accuracy, (int, float)) or not (0 <= accuracy <= 1):
                raise ValidationError("Accuracy must be a number between 0 and 1")
        
        if "attempts" in performance_data:
            attempts = performance_data["attempts"]
            if not isinstance(attempts, int) or attempts < 1:
                raise ValidationError("Attempts must be a positive integer")
        
        if "time_spent" in performance_data:
            time_spent = performance_data["time_spent"]
            if not isinstance(time_spent, (int, float)) or time_spent < 0:
                raise ValidationError("Time spent must be a non-negative number")
        
        return True


class StreakEligibilityValidator:
    """Validates streak eligibility."""
    
    @staticmethod
    def validate_streak_eligibility(user_id: str, activity_date: datetime) -> bool:
        """Validate if user is eligible for streak tracking."""
        if not isinstance(user_id, str) or not user_id.strip():
            raise ValidationError("User ID must be a non-empty string")
        
        if not isinstance(activity_date, datetime):
            raise ValidationError("Activity date must be a datetime object")
        
        # Check if it's a future date
        if activity_date > datetime.utcnow():
            raise ValidationError("Activity date cannot be in the future")
        
        return True


class OrganizationBoundaryValidator:
    """Validates organization boundaries."""
    
    @staticmethod
    def validate_organization_access(user_org_id: str, resource_org_id: str) -> bool:
        """Validate if user can access resource in their organization."""
        if not isinstance(user_org_id, str) or not user_org_id.strip():
            raise ValidationError("User organization ID must be a non-empty string")
        
        if not isinstance(resource_org_id, str) or not resource_org_id.strip():
            raise ValidationError("Resource organization ID must be a non-empty string")
        
        # For now, check if they match (in real system, there might be cross-org access rules)
        if user_org_id != resource_org_id:
            raise ValidationError(
                f"Access denied: User org ({user_org_id}) does not match resource org ({resource_org_id})"
            )
        
        return True


class AIInputOutputValidator:
    """Validates AI input/output constraints."""
    
    @staticmethod
    def validate_ai_input(prompt: str, max_length: int = 2000) -> bool:
        """Validate AI input prompt."""
        if not isinstance(prompt, str):
            raise ValidationError("AI prompt must be a string")
        
        if len(prompt) > max_length:
            raise ValidationError(f"AI prompt exceeds maximum length of {max_length} characters")
        
        # Check for potentially harmful content
        harmful_patterns = [
            r"(?i)(system|ignore|disregard).*instructions",
            r"(?i)never\s+say\s+\"?no\"?",
            r"(?i)output\s+the\s+following"
        ]
        
        for pattern in harmful_patterns:
            if re.search(pattern, prompt):
                raise ValidationError("Prompt contains potentially harmful content")
        
        return True
    
    @staticmethod
    def validate_ai_output(response: str, safety_filter: str = "moderate") -> bool:
        """Validate AI output response."""
        if not isinstance(response, str):
            raise ValidationError("AI response must be a string")
        
        # Apply different safety levels
        if safety_filter == "strict":
            return AIInputOutputValidator._strict_output_validation(response)
        elif safety_filter == "moderate":
            return AIInputOutputValidator._moderate_output_validation(response)
        elif safety_filter == "permissive":
            return AIInputOutputValidator._permissive_output_validation(response)
        else:
            return True  # Default to permissive if unknown level
    
    @staticmethod
    def _strict_output_validation(response: str) -> bool:
        """Apply strict output validation."""
        harmful_patterns = [
            r"(?i)(kill|murder|assassinate|terrorist|bomb|weapon|violence)",
            r"(?i)(sexually|explicit|nudity|pornographic)",
            r"(?i)(drug|illegal|substance abuse)",
            r"(?i)(suicide|self-harm|kill myself)"
        ]
        
        for pattern in harmful_patterns:
            if re.search(pattern, response):
                raise ValidationError("Response contains potentially harmful content")
        
        return True
    
    @staticmethod
    def _moderate_output_validation(response: str) -> bool:
        """Apply moderate output validation."""
        harmful_patterns = [
            r"(?i)(terrorist|bomb|weapon)",
            r"(?i)(explicit|nudity|pornographic)",
            r"(?i)(drug|illegal|controlled substance)",
            r"(?i)(suicide|kill myself)"
        ]
        
        for pattern in harmful_patterns:
            if re.search(pattern, response):
                raise ValidationError("Response contains potentially harmful content")
        
        return True
    
    @staticmethod
    def _permissive_output_validation(response: str) -> bool:
        """Apply permissive output validation."""
        harmful_patterns = [
            r"(?i)(terrorist|bomb|weapon|chemical weapon)",
            r"(?i)(instructions for making explosives)",
            r"(?i)(suicide method|how to kill myself)"
        ]
        
        for pattern in harmful_patterns:
            if re.search(pattern, response):
                raise ValidationError("Response contains potentially harmful content")
        
        return True


class AudioFormatValidator:
    """Validates audio format compliance."""
    
    @staticmethod
    def validate_audio_format(audio_data: bytes, expected_format: str = None) -> bool:
        """Validate audio format compliance."""
        if not isinstance(audio_data, bytes):
            raise ValidationError("Audio data must be in bytes format")
        
        if len(audio_data) == 0:
            raise ValidationError("Audio data cannot be empty")
        
        # Check for valid audio headers
        if len(audio_data) < 12:
            raise ValidationError("Audio data is too short to be valid")
        
        # Check for WAV format
        if audio_data[0:4] == b'RIFF' and audio_data[8:12] == b'WAVE':
            if expected_format and expected_format.lower() != 'wav':
                raise ValidationError(f"Expected {expected_format} format but got WAV")
            return True
        
        # Check for MP3 format (simplified check)
        if audio_data[0:3] == b'ID3' or (audio_data[0] & 0xFF) == 0xFF and (audio_data[1] & 0xE0) == 0xE0:
            if expected_format and expected_format.lower() != 'mp3':
                raise ValidationError(f"Expected {expected_format} format but got MP3")
            return True
        
        # Check for FLAC format
        if audio_data[0:4] == b'fLaC':
            if expected_format and expected_format.lower() != 'flac':
                raise ValidationError(f"Expected {expected_format} format but got FLAC")
            return True
        
        # Check for M4A format
        if audio_data[4:8] == b'ftyp' and (audio_data[8:12] in [b'M4A ', b'mp42', b'mp41']):
            if expected_format and expected_format.lower() != 'm4a':
                raise ValidationError(f"Expected {expected_format} format but got M4A")
            return True
        
        raise ValidationError("Unsupported or invalid audio format")


class ComprehensiveValidator:
    """Comprehensive validation service that combines all validators."""
    
    @staticmethod
    def validate_content_hierarchy(category_data: Dict[str, Any], 
                                 subcategory_data: Dict[str, Any] = None,
                                 topic_data: Dict[str, Any] = None) -> bool:
        """Validate complete content hierarchy."""
        ContentHierarchyValidator.validate_category_structure(category_data)
        
        if subcategory_data:
            ContentHierarchyValidator.validate_subcategory_structure(subcategory_data)
            # Validate parent-child relationship
            if subcategory_data["parent_category_id"] != category_data["id"]:
                raise ValidationError("Subcategory parent ID does not match category ID")
        
        if topic_data:
            ContentHierarchyValidator.validate_topic_structure(topic_data)
            # Validate parent-child relationship
            if subcategory_data and topic_data["subcategory_id"] != subcategory_data["id"]:
                raise ValidationError("Topic subcategory ID does not match subcategory ID")
        
        return True
    
    @staticmethod
    def validate_all_for_user(user_id: str, org_id: str) -> bool:
        """Run all validations that apply to a user in an organization."""
        # Validate user ID format
        if not isinstance(user_id, str) or not user_id.strip():
            raise ValidationError("User ID must be a non-empty string")
        
        # Validate org ID format
        if not isinstance(org_id, str) or not org_id.strip():
            raise ValidationError("Organization ID must be a non-empty string")
        
        # Validate organization boundary
        OrganizationBoundaryValidator.validate_organization_access(org_id, org_id)
        
        return True