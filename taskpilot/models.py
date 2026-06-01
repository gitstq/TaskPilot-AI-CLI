"""
Data models for TaskPilot-CLI
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Optional, List, Dict, Any
import json


class TaskStatus(Enum):
    """Task status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class Priority(Enum):
    """Task priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4


@dataclass
class Task:
    """Task data model"""
    id: str
    title: str
    description: str = ""
    status: TaskStatus = TaskStatus.PENDING
    priority: Priority = Priority.MEDIUM
    created_at: datetime = field(default_factory=datetime.now)
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)
    estimated_minutes: int = 25  # Default pomodoro length
    actual_minutes: int = 0
    ai_priority_score: float = 0.0  # AI-calculated priority (0-100)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "priority": self.priority.value,
            "created_at": self.created_at.isoformat(),
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "tags": self.tags,
            "estimated_minutes": self.estimated_minutes,
            "actual_minutes": self.actual_minutes,
            "ai_priority_score": self.ai_priority_score,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """Create task from dictionary"""
        return cls(
            id=data["id"],
            title=data["title"],
            description=data.get("description", ""),
            status=TaskStatus(data["status"]),
            priority=Priority(data["priority"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            due_date=datetime.fromisoformat(data["due_date"]) if data.get("due_date") else None,
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            tags=data.get("tags", []),
            estimated_minutes=data.get("estimated_minutes", 25),
            actual_minutes=data.get("actual_minutes", 0),
            ai_priority_score=data.get("ai_priority_score", 0.0),
        )
    
    def is_overdue(self) -> bool:
        """Check if task is overdue"""
        if self.due_date and self.status != TaskStatus.COMPLETED:
            return datetime.now() > self.due_date
        return False
    
    def get_priority_emoji(self) -> str:
        """Get emoji for priority level"""
        emoji_map = {
            Priority.URGENT: "🔴",
            Priority.HIGH: "🟠",
            Priority.MEDIUM: "🟡",
            Priority.LOW: "🟢",
        }
        return emoji_map.get(self.priority, "⚪")
    
    def get_status_emoji(self) -> str:
        """Get emoji for status"""
        emoji_map = {
            TaskStatus.PENDING: "⏳",
            TaskStatus.IN_PROGRESS: "🔄",
            TaskStatus.COMPLETED: "✅",
            TaskStatus.ARCHIVED: "📦",
        }
        return emoji_map.get(self.status, "⚪")


@dataclass
class PomodoroSession:
    """Pomodoro session data model"""
    id: str
    task_id: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    duration_minutes: int = 25
    completed: bool = False
    interruptions: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "task_id": self.task_id,
            "started_at": self.started_at.isoformat(),
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "duration_minutes": self.duration_minutes,
            "completed": self.completed,
            "interruptions": self.interruptions,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PomodoroSession":
        return cls(
            id=data["id"],
            task_id=data["task_id"],
            started_at=datetime.fromisoformat(data["started_at"]),
            ended_at=datetime.fromisoformat(data["ended_at"]) if data.get("ended_at") else None,
            duration_minutes=data.get("duration_minutes", 25),
            completed=data.get("completed", False),
            interruptions=data.get("interruptions", 0),
        )


@dataclass
class DailyStats:
    """Daily productivity statistics"""
    date: datetime
    tasks_completed: int = 0
    tasks_created: int = 0
    pomodoro_sessions: int = 0
    total_focus_minutes: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "date": self.date.strftime("%Y-%m-%d"),
            "tasks_completed": self.tasks_completed,
            "tasks_created": self.tasks_created,
            "pomodoro_sessions": self.pomodoro_sessions,
            "total_focus_minutes": self.total_focus_minutes,
        }