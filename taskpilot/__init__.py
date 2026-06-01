"""
TaskPilot-CLI - Lightweight Terminal AI Task Management Engine
轻量级终端AI智能任务管理引擎

A zero-dependency, AI-powered task management CLI tool with pomodoro timer,
natural language processing, and intelligent priority sorting.
"""

__version__ = "1.0.0"
__author__ = "TaskPilot Team"
__license__ = "MIT"

from .core import TaskPilot
from .models import Task, TaskStatus, Priority
from .ai_engine import AIEngine
from .pomodoro import PomodoroTimer

__all__ = [
    "TaskPilot",
    "Task", 
    "TaskStatus",
    "Priority",
    "AIEngine",
    "PomodoroTimer",
]