"""
SQLite database management for TaskPilot-CLI
Zero external dependencies - uses only Python standard library
"""

import sqlite3
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

from .models import Task, TaskStatus, Priority, PomodoroSession, DailyStats


class Database:
    """SQLite database manager"""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize database connection"""
        if db_path is None:
            # Store in user's home directory
            home = Path.home()
            config_dir = home / ".taskpilot"
            config_dir.mkdir(exist_ok=True)
            db_path = config_dir / "taskpilot.db"
        
        self.db_path = str(db_path)
        self._init_database()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_database(self):
        """Initialize database tables"""
        with self._get_connection() as conn:
            # Tasks table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    status TEXT DEFAULT 'pending',
                    priority INTEGER DEFAULT 2,
                    created_at TEXT NOT NULL,
                    due_date TEXT,
                    completed_at TEXT,
                    tags TEXT DEFAULT '[]',
                    estimated_minutes INTEGER DEFAULT 25,
                    actual_minutes INTEGER DEFAULT 0,
                    ai_priority_score REAL DEFAULT 0.0
                )
            """)
            
            # Pomodoro sessions table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pomodoro_sessions (
                    id TEXT PRIMARY KEY,
                    task_id TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    ended_at TEXT,
                    duration_minutes INTEGER DEFAULT 25,
                    completed BOOLEAN DEFAULT 0,
                    interruptions INTEGER DEFAULT 0,
                    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
                )
            """)
            
            # Daily stats table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS daily_stats (
                    date TEXT PRIMARY KEY,
                    tasks_completed INTEGER DEFAULT 0,
                    tasks_created INTEGER DEFAULT 0,
                    pomodoro_sessions INTEGER DEFAULT 0,
                    total_focus_minutes INTEGER DEFAULT 0
                )
            """)
            
            # Settings table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)
            
            conn.commit()
    
    # Task operations
    def create_task(self, task: Task) -> Task:
        """Create a new task"""
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO tasks 
                (id, title, description, status, priority, created_at, due_date, 
                 completed_at, tags, estimated_minutes, actual_minutes, ai_priority_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                task.id, task.title, task.description, task.status.value,
                task.priority.value, task.created_at.isoformat(),
                task.due_date.isoformat() if task.due_date else None,
                task.completed_at.isoformat() if task.completed_at else None,
                json.dumps(task.tags), task.estimated_minutes,
                task.actual_minutes, task.ai_priority_score
            ))
            conn.commit()
        return task
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID"""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM tasks WHERE id = ?", (task_id,)
            ).fetchone()
            
            if row:
                return self._row_to_task(row)
            return None
    
    def get_all_tasks(self, status: Optional[TaskStatus] = None) -> List[Task]:
        """Get all tasks, optionally filtered by status"""
        with self._get_connection() as conn:
            if status:
                rows = conn.execute(
                    "SELECT * FROM tasks WHERE status = ? ORDER BY ai_priority_score DESC, priority DESC, created_at DESC",
                    (status.value,)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM tasks WHERE status != 'archived' ORDER BY ai_priority_score DESC, priority DESC, created_at DESC"
                ).fetchall()
            
            return [self._row_to_task(row) for row in rows]
    
    def update_task(self, task: Task) -> Task:
        """Update existing task"""
        with self._get_connection() as conn:
            conn.execute("""
                UPDATE tasks SET
                    title = ?, description = ?, status = ?, priority = ?,
                    due_date = ?, completed_at = ?, tags = ?,
                    estimated_minutes = ?, actual_minutes = ?, ai_priority_score = ?
                WHERE id = ?
            """, (
                task.title, task.description, task.status.value, task.priority.value,
                task.due_date.isoformat() if task.due_date else None,
                task.completed_at.isoformat() if task.completed_at else None,
                json.dumps(task.tags), task.estimated_minutes,
                task.actual_minutes, task.ai_priority_score, task.id
            ))
            conn.commit()
        return task
    
    def delete_task(self, task_id: str) -> bool:
        """Delete task by ID"""
        with self._get_connection() as conn:
            cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def search_tasks(self, query: str) -> List[Task]:
        """Search tasks by title or description"""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM tasks 
                WHERE (title LIKE ? OR description LIKE ?) AND status != 'archived'
                ORDER BY ai_priority_score DESC, priority DESC
            """, (f"%{query}%", f"%{query}%")).fetchall()
            return [self._row_to_task(row) for row in rows]
    
    def get_tasks_by_tag(self, tag: str) -> List[Task]:
        """Get tasks by tag"""
        all_tasks = self.get_all_tasks()
        return [t for t in all_tasks if tag.lower() in [tg.lower() for tg in t.tags]]
    
    def get_overdue_tasks(self) -> List[Task]:
        """Get all overdue tasks"""
        now = datetime.now().isoformat()
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM tasks 
                WHERE due_date < ? AND status != 'completed' AND status != 'archived'
                ORDER BY due_date ASC
            """, (now,)).fetchall()
            return [self._row_to_task(row) for row in rows]
    
    def _row_to_task(self, row: sqlite3.Row) -> Task:
        """Convert database row to Task object"""
        return Task(
            id=row["id"],
            title=row["title"],
            description=row["description"],
            status=TaskStatus(row["status"]),
            priority=Priority(row["priority"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            due_date=datetime.fromisoformat(row["due_date"]) if row["due_date"] else None,
            completed_at=datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None,
            tags=json.loads(row["tags"]),
            estimated_minutes=row["estimated_minutes"],
            actual_minutes=row["actual_minutes"],
            ai_priority_score=row["ai_priority_score"],
        )
    
    # Pomodoro operations
    def create_pomodoro_session(self, session: PomodoroSession) -> PomodoroSession:
        """Create a new pomodoro session"""
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO pomodoro_sessions 
                (id, task_id, started_at, ended_at, duration_minutes, completed, interruptions)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                session.id, session.task_id, session.started_at.isoformat(),
                session.ended_at.isoformat() if session.ended_at else None,
                session.duration_minutes, session.completed, session.interruptions
            ))
            conn.commit()
        return session
    
    def update_pomodoro_session(self, session: PomodoroSession) -> PomodoroSession:
        """Update pomodoro session"""
        with self._get_connection() as conn:
            conn.execute("""
                UPDATE pomodoro_sessions SET
                    ended_at = ?, completed = ?, interruptions = ?
                WHERE id = ?
            """, (
                session.ended_at.isoformat() if session.ended_at else None,
                session.completed, session.interruptions, session.id
            ))
            conn.commit()
        return session
    
    def get_task_pomodoro_sessions(self, task_id: str) -> List[PomodoroSession]:
        """Get all pomodoro sessions for a task"""
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM pomodoro_sessions WHERE task_id = ? ORDER BY started_at DESC",
                (task_id,)
            ).fetchall()
            return [self._row_to_session(row) for row in rows]
    
    def _row_to_session(self, row: sqlite3.Row) -> PomodoroSession:
        """Convert database row to PomodoroSession"""
        return PomodoroSession(
            id=row["id"],
            task_id=row["task_id"],
            started_at=datetime.fromisoformat(row["started_at"]),
            ended_at=datetime.fromisoformat(row["ended_at"]) if row["ended_at"] else None,
            duration_minutes=row["duration_minutes"],
            completed=bool(row["completed"]),
            interruptions=row["interruptions"],
        )
    
    # Stats operations
    def get_or_create_daily_stats(self, date: datetime) -> DailyStats:
        """Get or create daily stats for a date"""
        date_str = date.strftime("%Y-%m-%d")
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM daily_stats WHERE date = ?", (date_str,)
            ).fetchone()
            
            if row:
                return DailyStats(
                    date=datetime.strptime(row["date"], "%Y-%m-%d"),
                    tasks_completed=row["tasks_completed"],
                    tasks_created=row["tasks_created"],
                    pomodoro_sessions=row["pomodoro_sessions"],
                    total_focus_minutes=row["total_focus_minutes"],
                )
            else:
                # Create new stats entry
                conn.execute("""
                    INSERT INTO daily_stats (date, tasks_completed, tasks_created, pomodoro_sessions, total_focus_minutes)
                    VALUES (?, 0, 0, 0, 0)
                """, (date_str,))
                conn.commit()
                return DailyStats(date=date)
    
    def update_daily_stats(self, stats: DailyStats) -> DailyStats:
        """Update daily stats"""
        date_str = stats.date.strftime("%Y-%m-%d")
        with self._get_connection() as conn:
            conn.execute("""
                UPDATE daily_stats SET
                    tasks_completed = ?, tasks_created = ?, pomodoro_sessions = ?, total_focus_minutes = ?
                WHERE date = ?
            """, (
                stats.tasks_completed, stats.tasks_created,
                stats.pomodoro_sessions, stats.total_focus_minutes, date_str
            ))
            conn.commit()
        return stats
    
    def get_stats_range(self, days: int = 7) -> List[DailyStats]:
        """Get stats for the last N days"""
        from datetime import timedelta
        
        stats = []
        for i in range(days - 1, -1, -1):
            date = datetime.now() - timedelta(days=i)
            stats.append(self.get_or_create_daily_stats(date))
        return stats
    
    # Settings operations
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get setting value"""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT value FROM settings WHERE key = ?", (key,)
            ).fetchone()
            return json.loads(row["value"]) if row else default
    
    def set_setting(self, key: str, value: Any):
        """Set setting value"""
        with self._get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)
            """, (key, json.dumps(value)))
            conn.commit()