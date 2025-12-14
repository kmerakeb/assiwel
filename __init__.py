"""
Main initialization module for the AI-driven learning platform.
Sets up all services, middleware, and infrastructure components.
"""

from services.auth.service import AuthService
from services.permission.service import PermissionService
from services.learning.service import LearningService
from services.progress.service import ProgressService
from services.gamification.service import GamificationService
from services.recommendation.service import RecommendationService
from services.ai.service import AIService
from services.speech.service import SpeechService
from services.notification.service import NotificationService

from validation.validators import ComprehensiveValidator
from middleware.core import RequestProcessor
from infrastructure.cache.service import CacheService
from infrastructure.async_tasks.service import AsyncTaskService
from infrastructure.observability.service import ObservabilityService, observability_service
from infrastructure.feature_flags.service import FeatureFlagService, FeatureFlagStatus, feature_flag_service


class PlatformInitializer:
    """
    Initializes and configures all platform services.
    """
    
    def __init__(self):
        self.auth_service = None
        self.permission_service = None
        self.learning_service = None
        self.progress_service = None
        self.gamification_service = None
        self.recommendation_service = None
        self.ai_service = None
        self.speech_service = None
        self.notification_service = None
        
        self.validator = None
        self.middleware = None
        
        self.cache_service = None
        self.async_task_service = None
        self.observability_service = None
        self.feature_flag_service = None
    
    def initialize_services(self):
        """
        Initialize all core domain services.
        """
        # Initialize auth service
        self.auth_service = AuthService(
            secret_key="your-super-secret-key-change-in-production",
            algorithm="HS256"
        )
        
        # Initialize permission service
        self.permission_service = PermissionService()
        
        # Initialize learning service
        self.learning_service = LearningService()
        
        # Initialize progress service
        self.progress_service = ProgressService()
        
        # Initialize gamification service
        self.gamification_service = GamificationService()
        
        # Initialize recommendation service
        self.recommendation_service = RecommendationService()
        
        # Initialize AI service
        self.ai_service = AIService(
            ollama_url="http://localhost:11434",
            default_model="mistral"
        )
        
        # Initialize speech service
        self.speech_service = SpeechService()
        
        # Initialize notification service
        self.notification_service = NotificationService()
        
        print("✓ Core domain services initialized")
    
    def initialize_validation_layer(self):
        """
        Initialize the validation layer.
        """
        self.validator = ComprehensiveValidator()
        print("✓ Validation layer initialized")
    
    def initialize_middleware(self):
        """
        Initialize middleware components.
        """
        self.middleware = RequestProcessor(
            auth_service=self.auth_service,
            permission_service=self.permission_service
        )
        print("✓ Middleware components initialized")
    
    def initialize_infrastructure_services(self):
        """
        Initialize infrastructure services.
        """
        # Initialize cache service
        self.cache_service = CacheService()
        
        # Initialize async task service
        self.async_task_service = AsyncTaskService()
        
        # Use the global observability service instance
        self.observability_service = observability_service
        
        # Use the global feature flag service instance
        self.feature_flag_service = feature_flag_service
        
        print("✓ Infrastructure services initialized")
    
    def setup_feature_flags(self):
        """
        Setup initial feature flags for the platform.
        """
        # Create feature flags for different platform features
        flags_to_create = [
            {
                "name": "ai_tutor_enabled",
                "description": "Enable AI tutor functionality for learners"
            },
            {
                "name": "speech_recognition_enabled", 
                "description": "Enable speech recognition for language learning"
            },
            {
                "name": "advanced_analytics_enabled",
                "description": "Enable advanced analytics dashboard for admins"
            },
            {
                "name": "gamification_enabled",
                "description": "Enable gamification features like XP and achievements"
            },
            {
                "name": "personalized_recommendations_enabled",
                "description": "Enable personalized learning path recommendations"
            }
        ]
        
        for flag_config in flags_to_create:
            try:
                self.feature_flag_service.create_flag(
                    name=flag_config["name"],
                    description=flag_config["description"],
                    initial_status=FeatureFlagStatus.ENABLED  # Enable by default
                )
            except ValueError:
                # Flag already exists
                continue
        
        print("✓ Feature flags setup completed")
    
    def setup_default_validators(self):
        """
        Setup default validation configurations.
        """
        # The validators are already defined in the validation module
        # This method can be used to set up any additional validation configurations
        print("✓ Default validators setup completed")
    
    def initialize_platform(self):
        """
        Main initialization method that sets up the entire platform.
        """
        print("🚀 Initializing AI-driven Learning Platform...")
        
        # Initialize services
        self.initialize_services()
        
        # Initialize validation layer
        self.initialize_validation_layer()
        
        # Initialize middleware
        self.initialize_middleware()
        
        # Initialize infrastructure services
        self.initialize_infrastructure_services()
        
        # Setup feature flags
        self.setup_feature_flags()
        
        # Setup default validators
        self.setup_default_validators()
        
        print("\n✅ Platform initialization completed successfully!")
        print("\n📋 Services Summary:")
        print(f"   • Core Domain Services: 9")
        print(f"   • Validation Layer: 1")
        print(f"   • Middleware Components: 1")
        print(f"   • Infrastructure Services: 4")
        print(f"   • Feature Flags: {len(self.feature_flag_service.flags)}")
        
        return self
    
    def get_service(self, service_name: str):
        """
        Get a specific service by name.
        """
        services = {
            'auth': self.auth_service,
            'permission': self.permission_service,
            'learning': self.learning_service,
            'progress': self.progress_service,
            'gamification': self.gamification_service,
            'recommendation': self.recommendation_service,
            'ai': self.ai_service,
            'speech': self.speech_service,
            'notification': self.notification_service,
            'validator': self.validator,
            'middleware': self.middleware,
            'cache': self.cache_service,
            'async_task': self.async_task_service,
            'observability': self.observability_service,
            'feature_flag': self.feature_flag_service
        }
        
        return services.get(service_name)


# Initialize the platform when this module is imported
platform = PlatformInitializer().initialize_platform()