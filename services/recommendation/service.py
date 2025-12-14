"""
Recommendation Service for the AI-driven learning platform.
Handles skill gap analysis and learning path generation.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
import uuid


class SkillLevel(Enum):
    NOVICE = 1
    BEGINNER = 2
    INTERMEDIATE = 3
    ADVANCED = 4
    EXPERT = 5


class RecommendationType(Enum):
    SKILL_GAP = "skill_gap"
    REVIEW = "review"
    NEXT_STEPS = "next_steps"
    CHALLENGE = "challenge"
    REINFORCEMENT = "reinforcement"


class RecommendationPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class RecommendationService:
    def __init__(self):
        # In a real implementation, this would connect to a database
        self.user_skills = {}
        self.skill_mappings = {}
        self.learning_paths = {}
        self.recommendation_history = {}
        
    def analyze_skill_gaps(self, user_id: str, target_skills: List[str], 
                          current_skills: Dict[str, SkillLevel] = None) -> List[Dict[str, Any]]:
        """
        Analyze skill gaps between current skills and target skills.
        """
        if current_skills is None:
            current_skills = self.get_user_current_skills(user_id)
        
        gaps = []
        for target_skill in target_skills:
            if target_skill not in current_skills or current_skills[target_skill].value < SkillLevel.INTERMEDIATE.value:
                # Determine the gap level
                current_level = current_skills.get(target_skill, SkillLevel.NOVICE)
                gap_severity = self._calculate_gap_severity(current_level, SkillLevel.INTERMEDIATE)
                
                gaps.append({
                    "skill": target_skill,
                    "current_level": current_level,
                    "target_level": SkillLevel.INTERMEDIATE,
                    "gap_severity": gap_severity,
                    "recommended_items": self._find_learning_items_for_skill(target_skill, current_level),
                    "priority": self._determine_priority(gap_severity, target_skill in target_skills)
                })
        
        # Sort by priority
        gaps.sort(key=lambda x: x["priority"].value, reverse=True)
        return gaps
    
    def _calculate_gap_severity(self, current_level: SkillLevel, target_level: SkillLevel) -> float:
        """
        Calculate numerical severity of the skill gap.
        """
        return (target_level.value - current_level.value) / target_level.value
    
    def _determine_priority(self, gap_severity: float, is_target_skill: bool) -> RecommendationPriority:
        """
        Determine recommendation priority based on gap severity and importance.
        """
        if gap_severity >= 0.8 or (is_target_skill and gap_severity >= 0.5):
            return RecommendationPriority.CRITICAL
        elif gap_severity >= 0.5 or (is_target_skill and gap_severity >= 0.3):
            return RecommendationPriority.HIGH
        elif gap_severity >= 0.3:
            return RecommendationPriority.MEDIUM
        else:
            return RecommendationPriority.LOW
    
    def _find_learning_items_for_skill(self, skill: str, current_level: SkillLevel) -> List[str]:
        """
        Find appropriate learning items for a skill based on current level.
        """
        # This would normally query a database of skill-to-item mappings
        # For demonstration, we'll return some mock items
        base_items = [f"{skill}_intro", f"{skill}_basics", f"{skill}_intermediate"]
        
        if current_level.value < SkillLevel.INTERMEDIATE.value:
            return base_items
        else:
            return [f"{skill}_advanced", f"{skill}_mastery"]
    
    def generate_personalized_learning_path(self, user_id: str, 
                                          target_skills: List[str],
                                          time_constraint_days: int = 30) -> Dict[str, Any]:
        """
        Generate a personalized learning path based on skill gaps and user profile.
        """
        skill_gaps = self.analyze_skill_gaps(user_id, target_skills)
        
        # Create learning path
        path_id = str(uuid.uuid4())
        learning_items = []
        
        for gap in skill_gaps:
            learning_items.extend(gap["recommended_items"])
        
        # Add reinforcement items for skills that are already somewhat developed
        current_skills = self.get_user_current_skills(user_id)
        reinforcement_items = []
        for skill, level in current_skills.items():
            if SkillLevel.INTERMEDIATE.value <= level.value < SkillLevel.EXPERT.value:
                reinforcement_items.extend(self._find_reinforcement_items(skill))
        
        # Combine all items
        all_items = learning_items + reinforcement_items
        
        # Create path with estimated timeline
        path_duration = min(len(all_items) * 2, time_constraint_days)  # 2 days per item estimate
        
        learning_path = {
            "id": path_id,
            "user_id": user_id,
            "target_skills": target_skills,
            "items": all_items,
            "estimated_duration_days": path_duration,
            "generated_at": datetime.utcnow(),
            "skill_gaps_addressed": [gap["skill"] for gap in skill_gaps],
            "reinforcement_skills": [skill for skill in current_skills.keys() 
                                   if SkillLevel.INTERMEDIATE.value <= current_skills[skill].value < SkillLevel.EXPERT.value]
        }
        
        self.learning_paths[path_id] = learning_path
        return learning_path
    
    def _find_reinforcement_items(self, skill: str) -> List[str]:
        """
        Find reinforcement items for skills that are developing.
        """
        # Mock implementation - in reality, this would fetch reinforcement items
        return [f"{skill}_review", f"{skill}_practice"]
    
    def get_adaptive_recommendations(self, user_id: str, 
                                   context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Get adaptive recommendations based on user progress, preferences, and context.
        """
        recommendations = []
        
        # Get user's current skill profile
        current_skills = self.get_user_current_skills(user_id)
        
        # Identify weak areas (skills with low mastery)
        weak_skills = [
            skill for skill, level in current_skills.items()
            if level.value < SkillLevel.INTERMEDIATE.value
        ]
        
        # Add recommendations for weak skills
        for skill in weak_skills:
            recommendations.append({
                "type": RecommendationType.SKILL_GAP,
                "skill": skill,
                "item_id": f"{skill}_remedial",
                "reason": f"Skill '{skill}' needs improvement",
                "priority": RecommendationPriority.HIGH,
                "confidence": 0.9
            })
        
        # Add review recommendations based on spaced repetition
        from services.progress.service import ProgressService
        # In a real system, we'd have access to the progress service instance
        # For now, we'll simulate getting items due for review
        items_due_for_review = self._get_items_due_for_review(user_id)
        for item_id in items_due_for_review:
            recommendations.append({
                "type": RecommendationType.REVIEW,
                "skill": self._get_skill_for_item(item_id),
                "item_id": item_id,
                "reason": "Scheduled review based on spaced repetition",
                "priority": RecommendationPriority.MEDIUM,
                "confidence": 0.85
            })
        
        # Add next-step recommendations based on completed items
        next_steps = self._suggest_next_steps(user_id)
        for step in next_steps:
            recommendations.append({
                "type": RecommendationType.NEXT_STEPS,
                "skill": step["skill"],
                "item_id": step["item_id"],
                "reason": "Logical next step after recent completions",
                "priority": RecommendationPriority.MEDIUM,
                "confidence": 0.8
            })
        
        # Sort by priority and confidence
        recommendations.sort(key=lambda x: (x["priority"].value, x["confidence"]), reverse=True)
        return recommendations
    
    def _get_items_due_for_review(self, user_id: str) -> List[str]:
        """
        Simulate getting items due for review (in real system, connect to ProgressService).
        """
        # Mock implementation
        return [f"item_{i}" for i in range(3)]
    
    def _get_skill_for_item(self, item_id: str) -> str:
        """
        Get the skill associated with a learning item.
        """
        # Mock implementation
        return item_id.split("_")[0]
    
    def _suggest_next_steps(self, user_id: str) -> List[Dict[str, str]]:
        """
        Suggest logical next steps based on user's progress.
        """
        # Mock implementation
        return [
            {"skill": "python_basics", "item_id": "python_functions"},
            {"skill": "web_dev", "item_id": "html_css_advanced"}
        ]
    
    def update_user_skills(self, user_id: str, skill_updates: Dict[str, SkillLevel]) -> bool:
        """
        Update user's skill levels based on assessment or completion data.
        """
        if user_id not in self.user_skills:
            self.user_skills[user_id] = {}
        
        for skill, level in skill_updates.items():
            # Only update if the new level is higher than existing (avoid downgrades)
            if skill not in self.user_skills[user_id] or self.user_skills[user_id][skill].value < level.value:
                self.user_skills[user_id][skill] = level
        
        return True
    
    def get_user_current_skills(self, user_id: str) -> Dict[str, SkillLevel]:
        """
        Get current skill levels for a user.
        """
        return self.user_skills.get(user_id, {})
    
    def record_recommendation_interaction(self, user_id: str, recommendation_id: str, 
                                        interaction_type: str, timestamp: datetime = None) -> bool:
        """
        Record how a user interacted with a recommendation.
        """
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        interaction_record = {
            "user_id": user_id,
            "recommendation_id": recommendation_id,
            "interaction_type": interaction_type,  # accepted, rejected, completed, ignored
            "timestamp": timestamp
        }
        
        if user_id not in self.recommendation_history:
            self.recommendation_history[user_id] = []
        
        self.recommendation_history[user_id].append(interaction_record)
        return True
    
    def get_recommendation_effectiveness(self, user_id: str) -> Dict[str, float]:
        """
        Calculate effectiveness metrics for recommendations to this user.
        """
        if user_id not in self.recommendation_history:
            return {"acceptance_rate": 0.0, "completion_rate": 0.0, "engagement_score": 0.0}
        
        interactions = self.recommendation_history[user_id]
        if not interactions:
            return {"acceptance_rate": 0.0, "completion_rate": 0.0, "engagement_score": 0.0}
        
        total = len(interactions)
        accepted = sum(1 for i in interactions if i["interaction_type"] in ["accepted", "completed"])
        completed = sum(1 for i in interactions if i["interaction_type"] == "completed")
        
        acceptance_rate = accepted / total if total > 0 else 0.0
        completion_rate = completed / accepted if accepted > 0 else 0.0
        engagement_score = (accepted * 0.6 + completed * 0.4) / total if total > 0 else 0.0
        
        return {
            "acceptance_rate": acceptance_rate,
            "completion_rate": completion_rate,
            "engagement_score": engagement_score
        }