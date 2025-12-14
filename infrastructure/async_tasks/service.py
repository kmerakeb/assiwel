"""
Async tasks service for the AI-driven learning platform.
Implements background task orchestration using Django 6 async capabilities.
"""

import asyncio
import uuid
from datetime import datetime
from typing import Any, Dict, Callable, Optional, List
from enum import Enum
from dataclasses import dataclass
import logging


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Task:
    """Represents an asynchronous task."""
    id: str
    name: str
    function: Callable
    args: tuple
    kwargs: dict
    priority: TaskPriority
    created_at: datetime
    scheduled_at: datetime = None
    started_at: datetime = None
    completed_at: datetime = None
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: str = None
    retries: int = 0
    max_retries: int = 3


class AsyncTaskService:
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.task_queue: List[Task] = []
        self.active_tasks: List[Task] = []
        self.max_concurrent_tasks = 10
        self.logger = logging.getLogger(__name__)
        
    async def create_task(self, name: str, func: Callable, *args, 
                         priority: TaskPriority = TaskPriority.MEDIUM,
                         max_retries: int = 3, **kwargs) -> str:
        """
        Create a new async task.
        """
        task_id = str(uuid.uuid4())
        task = Task(
            id=task_id,
            name=name,
            function=func,
            args=args,
            kwargs=kwargs,
            priority=priority,
            created_at=datetime.utcnow(),
            max_retries=max_retries
        )
        
        self.tasks[task_id] = task
        self._add_to_queue(task)
        
        # Trigger task processing
        asyncio.create_task(self._process_queue())
        
        return task_id
    
    def _add_to_queue(self, task: Task):
        """
        Add task to the priority queue.
        """
        self.task_queue.append(task)
        # Sort queue by priority (higher priority first)
        self.task_queue.sort(key=lambda t: t.priority.value, reverse=True)
    
    async def _process_queue(self):
        """
        Process tasks in the queue.
        """
        while self.task_queue and len(self.active_tasks) < self.max_concurrent_tasks:
            task = self.task_queue.pop(0)
            self.active_tasks.append(task)
            
            # Update task status
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.utcnow()
            
            # Run the task
            asyncio.create_task(self._execute_task(task))
    
    async def _execute_task(self, task: Task):
        """
        Execute a single task.
        """
        try:
            # Mark as running
            task.status = TaskStatus.RUNNING
            
            # Execute the task function
            if asyncio.iscoroutinefunction(task.function):
                result = await task.function(*task.args, **task.kwargs)
            else:
                result = task.function(*task.args, **task.kwargs)
            
            # Mark as completed
            task.result = result
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            
            self.logger.info(f"Task {task.id} ({task.name}) completed successfully")
            
        except Exception as e:
            task.error = str(e)
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.utcnow()
            
            # Check if we should retry
            if task.retries < task.max_retries:
                task.retries += 1
                task.status = TaskStatus.PENDING
                task.started_at = None
                task.completed_at = None
                task.error = None  # Reset error for retry
                self._add_to_queue(task)  # Add back to queue for retry
                self.logger.warning(f"Task {task.id} failed, retrying ({task.retries}/{task.max_retries}): {e}")
            else:
                self.logger.error(f"Task {task.id} failed after {task.max_retries} retries: {e}")
        
        finally:
            # Remove from active tasks
            if task in self.active_tasks:
                self.active_tasks.remove(task)
            
            # Process next tasks in queue
            await self._process_queue()
    
    async def schedule_task(self, name: str, func: Callable, delay_seconds: int, *args,
                           priority: TaskPriority = TaskPriority.MEDIUM,
                           max_retries: int = 3, **kwargs) -> str:
        """
        Schedule a task to run after a delay.
        """
        task_id = str(uuid.uuid4())
        scheduled_at = datetime.utcnow() + timedelta(seconds=delay_seconds)
        
        task = Task(
            id=task_id,
            name=name,
            function=func,
            args=args,
            kwargs=kwargs,
            priority=priority,
            created_at=datetime.utcnow(),
            scheduled_at=scheduled_at,
            max_retries=max_retries
        )
        
        self.tasks[task_id] = task
        # We'll check scheduled tasks in a separate process
        self._check_scheduled_tasks()
        
        return task_id
    
    def _check_scheduled_tasks(self):
        """
        Check for scheduled tasks that are ready to run.
        """
        now = datetime.utcnow()
        ready_tasks = [
            task for task in self.tasks.values()
            if task.scheduled_at and task.scheduled_at <= now and task.status == TaskStatus.PENDING
        ]
        
        for task in ready_tasks:
            task.scheduled_at = None  # Clear scheduled time
            self._add_to_queue(task)
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of a specific task.
        """
        if task_id not in self.tasks:
            return None
        
        task = self.tasks[task_id]
        return {
            "id": task.id,
            "name": task.name,
            "status": task.status.value,
            "priority": task.priority.value,
            "created_at": task.created_at,
            "started_at": task.started_at,
            "completed_at": task.completed_at,
            "result": task.result,
            "error": task.error,
            "retries": task.retries,
            "progress": self._get_task_progress(task)
        }
    
    def _get_task_progress(self, task: Task) -> float:
        """
        Get estimated progress of a task (placeholder implementation).
        """
        if task.status == TaskStatus.COMPLETED:
            return 1.0
        elif task.status == TaskStatus.PENDING:
            return 0.0
        else:
            # In a real implementation, this would track actual progress
            # For now, return a placeholder
            return 0.5
    
    async def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a pending or running task.
        """
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        
        if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
            return False  # Cannot cancel completed/failed/cancelled tasks
        
        task.status = TaskStatus.CANCELLED
        task.completed_at = datetime.utcnow()
        
        # Remove from queue if it's there
        if task in self.task_queue:
            self.task_queue.remove(task)
        
        # Remove from active tasks if it's running
        if task in self.active_tasks:
            self.active_tasks.remove(task)
        
        return True
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the task queue.
        """
        total_tasks = len(self.tasks)
        pending_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.PENDING])
        running_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.RUNNING])
        completed_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED])
        failed_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.FAILED])
        cancelled_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.CANCELLED])
        
        return {
            "total_tasks": total_tasks,
            "pending_tasks": pending_tasks,
            "running_tasks": running_tasks,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "cancelled_tasks": cancelled_tasks,
            "queue_size": len(self.task_queue),
            "active_tasks": len(self.active_tasks)
        }
    
    async def wait_for_task(self, task_id: str, timeout: int = 300) -> Optional[Any]:
        """
        Wait for a task to complete and return its result.
        """
        if task_id not in self.tasks:
            return None
        
        task = self.tasks[task_id]
        
        # If already completed, return result immediately
        if task.status == TaskStatus.COMPLETED:
            return task.result
        elif task.status in [TaskStatus.FAILED, TaskStatus.CANCELLED]:
            raise Exception(f"Task {task_id} ended with status: {task.status.value}")
        
        # Wait for the task to complete
        start_time = datetime.utcnow()
        while task.status not in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
            if (datetime.utcnow() - start_time).total_seconds() > timeout:
                raise TimeoutError(f"Task {task_id} timed out after {timeout} seconds")
            
            await asyncio.sleep(0.1)  # Check every 100ms
        
        if task.status == TaskStatus.FAILED:
            raise Exception(f"Task {task_id} failed: {task.error}")
        elif task.status == TaskStatus.CANCELLED:
            raise Exception(f"Task {task_id} was cancelled")
        
        return task.result


# Decorator for marking functions as async tasks
def async_task(priority: TaskPriority = TaskPriority.MEDIUM, max_retries: int = 3):
    """
    Decorator to mark functions as async tasks.
    """
    def decorator(func):
        func._is_async_task = True
        func._task_priority = priority
        func._task_max_retries = max_retries
        return func
    return decorator