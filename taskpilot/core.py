"""
Core TaskPilot functionality
"""

import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from .models import Task, TaskStatus, Priority, PomodoroSession, DailyStats
from .database import Database
from .ai_engine import AIEngine
from .pomodoro import PomodoroTimer, PomodoroStats


class TaskPilot:
    """
    Main TaskPilot controller class
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize TaskPilot"""
        self.db = Database(db_path)
        self.ai = AIEngine()
        self.timer = PomodoroTimer()
        
        # Set up timer callbacks
        self.timer.on_complete = self._on_pomodoro_complete
    
    # Task Management
    def create_task(self, title: str, description: str = "", **kwargs) -> Task:
        """
        Create a new task with AI analysis
        
        Args:
            title: Task title
            description: Task description
            **kwargs: Additional task properties
            
        Returns:
            Created Task object
        """
        # AI analysis
        ai_result = self.ai.analyze_task(title, description)
        
        # Create task
        task = Task(
            id=self._generate_id(),
            title=title,
            description=description,
            priority=kwargs.get("priority", ai_result["priority"]),
            due_date=kwargs.get("due_date", ai_result["due_date"]),
            estimated_minutes=kwargs.get("estimated_minutes", ai_result["estimated_minutes"]),
            tags=kwargs.get("tags", ai_result["tags"]),
            ai_priority_score=ai_result["priority_score"],
        )
        
        # Save to database
        self.db.create_task(task)
        
        # Update daily stats
        stats = self.db.get_or_create_daily_stats(datetime.now())
        stats.tasks_created += 1
        self.db.update_daily_stats(stats)
        
        return task
    
    def create_task_from_natural_language(self, text: str) -> Task:
        """
        Create task from natural language input
        
        Args:
            text: Natural language task description
            
        Returns:
            Created Task object
        """
        parsed = self.ai.parse_natural_language(text)
        
        task = Task(
            id=self._generate_id(),
            title=parsed["title"],
            description=parsed.get("description", ""),
            priority=parsed["priority"],
            due_date=parsed["due_date"],
            estimated_minutes=parsed["estimated_minutes"],
            tags=parsed["tags"],
            ai_priority_score=self.ai._calculate_priority_score(
                parsed["priority"], parsed["due_date"], 
                parsed["estimated_minutes"], text
            ),
        )
        
        self.db.create_task(task)
        
        # Update daily stats
        stats = self.db.get_or_create_daily_stats(datetime.now())
        stats.tasks_created += 1
        self.db.update_daily_stats(stats)
        
        return task
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID"""
        return self.db.get_task(task_id)
    
    def list_tasks(self, status: Optional[str] = None) -> List[Task]:
        """
        List all tasks
        
        Args:
            status: Filter by status (pending, in_progress, completed, archived)
            
        Returns:
            List of Task objects
        """
        if status:
            task_status = TaskStatus(status)
            tasks = self.db.get_all_tasks(task_status)
        else:
            tasks = self.db.get_all_tasks()
        
        # Sort by AI priority
        return self.ai.sort_tasks_by_priority(tasks)
    
    def update_task(self, task_id: str, **kwargs) -> Optional[Task]:
        """
        Update task properties
        
        Args:
            task_id: Task ID
            **kwargs: Properties to update
            
        Returns:
            Updated Task or None if not found
        """
        task = self.db.get_task(task_id)
        if not task:
            return None
        
        # Update fields
        for key, value in kwargs.items():
            if hasattr(task, key):
                setattr(task, key, value)
        
        # Recalculate AI priority if relevant fields changed
        if any(k in kwargs for k in ["title", "description", "priority", "due_date"]):
            ai_result = self.ai.analyze_task(task.title, task.description)
            task.ai_priority_score = ai_result["priority_score"]
        
        return self.db.update_task(task)
    
    def complete_task(self, task_id: str) -> Optional[Task]:
        """
        Mark task as completed
        
        Args:
            task_id: Task ID
            
        Returns:
            Updated Task or None if not found
        """
        task = self.db.get_task(task_id)
        if not task:
            return None
        
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.now()
        
        # Update daily stats
        stats = self.db.get_or_create_daily_stats(datetime.now())
        stats.tasks_completed += 1
        self.db.update_daily_stats(stats)
        
        return self.db.update_task(task)
    
    def delete_task(self, task_id: str) -> bool:
        """Delete task by ID"""
        return self.db.delete_task(task_id)
    
    def search_tasks(self, query: str) -> List[Task]:
        """Search tasks by query"""
        return self.db.search_tasks(query)
    
    def get_overdue_tasks(self) -> List[Task]:
        """Get all overdue tasks"""
        return self.db.get_overdue_tasks()
    
    def suggest_next_task(self) -> Optional[Task]:
        """Get AI suggestion for next task"""
        tasks = self.db.get_all_tasks()
        return self.ai.suggest_next_task(tasks)
    
    # Pomodoro Management
    def start_pomodoro(self, task_id: str) -> PomodoroSession:
        """
        Start pomodoro session for a task
        
        Args:
            task_id: Task ID
            
        Returns:
            PomodoroSession object
        """
        # Update task status
        task = self.db.get_task(task_id)
        if task and task.status == TaskStatus.PENDING:
            task.status = TaskStatus.IN_PROGRESS
            self.db.update_task(task)
        
        # Start timer
        session = self.timer.start(task_id)
        
        return session
    
    def stop_pomodoro(self) -> Optional[PomodoroSession]:
        """Stop current pomodoro session"""
        session = self.timer.stop()
        
        if session:
            # Save to database
            self.db.create_pomodoro_session(session)
            
            # Update task actual minutes
            task = self.db.get_task(session.task_id)
            if task:
                task.actual_minutes += session.duration_minutes
                self.db.update_task(task)
            
            # Update daily stats
            if session.completed:
                stats = self.db.get_or_create_daily_stats(datetime.now())
                stats.pomodoro_sessions += 1
                stats.total_focus_minutes += session.duration_minutes
                self.db.update_daily_stats(stats)
        
        return session
    
    def pause_pomodoro(self):
        """Pause current pomodoro session"""
        self.timer.pause()
    
    def resume_pomodoro(self):
        """Resume paused pomodoro session"""
        self.timer.resume()
    
    def get_pomodoro_status(self) -> Dict[str, Any]:
        """Get current pomodoro status"""
        minutes, seconds = self.timer.get_remaining_time()
        return {
            "is_running": self.timer.is_running,
            "is_paused": self.timer.is_paused,
            "remaining_minutes": minutes,
            "remaining_seconds": seconds,
            "formatted_time": self.timer.get_current_formatted_time(),
            "progress_percentage": self.timer.get_progress_percentage(),
        }
    
    def get_task_pomodoro_sessions(self, task_id: str) -> List[PomodoroSession]:
        """Get all pomodoro sessions for a task"""
        return self.db.get_task_pomodoro_sessions(task_id)
    
    # Statistics
    def get_daily_summary(self) -> str:
        """Get AI-generated daily summary"""
        tasks = self.db.get_all_tasks()
        stats = self.db.get_or_create_daily_stats(datetime.now())
        
        return self.ai.generate_daily_summary(
            tasks, stats.tasks_completed, stats.pomodoro_sessions
        )
    
    def get_stats(self, days: int = 7) -> List[DailyStats]:
        """Get statistics for the last N days"""
        return self.db.get_stats_range(days)
    
    def get_productivity_score(self) -> float:
        """
        Calculate overall productivity score (0-100)
        Based on task completion rate and pomodoro consistency
        """
        # Get last 7 days stats
        stats = self.get_stats(7)
        
        if not stats:
            return 0.0
        
        total_tasks = sum(s.tasks_created for s in stats)
        total_completed = sum(s.tasks_completed for s in stats)
        total_pomodoro = sum(s.pomodoro_sessions for s in stats)
        
        if total_tasks == 0:
            return 0.0
        
        # Completion rate (max 60 points)
        completion_rate = (total_completed / total_tasks) * 60 if total_tasks > 0 else 0
        
        # Pomodoro consistency (max 40 points)
        # Assume 8 pomodoros per day is excellent
        expected_pomodoros = 7 * 8
        pomodoro_score = min((total_pomodoro / expected_pomodoros) * 40, 40)
        
        return min(completion_rate + pomodoro_score, 100)
    
    # Settings
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get setting value"""
        return self.db.get_setting(key, default)
    
    def set_setting(self, key: str, value: Any):
        """Set setting value"""
        self.db.set_setting(key, value)
    
    # Internal methods
    def _generate_id(self) -> str:
        """Generate unique task ID"""
        return f"task_{uuid.uuid4().hex[:8]}"
    
    def _on_pomodoro_complete(self):
        """Callback when pomodoro session completes"""
        pass  # Can be used for notifications