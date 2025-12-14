"""
Progress Service for the AI-driven learning platform.
Handles mastery calculation, spaced repetition, and completion rules.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import math
from enum import Enum


class MasteryLevel(Enum):
    BEGINNER = 1
    DEVELOPING = 2
    PROFICIENT = 3
    ADVANCED = 4
    EXPERT = 5


class CompletionStatus(Enum):
    NOT_ATTEMPTED = "not_attempted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    MASTERED = "mastered"


class ProgressService:
    def __init__(self):
        # In a real implementation, this would connect to a database
        self.user_progress = {}
        self.completion_rules = {}
        
    def calculate_mastery_score(self, user_id: str, item_id: str, 
                              performance_data: Dict[str, Any]) -> float:
        """
        Calculate mastery score based on various performance factors.
        """
        # Weighted scoring system
        accuracy_weight = 0.4
        consistency_weight = 0.2
        retention_weight = 0.2
        time_efficiency_weight = 0.1
        attempts_weight = 0.1
        
        # Extract performance metrics
        accuracy = performance_data.get('accuracy', 0.0)  # 0.0 to 1.0
        consistency = performance_data.get('consistency', 0.0)  # 0.0 to 1.0
        retention = performance_data.get('retention', 0.0)  # 0.0 to 1.0
        time_efficiency = performance_data.get('time_efficiency', 0.0)  # 0.0 to 1.0
        attempts = performance_data.get('attempts', 1)
        
        # Normalize attempts (fewer is better, max 10 attempts considered)
        normalized_attempts = max(0.0, 1.0 - min(attempts - 1, 9) / 9.0)
        
        # Calculate weighted mastery score (0.0 to 1.0)
        mastery_score = (
            accuracy * accuracy_weight +
            consistency * consistency_weight +
            retention * retention_weight +
            time_efficiency * time_efficiency_weight +
            normalized_attempts * attempts_weight
        )
        
        return mastery_score
    
    def get_mastery_level(self, mastery_score: float) -> MasteryLevel:
        """
        Convert mastery score to mastery level.
        """
        if mastery_score >= 0.9:
            return MasteryLevel.EXPERT
        elif mastery_score >= 0.8:
            return MasteryLevel.ADVANCED
        elif mastery_score >= 0.7:
            return MasteryLevel.PROFICIENT
        elif mastery_score >= 0.5:
            return MasteryLevel.DEVELOPING
        else:
            return MasteryLevel.BEGINNER
    
    def schedule_review(self, user_id: str, item_id: str, 
                       current_mastery: MasteryLevel) -> datetime:
        """
        Determine next review date using spaced repetition algorithm.
        """
        # Spaced repetition intervals based on mastery level
        intervals = {
            MasteryLevel.BEGINNER: timedelta(hours=1),      # Review in 1 hour
            MasteryLevel.DEVELOPING: timedelta(hours=6),    # Review in 6 hours
            MasteryLevel.PROFICIENT: timedelta(days=1),     # Review in 1 day
            MasteryLevel.ADVANCED: timedelta(days=3),       # Review in 3 days
            MasteryLevel.EXPERT: timedelta(days=7)          # Review in 7 days
        }
        
        next_review_date = datetime.utcnow() + intervals[current_mastery]
        return next_review_date
    
    def update_progress(self, user_id: str, item_id: str, 
                       performance_data: Dict[str, Any],
                       org_id: str = None) -> Dict[str, Any]:
        """
        Update user progress for a specific learning item.
        """
        mastery_score = self.calculate_mastery_score(user_id, item_id, performance_data)
        mastery_level = self.get_mastery_level(mastery_score)
        next_review_date = self.schedule_review(user_id, item_id, mastery_level)
        
        # Initialize user data if not exists
        if user_id not in self.user_progress:
            self.user_progress[user_id] = {}
        
        # Update item progress
        self.user_progress[user_id][item_id] = {
            "last_attempt_date": datetime.utcnow(),
            "mastery_score": mastery_score,
            "mastery_level": mastery_level.value,
            "next_review_date": next_review_date,
            "performance_data": performance_data,
            "attempts_count": performance_data.get('attempts', 1),
            "status": CompletionStatus.MASTERED if mastery_score >= 0.7 else CompletionStatus.COMPLETED
        }
        
        return {
            "mastery_score": mastery_score,
            "mastery_level": mastery_level,
            "next_review_date": next_review_date,
            "status": self.user_progress[user_id][item_id]["status"]
        }
    
    def get_user_progress(self, user_id: str, org_id: str = None) -> Dict[str, Any]:
        """
        Get overall progress for a user across all items.
        """
        if user_id not in self.user_progress:
            return {
                "overall_completion": 0.0,
                "mastery_distribution": {},
                "total_items_tracked": 0,
                "average_mastery_score": 0.0,
                "items": {}
            }
        
        user_data = self.user_progress[user_id]
        total_items = len(user_data)
        
        if total_items == 0:
            return {
                "overall_completion": 0.0,
                "mastery_distribution": {},
                "total_items_tracked": 0,
                "average_mastery_score": 0.0,
                "items": {}
            }
        
        # Calculate statistics
        completed_items = sum(1 for item in user_data.values() 
                            if item["status"] in [CompletionStatus.COMPLETED, CompletionStatus.MASTERED])
        average_mastery = sum(item["mastery_score"] for item in user_data.values()) / total_items
        overall_completion = (completed_items / total_items) * 100
        
        # Count mastery levels
        mastery_counts = {level.name: 0 for level in MasteryLevel}
        for item in user_data.values():
            level_name = MasteryLevel(item["mastery_level"]).name
            mastery_counts[level_name] += 1
        
        return {
            "overall_completion": overall_completion,
            "mastery_distribution": mastery_counts,
            "total_items_tracked": total_items,
            "average_mastery_score": average_mastery,
            "items": user_data
        }
    
    def get_items_due_for_review(self, user_id: str) -> List[str]:
        """
        Get list of items that are due for review by the user.
        """
        if user_id not in self.user_progress:
            return []
        
        now = datetime.utcnow()
        due_items = []
        
        for item_id, progress in self.user_progress[user_id].items():
            next_review = progress.get("next_review_date")
            if next_review and next_review <= now:
                due_items.append(item_id)
        
        return due_items
    
    def check_completion_rules(self, user_id: str, item_id: str, 
                             completion_criteria: Dict[str, Any] = None) -> bool:
        """
        Check if user meets completion criteria for an item.
        """
        if not completion_criteria:
            # Default completion rule: just needs to attempt the item
            return True
        
        if user_id not in self.user_progress or item_id not in self.user_progress[user_id]:
            return False
        
        progress = self.user_progress[user_id][item_id]
        
        # Check minimum mastery score if specified
        min_mastery = completion_criteria.get("min_mastery_score")
        if min_mastery is not None and progress["mastery_score"] < min_mastery:
            return False
        
        # Check minimum attempts if specified
        min_attempts = completion_criteria.get("min_attempts")
        if min_attempts is not None and progress["attempts_count"] < min_attempts:
            return False
        
        # Check if passed assessment if required
        requires_assessment = completion_criteria.get("requires_assessment", False)
        if requires_assessment and not progress["performance_data"].get("passed_assessment", False):
            return False
        
        return True
    
    def get_recommendations_for_review(self, user_id: str, count: int = 5) -> List[str]:
        """
        Get personalized recommendations for review based on spaced repetition and mastery gaps.
        """
        if user_id not in self.user_progress:
            return []
        
        # Get items due for review first
        due_items = self.get_items_due_for_review(user_id)
        
        # If we don't have enough due items, add items with lower mastery scores
        if len(due_items) < count:
            user_items = self.user_progress[user_id]
            # Sort items by mastery score (ascending) - focus on weaker areas
            low_mastery_items = sorted(
                [(item_id, progress) for item_id, progress in user_items.items()],
                key=lambda x: x[1]["mastery_score"]
            )
            
            # Add items that aren't already in due_items
            for item_id, _ in low_mastery_items:
                if len(due_items) >= count:
                    break
                if item_id not in due_items:
                    due_items.append(item_id)
        
        return due_items[:count]