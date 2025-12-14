"""
Gamification Service for the AI-driven learning platform.
Handles XP, streaks, achievements, and other engagement mechanics.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
import uuid


class AchievementType(Enum):
    COMPLETION = "completion"
    MASTERY = "mastery"
    STREAK = "streak"
    PARTICIPATION = "participation"
    PERFECT_SCORE = "perfect_score"
    FIRST_STEP = "first_step"


class AchievementCategory(Enum):
    LEARNING = "learning"
    SOCIAL = "social"
    MILESTONE = "milestone"
    CHALLENGE = "challenge"


class GamificationService:
    def __init__(self):
        # In a real implementation, this would connect to a database
        self.user_xp = {}
        self.user_streaks = {}
        self.user_achievements = {}
        self.achievement_definitions = {}
        self.initialize_default_achievements()
    
    def initialize_default_achievements(self):
        """
        Initialize default achievement definitions.
        """
        self.achievement_definitions = {
            "first_lesson_completed": {
                "type": AchievementType.COMPLETION,
                "category": AchievementCategory.MILESTONE,
                "name": "First Steps",
                "description": "Complete your first lesson",
                "xp_reward": 50,
                "criteria": {"lessons_completed": 1}
            },
            "first_quiz_passed": {
                "type": AchievementType.PERFECT_SCORE,
                "category": AchievementCategory.MILESTONE,
                "name": "Perfect Start",
                "description": "Pass your first quiz with 100% accuracy",
                "xp_reward": 100,
                "criteria": {"quizzes_passed_with_100_percent": 1}
            },
            "week_streak": {
                "type": AchievementType.STREAK,
                "category": AchievementCategory.CHALLENGE,
                "name": "Week Warrior",
                "description": "Maintain a 7-day learning streak",
                "xp_reward": 200,
                "criteria": {"consecutive_days_learning": 7}
            },
            "ten_lessons_completed": {
                "type": AchievementType.COMPLETION,
                "category": AchievementCategory.MILESTONE,
                "name": "Learner",
                "description": "Complete 10 lessons",
                "xp_reward": 150,
                "criteria": {"lessons_completed": 10}
            },
            "master_level": {
                "type": AchievementType.MASTERY,
                "category": AchievementCategory.LEARNING,
                "name": "Master",
                "description": "Achieve expert mastery level on any item",
                "xp_reward": 300,
                "criteria": {"expert_mastery_count": 1}
            }
        }
    
    def award_xp(self, user_id: str, xp_amount: int, activity_type: str = "general") -> Dict[str, Any]:
        """
        Award XP to a user for an activity.
        """
        if user_id not in self.user_xp:
            self.user_xp[user_id] = {
                "total_xp": 0,
                "level": 1,
                "xp_to_next_level": 100,
                "activity_log": []
            }
        
        # Update XP
        self.user_xp[user_id]["total_xp"] += xp_amount
        
        # Log the activity
        self.user_xp[user_id]["activity_log"].append({
            "timestamp": datetime.utcnow(),
            "activity_type": activity_type,
            "xp_awarded": xp_amount,
            "total_xp_after": self.user_xp[user_id]["total_xp"]
        })
        
        # Check for level up
        old_level = self.user_xp[user_id]["level"]
        new_level, xp_to_next_level = self._calculate_level_from_xp(self.user_xp[user_id]["total_xp"])
        self.user_xp[user_id]["level"] = new_level
        self.user_xp[user_id]["xp_to_next_level"] = xp_to_next_level
        
        level_up = new_level > old_level
        
        return {
            "total_xp": self.user_xp[user_id]["total_xp"],
            "current_level": self.user_xp[user_id]["level"],
            "xp_to_next_level": self.user_xp[user_id]["xp_to_next_level"],
            "level_up": level_up,
            "new_level_reached": new_level if level_up else None
        }
    
    def _calculate_level_from_xp(self, total_xp: int) -> tuple:
        """
        Calculate user level based on total XP using exponential progression.
        """
        # Simple exponential formula: XP needed for next level increases by 100 each level
        level = 1
        xp_needed = 100  # XP needed for level 2
        
        while total_xp >= xp_needed:
            level += 1
            total_xp -= xp_needed
            xp_needed = 100 * level  # Increase XP needed for next level
        
        xp_to_next_level = xp_needed - total_xp
        return level, xp_to_next_level
    
    def update_streak(self, user_id: str, activity_date: datetime = None) -> Dict[str, Any]:
        """
        Update user's learning streak.
        """
        if activity_date is None:
            activity_date = datetime.utcnow()
        
        if user_id not in self.user_streaks:
            self.user_streaks[user_id] = {
                "current_streak": 0,
                "longest_streak": 0,
                "last_activity_date": None,
                "streak_breaks": 0
            }
        
        streak_info = self.user_streaks[user_id]
        today = activity_date.date()
        
        # If this is the first activity
        if streak_info["last_activity_date"] is None:
            streak_info["current_streak"] = 1
            streak_info["last_activity_date"] = today
            streak_info["longest_streak"] = max(streak_info["longest_streak"], 1)
        else:
            last_activity = streak_info["last_activity_date"]
            
            # Calculate difference in days
            days_diff = (today - last_activity).days
            
            if days_diff == 0:
                # Same day activity, no change to streak
                pass
            elif days_diff == 1:
                # Consecutive day, increment streak
                streak_info["current_streak"] += 1
                streak_info["longest_streak"] = max(streak_info["longest_streak"], streak_info["current_streak"])
            elif days_diff > 1:
                # Streak was broken
                streak_info["streak_breaks"] += 1
                streak_info["current_streak"] = 1  # Reset to 1
            
            streak_info["last_activity_date"] = today
        
        return {
            "current_streak": streak_info["current_streak"],
            "longest_streak": streak_info["longest_streak"],
            "streak_breaks": streak_info["streak_breaks"],
            "last_activity_date": streak_info["last_activity_date"]
        }
    
    def check_and_unlock_achievements(self, user_id: str, event_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Check if user has unlocked any achievements based on event data.
        """
        if user_id not in self.user_achievements:
            self.user_achievements[user_id] = []
        
        unlocked_achievements = []
        
        # Check each achievement definition
        for achievement_id, definition in self.achievement_definitions.items():
            # Skip if already earned
            if any(a["id"] == achievement_id for a in self.user_achievements[user_id]):
                continue
            
            # Check if criteria are met
            if self._check_achievement_criteria(definition["criteria"], event_data):
                # Unlock the achievement
                achievement = {
                    "id": achievement_id,
                    "type": definition["type"],
                    "category": definition["category"],
                    "name": definition["name"],
                    "description": definition["description"],
                    "xp_reward": definition["xp_reward"],
                    "unlocked_at": datetime.utcnow()
                }
                
                self.user_achievements[user_id].append(achievement)
                unlocked_achievements.append(achievement)
                
                # Award XP for achievement
                self.award_xp(user_id, definition["xp_reward"], f"achievement_{achievement_id}")
        
        return unlocked_achievements
    
    def _check_achievement_criteria(self, criteria: Dict[str, Any], event_data: Dict[str, Any]) -> bool:
        """
        Check if event data meets achievement criteria.
        """
        for criterion, required_value in criteria.items():
            if criterion in event_data:
                if isinstance(required_value, dict):
                    # Complex condition (like ranges)
                    if "min" in required_value and "max" in required_value:
                        if not (required_value["min"] <= event_data[criterion] <= required_value["max"]):
                            return False
                    elif "min" in required_value:
                        if event_data[criterion] < required_value["min"]:
                            return False
                    elif "max" in required_value:
                        if event_data[criterion] > required_value["max"]:
                            return False
                else:
                    # Simple equality check
                    if event_data[criterion] < required_value:  # Using less than to handle cumulative values
                        return False
            else:
                # Criterion not in event data, consider it unmet
                return False
        
        return True
    
    def get_user_gamification_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Get comprehensive gamification stats for a user.
        """
        xp_info = self.user_xp.get(user_id, {
            "total_xp": 0,
            "level": 1,
            "xp_to_next_level": 100
        })
        
        streak_info = self.user_streaks.get(user_id, {
            "current_streak": 0,
            "longest_streak": 0,
            "streak_breaks": 0
        })
        
        achievements = self.user_achievements.get(user_id, [])
        
        return {
            "xp_info": xp_info,
            "streak_info": streak_info,
            "achievements": achievements,
            "achievement_count": len(achievements),
            "total_rewards_xp": sum(a["xp_reward"] for a in achievements)
        }
    
    def award_bonus_xp(self, user_id: str, base_xp: int, bonus_multiplier: float = 1.0) -> int:
        """
        Award XP with potential bonuses (for streaks, perfect scores, etc.).
        """
        # Apply streak bonus (extra 10% for every 7 days of streak)
        streak_bonus = 0
        if user_id in self.user_streaks:
            current_streak = self.user_streaks[user_id]["current_streak"]
            streak_bonus = (current_streak // 7) * 0.1  # 10% bonus for every week streak
        
        total_multiplier = bonus_multiplier + streak_bonus
        total_xp = int(base_xp * total_multiplier)
        
        return self.award_xp(user_id, total_xp, "bonus_activity")["total_xp"]