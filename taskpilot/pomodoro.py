"""
Pomodoro timer implementation for TaskPilot-CLI
Zero external dependencies
"""

import time
import threading
from datetime import datetime, timedelta
from typing import Optional, Callable, List
from .models import PomodoroSession


class PomodoroTimer:
    """
    Pomodoro timer with callback support
    """
    
    def __init__(self, 
                 work_minutes: int = 25,
                 short_break_minutes: int = 5,
                 long_break_minutes: int = 15,
                 sessions_before_long_break: int = 4):
        """
        Initialize pomodoro timer
        
        Args:
            work_minutes: Duration of work session
            short_break_minutes: Duration of short break
            long_break_minutes: Duration of long break
            sessions_before_long_break: Number of work sessions before long break
        """
        self.work_minutes = work_minutes
        self.short_break_minutes = short_break_minutes
        self.long_break_minutes = long_break_minutes
        self.sessions_before_long_break = sessions_before_long_break
        
        self._timer_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._is_running = False
        self._is_paused = False
        
        self._current_session: Optional[PomodoroSession] = None
        self._session_count = 0
        self._remaining_seconds = 0
        
        # Callbacks
        self.on_tick: Optional[Callable[[int, int], None]] = None  # (remaining, total)
        self.on_complete: Optional[Callable[[], None]] = None
        self.on_break_start: Optional[Callable[[int], None]] = None  # (break_minutes)
    
    @property
    def is_running(self) -> bool:
        """Check if timer is running"""
        return self._is_running
    
    @property
    def is_paused(self) -> bool:
        """Check if timer is paused"""
        return self._is_paused
    
    def start(self, task_id: str) -> PomodoroSession:
        """
        Start a new pomodoro session
        
        Args:
            task_id: ID of the task being worked on
            
        Returns:
            PomodoroSession object
        """
        if self._is_running:
            raise RuntimeError("Timer is already running")
        
        self._stop_event.clear()
        self._pause_event.clear()
        self._is_paused = False
        
        self._current_session = PomodoroSession(
            id=self._generate_session_id(),
            task_id=task_id,
            started_at=datetime.now(),
            duration_minutes=self.work_minutes,
        )
        
        self._remaining_seconds = self.work_minutes * 60
        
        self._timer_thread = threading.Thread(target=self._run_timer)
        self._timer_thread.daemon = True
        self._timer_thread.start()
        
        self._is_running = True
        
        return self._current_session
    
    def pause(self):
        """Pause the current session"""
        if self._is_running and not self._is_paused:
            self._pause_event.set()
            self._is_paused = True
    
    def resume(self):
        """Resume a paused session"""
        if self._is_running and self._is_paused:
            self._pause_event.clear()
            self._is_paused = False
    
    def stop(self) -> Optional[PomodoroSession]:
        """
        Stop the current session
        
        Returns:
            Completed session or None if no session was running
        """
        if not self._is_running:
            return None
        
        self._stop_event.set()
        self._pause_event.set()  # Unpause if paused
        
        if self._timer_thread:
            self._timer_thread.join(timeout=1)
        
        self._is_running = False
        self._is_paused = False
        
        if self._current_session:
            self._current_session.ended_at = datetime.now()
            session = self._current_session
            self._current_session = None
            return session
        
        return None
    
    def get_remaining_time(self) -> tuple:
        """
        Get remaining time
        
        Returns:
            Tuple of (minutes, seconds)
        """
        minutes = self._remaining_seconds // 60
        seconds = self._remaining_seconds % 60
        return minutes, seconds
    
    def get_progress_percentage(self) -> float:
        """Get session progress percentage (0-100)"""
        if not self._is_running:
            return 0.0
        total_seconds = self.work_minutes * 60
        elapsed = total_seconds - self._remaining_seconds
        return (elapsed / total_seconds) * 100
    
    def _run_timer(self):
        """Main timer loop"""
        total_seconds = self._remaining_seconds
        
        while self._remaining_seconds > 0 and not self._stop_event.is_set():
            # Check if paused
            if self._pause_event.is_set():
                time.sleep(0.1)
                continue
            
            # Call tick callback
            if self.on_tick:
                try:
                    self.on_tick(self._remaining_seconds, total_seconds)
                except Exception:
                    pass
            
            time.sleep(1)
            self._remaining_seconds -= 1
        
        # Session completed
        if self._remaining_seconds <= 0 and not self._stop_event.is_set():
            self._session_count += 1
            
            if self._current_session:
                self._current_session.completed = True
                self._current_session.ended_at = datetime.now()
            
            if self.on_complete:
                try:
                    self.on_complete()
                except Exception:
                    pass
            
            # Auto-start break
            self._start_break()
        
        self._is_running = False
    
    def _start_break(self):
        """Start break after work session"""
        # Determine break length
        if self._session_count % self.sessions_before_long_break == 0:
            break_minutes = self.long_break_minutes
        else:
            break_minutes = self.short_break_minutes
        
        if self.on_break_start:
            try:
                self.on_break_start(break_minutes)
            except Exception:
                pass
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        import uuid
        return f"pom_{uuid.uuid4().hex[:8]}"
    
    def format_time(self, minutes: int, seconds: int) -> str:
        """Format time as MM:SS"""
        return f"{minutes:02d}:{seconds:02d}"
    
    def get_current_formatted_time(self) -> str:
        """Get current remaining time formatted"""
        minutes, seconds = self.get_remaining_time()
        return self.format_time(minutes, seconds)


class PomodoroStats:
    """Statistics calculator for pomodoro sessions"""
    
    @staticmethod
    def calculate_total_focus_time(sessions: List[PomodoroSession]) -> int:
        """Calculate total focus time in minutes"""
        total = 0
        for session in sessions:
            if session.completed and session.ended_at:
                duration = (session.ended_at - session.started_at).total_seconds() / 60
                total += int(duration)
            else:
                total += session.duration_minutes
        return total
    
    @staticmethod
    def calculate_completion_rate(sessions: List[PomodoroSession]) -> float:
        """Calculate completion rate (0-100)"""
        if not sessions:
            return 0.0
        completed = sum(1 for s in sessions if s.completed)
        return (completed / len(sessions)) * 100
    
    @staticmethod
    def calculate_average_interruptions(sessions: List[PomodoroSession]) -> float:
        """Calculate average interruptions per session"""
        if not sessions:
            return 0.0
        total = sum(s.interruptions for s in sessions)
        return total / len(sessions)
    
    @staticmethod
    def get_daily_stats(sessions: List[PomodoroSession], date: datetime) -> dict:
        """Get stats for a specific date"""
        date_str = date.strftime("%Y-%m-%d")
        
        daily_sessions = [
            s for s in sessions 
            if s.started_at.strftime("%Y-%m-%d") == date_str
        ]
        
        return {
            "date": date_str,
            "total_sessions": len(daily_sessions),
            "completed_sessions": sum(1 for s in daily_sessions if s.completed),
            "total_focus_minutes": PomodoroStats.calculate_total_focus_time(daily_sessions),
            "completion_rate": PomodoroStats.calculate_completion_rate(daily_sessions),
            "total_interruptions": sum(s.interruptions for s in daily_sessions),
        }