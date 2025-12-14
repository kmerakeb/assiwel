"""
Learning Service for the AI-driven learning platform.
Handles session orchestration, item sequencing, and state transitions.
"""

from typing import List, Dict, Any, Optional
from enum import Enum
import uuid
from datetime import datetime


class LearningItemType(Enum):
    LESSON = "lesson"
    QUIZ = "quiz"
    EXERCISE = "exercise"
    VIDEO = "video"
    READING = "reading"
    INTERACTIVE = "interactive"


class SessionState(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class LearningService:
    def __init__(self):
        # In a real implementation, this would connect to a database
        self.sessions = {}
        self.learning_items = {}
        self.item_sequences = {}
    
    def create_learning_session(self, user_id: str, org_id: str, 
                              learning_path_id: str, 
                              initial_items: List[str]) -> str:
        """
        Create a new learning session with initial items.
        """
        session_id = str(uuid.uuid4())
        
        session_data = {
            "id": session_id,
            "user_id": user_id,
            "org_id": org_id,
            "learning_path_id": learning_path_id,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "state": SessionState.NOT_STARTED,
            "current_item_index": 0,
            "total_items": len(initial_items),
            "items_order": initial_items,
            "completed_items": [],
            "current_item_id": initial_items[0] if initial_items else None
        }
        
        self.sessions[session_id] = session_data
        return session_id
    
    def get_next_item(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the next learning item in the session sequence.
        """
        if session_id not in self.sessions:
            return None
            
        session = self.sessions[session_id]
        current_index = session["current_item_index"]
        items_order = session["items_order"]
        
        if current_index >= len(items_order):
            return None  # No more items
            
        next_item_id = items_order[current_index]
        return {
            "item_id": next_item_id,
            "index": current_index,
            "total": len(items_order),
            "completed_count": len(session["completed_items"])
        }
    
    def advance_session(self, session_id: str, current_item_id: str) -> bool:
        """
        Advance the session to the next item after completing the current one.
        """
        if session_id not in self.sessions:
            return False
            
        session = self.sessions[session_id]
        
        # Mark current item as completed
        if current_item_id not in session["completed_items"]:
            session["completed_items"].append(current_item_id)
        
        # Move to next item
        session["current_item_index"] += 1
        session["updated_at"] = datetime.utcnow()
        
        # Update current item ID
        items_order = session["items_order"]
        if session["current_item_index"] < len(items_order):
            session["current_item_id"] = items_order[session["current_item_index"]]
        else:
            # Session completed
            session["state"] = SessionState.COMPLETED
            session["current_item_id"] = None
        
        return True
    
    def pause_session(self, session_id: str) -> bool:
        """
        Pause the current learning session.
        """
        if session_id not in self.sessions:
            return False
            
        self.sessions[session_id]["state"] = SessionState.PAUSED
        self.sessions[session_id]["updated_at"] = datetime.utcnow()
        return True
    
    def resume_session(self, session_id: str) -> bool:
        """
        Resume a paused learning session.
        """
        if session_id not in self.sessions:
            return False
            
        session = self.sessions[session_id]
        if session["state"] == SessionState.PAUSED:
            session["state"] = SessionState.IN_PROGRESS
            session["updated_at"] = datetime.utcnow()
            return True
        return False
    
    def update_session_state(self, session_id: str, new_state: SessionState) -> bool:
        """
        Update the session state to a new value.
        """
        if session_id not in self.sessions:
            return False
            
        self.sessions[session_id]["state"] = new_state
        self.sessions[session_id]["updated_at"] = datetime.utcnow()
        return True
    
    def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the current status of a learning session.
        """
        if session_id not in self.sessions:
            return None
            
        session = self.sessions[session_id]
        return {
            "id": session["id"],
            "state": session["state"],
            "current_item_id": session["current_item_id"],
            "current_item_index": session["current_item_index"],
            "total_items": session["total_items"],
            "completed_items_count": len(session["completed_items"]),
            "completion_percentage": (
                len(session["completed_items"]) / session["total_items"] * 100
                if session["total_items"] > 0 else 0
            ),
            "created_at": session["created_at"],
            "updated_at": session["updated_at"]
        }
    
    def register_learning_item(self, item_id: str, item_type: LearningItemType, 
                             title: str, content: str, prerequisites: List[str] = None,
                             duration_estimate: int = 0) -> bool:
        """
        Register a new learning item in the system.
        """
        self.learning_items[item_id] = {
            "id": item_id,
            "type": item_type,
            "title": title,
            "content": content,
            "prerequisites": prerequisites or [],
            "duration_estimate": duration_estimate,
            "created_at": datetime.utcnow()
        }
        return True
    
    def create_item_sequence(self, sequence_id: str, item_ids: List[str], 
                           prerequisites_check: bool = True) -> bool:
        """
        Create a sequence of learning items with optional prerequisite checking.
        """
        if prerequisites_check:
            # Verify that prerequisites are satisfied in the sequence
            all_items = {item["id"]: item for item_id, item in self.learning_items.items()}
            for i, item_id in enumerate(item_ids):
                if item_id not in all_items:
                    raise ValueError(f"Item {item_id} does not exist")
                    
                item = all_items[item_id]
                for prereq_id in item.get("prerequisites", []):
                    # Prerequisite must appear before this item in the sequence
                    if prereq_id in item_ids and item_ids.index(prereq_id) >= i:
                        raise ValueError(f"Prerequisite {prereq_id} must come before {item_id}")
        
        self.item_sequences[sequence_id] = {
            "id": sequence_id,
            "item_ids": item_ids,
            "created_at": datetime.utcnow()
        }
        return True