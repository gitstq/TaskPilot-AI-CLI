"""
Unit tests for Database
"""

import unittest
import os
import tempfile
from datetime import datetime, timedelta
from taskpilot.database import Database
from taskpilot.models import Task, TaskStatus, Priority, PomodoroSession


class TestDatabase(unittest.TestCase):
    """Test Database operations"""
    
    def setUp(self):
        """Set up test database"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.db = Database(self.db_path)
    
    def tearDown(self):
        """Clean up test database"""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        os.rmdir(self.temp_dir)
    
    def test_create_and_get_task(self):
        """Test task creation and retrieval"""
        task = Task(
            id="task_001",
            title="Test Task",
            description="A test task",
            status=TaskStatus.PENDING,
            priority=Priority.HIGH,
        )
        
        created = self.db.create_task(task)
        self.assertEqual(created.id, "task_001")
        
        retrieved = self.db.get_task("task_001")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.title, "Test Task")
    
    def test_get_all_tasks(self):
        """Test listing all tasks"""
        # Create tasks
        for i in range(3):
            task = Task(
                id=f"task_{i}",
                title=f"Task {i}",
                status=TaskStatus.PENDING,
                priority=Priority.MEDIUM,
            )
            self.db.create_task(task)
        
        tasks = self.db.get_all_tasks()
        self.assertEqual(len(tasks), 3)
    
    def test_update_task(self):
        """Test task update"""
        task = Task(
            id="task_001",
            title="Original",
            status=TaskStatus.PENDING,
            priority=Priority.MEDIUM,
        )
        self.db.create_task(task)
        
        task.title = "Updated"
        task.priority = Priority.HIGH
        self.db.update_task(task)
        
        retrieved = self.db.get_task("task_001")
        self.assertEqual(retrieved.title, "Updated")
        self.assertEqual(retrieved.priority, Priority.HIGH)
    
    def test_delete_task(self):
        """Test task deletion"""
        task = Task(
            id="task_001",
            title="To Delete",
            status=TaskStatus.PENDING,
            priority=Priority.MEDIUM,
        )
        self.db.create_task(task)
        
        result = self.db.delete_task("task_001")
        self.assertTrue(result)
        
        retrieved = self.db.get_task("task_001")
        self.assertIsNone(retrieved)
    
    def test_search_tasks(self):
        """Test task search"""
        task1 = Task(
            id="task_001",
            title="Buy milk",
            description="Get from store",
            status=TaskStatus.PENDING,
            priority=Priority.MEDIUM,
        )
        task2 = Task(
            id="task_002",
            title="Finish report",
            description="Work project",
            status=TaskStatus.PENDING,
            priority=Priority.MEDIUM,
        )
        
        self.db.create_task(task1)
        self.db.create_task(task2)
        
        results = self.db.search_tasks("milk")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "Buy milk")
    
    def test_get_overdue_tasks(self):
        """Test overdue task retrieval"""
        # Create overdue task
        overdue = Task(
            id="task_overdue",
            title="Overdue Task",
            due_date=datetime.now() - timedelta(days=1),
            status=TaskStatus.PENDING,
            priority=Priority.MEDIUM,
        )
        
        # Create future task
        future = Task(
            id="task_future",
            title="Future Task",
            due_date=datetime.now() + timedelta(days=1),
            status=TaskStatus.PENDING,
            priority=Priority.MEDIUM,
        )
        
        self.db.create_task(overdue)
        self.db.create_task(future)
        
        overdue_tasks = self.db.get_overdue_tasks()
        self.assertEqual(len(overdue_tasks), 1)
        self.assertEqual(overdue_tasks[0].title, "Overdue Task")


if __name__ == "__main__":
    unittest.main()