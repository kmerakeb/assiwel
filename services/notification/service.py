"""
Notification Service for the AI-driven learning platform.
Handles channel routing, scheduling, and delivery of notifications.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json


class NotificationType(Enum):
    PROGRESS_UPDATE = "progress_update"
    DEADLINE_REMINDER = "deadline_reminder"
    ACHIEVEMENT_UNLOCKED = "achievement_unlocked"
    CONTENT_UPDATE = "content_update"
    SYSTEM_MESSAGE = "system_message"
    PEER_ACTIVITY = "peer_activity"


class NotificationChannel(Enum):
    EMAIL = "email"
    PUSH = "push"
    SMS = "sms"
    IN_APP = "in_app"


class NotificationPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4


class NotificationStatus(Enum):
    PENDING = "pending"
    SCHEDULED = "scheduled"
    SENT = "sent"
    FAILED = "failed"
    DELIVERED = "delivered"


class NotificationService:
    def __init__(self, email_config: Dict[str, Any] = None):
        self.email_config = email_config or {}
        self.notifications_queue = []
        self.delivery_status = {}
        self.user_preferences = {}
        self.channel_config = {}
        
    def send_notification(self, user_id: str, notification_type: NotificationType,
                         message: str, title: str = None, 
                         channels: List[NotificationChannel] = None,
                         priority: NotificationPriority = NotificationPriority.MEDIUM,
                         scheduled_time: datetime = None,
                         custom_data: Dict[str, Any] = None) -> str:
        """
        Send a notification to a user through specified channels.
        """
        if channels is None:
            channels = self._get_user_preferred_channels(user_id, notification_type)
        
        notification_id = self._generate_notification_id()
        
        notification = {
            "id": notification_id,
            "user_id": user_id,
            "type": notification_type,
            "title": title or self._generate_default_title(notification_type),
            "message": message,
            "channels": channels,
            "priority": priority,
            "status": NotificationStatus.PENDING if scheduled_time is None else NotificationStatus.SCHEDULED,
            "scheduled_time": scheduled_time,
            "created_at": datetime.utcnow(),
            "custom_data": custom_data or {},
            "delivery_attempts": 0,
            "delivery_status": {}
        }
        
        # Initialize delivery status for each channel
        for channel in channels:
            notification["delivery_status"][channel.value] = {
                "status": NotificationStatus.PENDING,
                "attempts": 0,
                "last_attempt": None,
                "delivered_at": None
            }
        
        # If scheduled, add to scheduled queue, otherwise process immediately
        if scheduled_time and scheduled_time > datetime.utcnow():
            self.notifications_queue.append(notification)
        else:
            self._process_notification(notification)
        
        return notification_id
    
    def _generate_notification_id(self) -> str:
        """
        Generate a unique notification ID.
        """
        import uuid
        return str(uuid.uuid4())
    
    def _generate_default_title(self, notification_type: NotificationType) -> str:
        """
        Generate a default title based on notification type.
        """
        titles = {
            NotificationType.PROGRESS_UPDATE: "Progress Update",
            NotificationType.DEADLINE_REMINDER: "Deadline Reminder",
            NotificationType.ACHIEVEMENT_UNLOCKED: "Achievement Unlocked!",
            NotificationType.CONTENT_UPDATE: "Content Update",
            NotificationType.SYSTEM_MESSAGE: "System Message",
            NotificationType.PEER_ACTIVITY: "Peer Activity"
        }
        return titles.get(notification_type, "Notification")
    
    def _get_user_preferred_channels(self, user_id: str, 
                                   notification_type: NotificationType) -> List[NotificationChannel]:
        """
        Get user's preferred notification channels for a specific notification type.
        """
        if user_id not in self.user_preferences:
            # Default preferences
            return [NotificationChannel.IN_APP, NotificationChannel.EMAIL]
        
        user_prefs = self.user_preferences[user_id]
        if notification_type.value in user_prefs:
            return [NotificationChannel(ch) for ch in user_prefs[notification_type.value]]
        else:
            # Use default channels for this user
            return [NotificationChannel(ch) for ch in user_prefs.get("default", 
                          [NotificationChannel.IN_APP.value, NotificationChannel.EMAIL.value])]
    
    def _process_notification(self, notification: Dict[str, Any]) -> bool:
        """
        Process a notification for delivery through all specified channels.
        """
        success = True
        user_id = notification["user_id"]
        
        for channel in notification["channels"]:
            if channel == NotificationChannel.EMAIL:
                result = self._send_email_notification(user_id, notification)
            elif channel == NotificationChannel.PUSH:
                result = self._send_push_notification(user_id, notification)
            elif channel == NotificationChannel.SMS:
                result = self._send_sms_notification(user_id, notification)
            elif channel == NotificationChannel.IN_APP:
                result = self._send_in_app_notification(user_id, notification)
            else:
                result = False
            
            # Update delivery status
            notification["delivery_status"][channel.value]["status"] = (
                NotificationStatus.SENT if result else NotificationStatus.FAILED
            )
            notification["delivery_status"][channel.value]["attempts"] += 1
            notification["delivery_status"][channel.value]["last_attempt"] = datetime.utcnow()
            
            if result:
                notification["delivery_status"][channel.value]["delivered_at"] = datetime.utcnow()
            else:
                success = False
        
        # Update overall notification status
        notification["status"] = NotificationStatus.SENT if success else NotificationStatus.FAILED
        
        return success
    
    def _send_email_notification(self, user_id: str, notification: Dict[str, Any]) -> bool:
        """
        Send email notification to user.
        """
        try:
            # In a real implementation, this would connect to an email service
            # For this implementation, we'll simulate the process
            
            # Get user's email (in real system, fetch from user profile)
            user_email = f"{user_id}@example.com"
            
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = self.email_config.get('from_email', 'noreply@learning-platform.com')
            msg['To'] = user_email
            msg['Subject'] = notification["title"]
            
            body = notification["message"]
            msg.attach(MIMEText(body, 'plain'))
            
            # In real implementation, send the email
            # server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            # server.starttls()
            # server.login(self.email_config['username'], self.email_config['password'])
            # server.send_message(msg)
            # server.quit()
            
            # For simulation, assume success
            return True
            
        except Exception as e:
            print(f"Email sending failed: {str(e)}")
            return False
    
    def _send_push_notification(self, user_id: str, notification: Dict[str, Any]) -> bool:
        """
        Send push notification to user's device.
        """
        try:
            # In a real implementation, this would connect to a push notification service
            # like Firebase Cloud Messaging (FCM) or Apple Push Notification Service (APNs)
            
            # For simulation, assume success
            return True
            
        except Exception as e:
            print(f"Push notification failed: {str(e)}")
            return False
    
    def _send_sms_notification(self, user_id: str, notification: Dict[str, Any]) -> bool:
        """
        Send SMS notification to user.
        """
        try:
            # In a real implementation, this would connect to an SMS service
            # like Twilio or AWS SNS
            
            # For simulation, assume success
            return True
            
        except Exception as e:
            print(f"SMS sending failed: {str(e)}")
            return False
    
    def _send_in_app_notification(self, user_id: str, notification: Dict[str, Any]) -> bool:
        """
        Send in-app notification to user.
        """
        try:
            # In a real implementation, this would store the notification
            # in a database for the user to see in their in-app notification center
            
            # For simulation, assume success
            return True
            
        except Exception as e:
            print(f"In-app notification failed: {str(e)}")
            return False
    
    def schedule_notification(self, user_id: str, notification_type: NotificationType,
                            message: str, schedule_time: datetime, title: str = None,
                            channels: List[NotificationChannel] = None) -> str:
        """
        Schedule a notification to be sent at a later time.
        """
        return self.send_notification(
            user_id=user_id,
            notification_type=notification_type,
            message=message,
            title=title,
            channels=channels,
            scheduled_time=schedule_time
        )
    
    def process_scheduled_notifications(self) -> int:
        """
        Process any scheduled notifications that are ready to be sent.
        """
        now = datetime.utcnow()
        processed_count = 0
        
        # Find notifications that are scheduled and ready to send
        ready_notifications = [
            n for n in self.notifications_queue 
            if n["status"] == NotificationStatus.SCHEDULED and n["scheduled_time"] <= now
        ]
        
        for notification in ready_notifications:
            self._process_notification(notification)
            notification["status"] = NotificationStatus.SENT
            processed_count += 1
        
        # Remove processed notifications from queue
        self.notifications_queue = [
            n for n in self.notifications_queue 
            if n["status"] != NotificationStatus.SENT
        ]
        
        return processed_count
    
    def get_user_notifications(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get recent notifications for a user (for in-app display).
        """
        # In a real implementation, this would query a database
        # For simulation, return empty list
        return []
    
    def set_user_notification_preferences(self, user_id: str, 
                                        preferences: Dict[str, List[str]]) -> bool:
        """
        Set user's notification preferences for different types and channels.
        """
        self.user_preferences[user_id] = preferences
        return True
    
    def get_notification_status(self, notification_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the delivery status of a specific notification.
        """
        for notification in self.notifications_queue:
            if notification["id"] == notification_id:
                return {
                    "id": notification["id"],
                    "status": notification["status"],
                    "delivery_status": notification["delivery_status"],
                    "created_at": notification["created_at"]
                }
        
        # In a real implementation, also check sent notifications
        # For simulation, return None if not found in queue
        return None
    
    def register_channel_config(self, channel: NotificationChannel, config: Dict[str, Any]) -> bool:
        """
        Register configuration for a notification channel.
        """
        self.channel_config[channel.value] = config
        return True
    
    def bulk_send_notifications(self, notifications: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Send multiple notifications efficiently.
        """
        results = {"success": 0, "failed": 0}
        
        for notification in notifications:
            try:
                user_id = notification["user_id"]
                notification_type = notification["type"]
                message = notification["message"]
                title = notification.get("title")
                channels = notification.get("channels")
                priority = notification.get("priority", NotificationPriority.MEDIUM)
                scheduled_time = notification.get("scheduled_time")
                custom_data = notification.get("custom_data", {})
                
                notification_id = self.send_notification(
                    user_id, notification_type, message, title, channels, 
                    priority, scheduled_time, custom_data
                )
                
                if notification_id:
                    results["success"] += 1
                else:
                    results["failed"] += 1
            except Exception as e:
                print(f"Bulk notification failed: {str(e)}")
                results["failed"] += 1
        
        return results