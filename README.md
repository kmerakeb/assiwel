# AI-Driven Learning Platform - Service Architecture

This enterprise-level AI-driven learning platform follows a service-oriented architecture with a strong foundation of domain services, validators, and middleware to ensure consistency across all modules.

## Architecture Overview

The platform is organized into the following main components:

### Core Domain Services
- **AuthService**: Handles authentication, token lifecycle, role and organization resolution
- **PermissionService**: Implements RBAC and object-level access control
- **LearningService**: Manages session orchestration, item sequencing, and state transitions
- **ProgressService**: Calculates mastery, implements spaced repetition, and enforces completion rules
- **GamificationService**: Handles XP, streaks, achievements, and engagement mechanics
- **RecommendationService**: Performs skill gap analysis and generates learning paths
- **AIService**: Provides Ollama abstraction, prompt execution, caching, and safety
- **SpeechService**: Handles ASR ingestion, pronunciation scoring, and TTS generation
- **NotificationService**: Manages channel routing, scheduling, and delivery

### Validation Layer
- Implements business rule enforcement for:
  - Content hierarchy integrity (category → subcategory → topic)
  - Learning item schema validation per item type
  - Session state transitions
  - Progress updates
  - Streak eligibility
  - Organization boundaries
  - AI input/output constraints
  - Audio format compliance

### Middleware Layer
- Organization and tenant resolution
- Request authentication and role injection
- Rate limiting
- Idempotency handling
- Request correlation IDs
- Locale and timezone detection
- AI usage metering
- Audit logging
- Global error normalization

### Infrastructure Services
- **Cache Service**: Performance optimization through caching
- **Async Task Service**: Background task orchestration (Django 6 async)
- **Observability Service**: Metrics, tracing, and logging
- **Feature Flags Service**: Controlled rollouts and experimentation

## Service Dependencies

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Controllers   │───▶│   Middleware     │───▶│  Domain Services│
└─────────────────┘    └──────────────────┘    └─────────────────┘
                             │
                             ▼
                       ┌─────────────┐
                       │  Validators │
                       └─────────────┘
                             │
                             ▼
                    ┌─────────────────────┐
                    │ Infrastructure Layer│
                    └─────────────────────┘
```

## Usage Example

```python
from workspace import platform

# Get any service
auth_service = platform.get_service('auth')
learning_service = platform.get_service('learning')
ai_service = platform.get_service('ai')

# Use the services
token = auth_service.generate_token(user_id="user123", roles=["learner"], org_id="org1")
session_id = learning_service.create_learning_session("user123", "org1", "path1", ["item1", "item2"])
ai_response = ai_service.generate_response("Explain quantum computing", model="mistral")
```

## Development Guidelines

1. **Service Layer**: All business logic should be encapsulated in services
2. **Validation**: Business rules are enforced at the validation layer, not in controllers
3. **Middleware**: Cross-cutting concerns are handled by middleware
4. **Infrastructure**: Shared infrastructure services are consumed by all apps
5. **Feature Flags**: Use feature flags for controlled rollouts and A/B testing

## Security & Compliance

- All requests are authenticated and authorized
- Organization boundaries are enforced
- Audit logging tracks all significant actions
- AI safety filters prevent harmful content
- Rate limiting prevents abuse
- Data is encrypted in transit and at rest

This architecture ensures predictable behavior, regulatory compliance, scalability, and developer velocity while maintaining enterprise-grade quality and long-term maintainability.