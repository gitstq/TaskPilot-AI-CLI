"""
Unit tests for TaskPilot models
"""

import unittest
from datetime import datetime, timedelta
from taskpilot.models import Task, TaskStatus, Priority, PomodoroSession, DailyStats


class TestTask(unittest.TestCase):
    """Test Task model"""
    
    def test_task_creation(self):
        """Test basic task creation"""
        task = Task(
            id="task_001",
            title="Test Task",
            description="A test task",
            status=TaskStatus.PENDING,
            priority=Priority.HIGH,
        )
        
        self.assertEqual(task.id, "task_001")
        self.assertEqual(task.title, "Test Task")
        self.assertEqual(task.status, TaskStatus.PENDING)
        self.assertEqual(task.priority, Priority.HIGH)
    
    def test_task_to_dict(self):
        """Test task serialization"""
        task = Task(
            id="task_001",
            title="Test Task",
            status=TaskStatus.PENDING,
            priority=Priority.MEDIUM,
        )
        
        data = task.to_dict()
        
        self.assertEqual(data["id"], "task_001")
        self.assertEqual(data["title"], "Test Task")
        self.assertEqual(data["status"], "pending")
        self.assertEqual(data["priority"], 2)
    
    def test_task_from_dict(self):
        """Test task deserialization"""
        data = {
            "id": "task_001",
            "title": "Test Task",
            "description": "",
            "status": "pending",
            "priority": 3,
            "created_at": datetime.now().isoformat(),
            "due_date": None,
            "completed_at": None,
            "tags": [],
            "estimated_minutes": 25,
            "actual_minutes": 0,
            "ai_priority_score": 0.0,
        }
        
        task = Task.from_dict(data)
        
        self.assertEqual(task.id, "task_001")
        self.assertEqual(task.priority, Priority.HIGH)
    
    def test_is_overdue(self):
        """Test overdue detection"""
        # Overdue task
        overdue_task = Task(
            id="task_001",
            title="Overdue",
            due_date=datetime.now() - timedelta(days=1),
            status=TaskStatus.PENDING,
        )
        self.assertTrue(overdue_task.is_overdue())
        
        # Future task
        future_task = Task(
            id="task_002",
            title="Future",
            due_date=datetime.now() + timedelta(days=1),
            status=TaskStatus.PENDING,
        )
        self.assertFalse(future_task.is_overdue())
        
        # Completed task (not overdue even if past due date)
        completed_task = Task(
            id="task_003",
            title="Completed",
            due_date=datetime.now() - timedelta(days=1),
            status=TaskStatus.COMPLETED,
        )
        self.assertFalse(completed_task.is_overdue())
    
    def test_priority_emoji(self):
        """Test priority emoji mapping"""
        urgent = Task(id="1", title="Urgent", priority=Priority.URGENT)
        high = Task(id="2", title="High", priority=Priority.HIGH)
        medium = Task(id="3", title="Medium", priority=Priority.MEDIUM)
        low = Task(id="4", title="Low", priority=Priority.LOW)
        
        self.assertEqual(urgent.get_priority_emoji(), "🔴")
        self.assertEqual(high.get_priority_emoji(), "🟠")
        self.assertEqual(medium.get_priority_emoji(), "🟡")
        self.assertEqual(low.get_priority_emoji(), "🟢")


class TestPomodoroSession(unittest.TestCase):
    """Test PomodoroSession model"""
    
    def test_session_creation(self):
        """Test session creation"""
        session = PomodoroSession(
            id="pom_001",
            task_id="task_001",
            started_at=datetime.now(),
            duration_minutes=25,
        )
        
        self.assertEqual(session.task_id, "task_001")
        self.assertEqual(session.duration_minutes, 25)
        self.assertFalse(session.completed)


if __name__ == "__main__":
    unittest.main()