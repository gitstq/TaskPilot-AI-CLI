"""
Terminal User Interface for TaskPilot-CLI
Zero external dependencies - uses ANSI escape codes
"""

import os
import sys
import shutil
from datetime import datetime
from typing import List, Optional, Callable

from .models import Task, TaskStatus, Priority
from .core import TaskPilot


class Colors:
    """ANSI color codes"""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    UNDERLINE = "\033[4m"
    
    # Foreground colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # Bright colors
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"
    
    # Background colors
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"


class TUI:
    """
    Terminal User Interface
    """
    
    def __init__(self, taskpilot: TaskPilot):
        """Initialize TUI"""
        self.tp = taskpilot
        self.term_width = shutil.get_terminal_size().columns
        self.term_height = shutil.get_terminal_size().lines
    
    def clear(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self, title: str):
        """Print header with title"""
        width = min(self.term_width, 80)
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * width}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}  🎯 {title}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'=' * width}{Colors.RESET}\n")
    
    def print_task(self, task: Task, index: Optional[int] = None):
        """Print a single task"""
        prefix = f"{index}. " if index is not None else "   "
        
        # Status and priority emojis
        status_emoji = task.get_status_emoji()
        priority_emoji = task.get_priority_emoji()
        
        # Title with color based on priority
        if task.priority == Priority.URGENT:
            title_color = Colors.BRIGHT_RED
        elif task.priority == Priority.HIGH:
            title_color = Colors.BRIGHT_YELLOW
        elif task.priority == Priority.LOW:
            title_color = Colors.DIM
        else:
            title_color = Colors.RESET
        
        # Overdue indicator
        overdue_marker = f" {Colors.BRIGHT_RED}[OVERDUE]{Colors.RESET}" if task.is_overdue() else ""
        
        print(f"{prefix}{status_emoji} {priority_emoji} {title_color}{task.title}{Colors.RESET}{overdue_marker}")
        
        # Description (if exists)
        if task.description:
            desc = task.description[:60] + "..." if len(task.description) > 60 else task.description
            print(f"     {Colors.DIM}{desc}{Colors.RESET}")
        
        # Metadata
        meta_parts = []
        if task.due_date:
            due_str = task.due_date.strftime("%Y-%m-%d")
            meta_parts.append(f"📅 {due_str}")
        if task.tags:
            meta_parts.append(f"🏷️  {', '.join(task.tags[:3])}")
        if task.estimated_minutes:
            meta_parts.append(f"⏱️  {task.estimated_minutes}min")
        if task.ai_priority_score > 0:
            meta_parts.append(f"🤖 {task.ai_priority_score:.0f}")
        
        if meta_parts:
            print(f"     {Colors.DIM}{' | '.join(meta_parts)}{Colors.RESET}")
        
        print()
    
    def print_task_list(self, tasks: List[Task], title: str = "Tasks"):
        """Print a list of tasks"""
        self.print_header(title)
        
        if not tasks:
            print(f"{Colors.DIM}No tasks found.{Colors.RESET}\n")
            return
        
        for i, task in enumerate(tasks, 1):
            self.print_task(task, i)
    
    def print_stats(self):
        """Print statistics dashboard"""
        self.print_header("📊 Statistics")
        
        # Get stats
        stats = self.tp.get_stats(7)
        productivity = self.tp.get_productivity_score()
        
        # Productivity score
        if productivity >= 80:
            score_color = Colors.BRIGHT_GREEN
            emoji = "🔥"
        elif productivity >= 60:
            score_color = Colors.BRIGHT_YELLOW
            emoji = "⚡"
        elif productivity >= 40:
            score_color = Colors.YELLOW
            emoji = "📈"
        else:
            score_color = Colors.DIM
            emoji = "💤"
        
        print(f"{emoji} Productivity Score: {score_color}{productivity:.1f}/100{Colors.RESET}\n")
        
        # Weekly stats
        print(f"{Colors.BOLD}Last 7 Days:{Colors.RESET}")
        total_tasks = sum(s.tasks_created for s in stats)
        total_completed = sum(s.tasks_completed for s in stats)
        total_pomodoro = sum(s.pomodoro_sessions for s in stats)
        total_focus = sum(s.total_focus_minutes for s in stats)
        
        print(f"  📋 Tasks Created: {total_tasks}")
        print(f"  ✅ Tasks Completed: {total_completed}")
        print(f"  🍅 Pomodoro Sessions: {total_pomodoro}")
        print(f"  ⏰ Total Focus Time: {total_focus // 60}h {total_focus % 60}m")
        
        if total_tasks > 0:
            completion_rate = (total_completed / total_tasks) * 100
            print(f"  📊 Completion Rate: {completion_rate:.1f}%")
        
        print()
        
        # Daily breakdown
        print(f"{Colors.BOLD}Daily Breakdown:{Colors.RESET}")
        for stat in stats:
            bar_length = min(stat.tasks_completed * 2, 20)
            bar = "█" * bar_length
            print(f"  {stat.date.strftime('%a')}: {Colors.GREEN}{bar}{Colors.RESET} {stat.tasks_completed}")
        
        print()
    
    def print_pomodoro_status(self):
        """Print pomodoro timer status"""
        status = self.tp.get_pomodoro_status()
        
        if not status["is_running"]:
            print(f"{Colors.DIM}No active pomodoro session.{Colors.RESET}")
            return
        
        # Progress bar
        progress = int(status["progress_percentage"] / 5)  # 20 segments
        bar = "█" * progress + "░" * (20 - progress)
        
        # Color based on remaining time
        if status["remaining_minutes"] < 5:
            color = Colors.BRIGHT_RED
        elif status["remaining_minutes"] < 15:
            color = Colors.BRIGHT_YELLOW
        else:
            color = Colors.BRIGHT_GREEN
        
        status_text = "PAUSED" if status["is_paused"] else "RUNNING"
        
        print(f"\n{Colors.BOLD}🍅 Pomodoro Timer [{status_text}]{Colors.RESET}")
        print(f"{color}┌{'─' * 40}┐{Colors.RESET}")
        print(f"{color}│ {bar} │{Colors.RESET}")
        print(f"{color}│     {status['formatted_time']} remaining      │{Colors.RESET}")
        print(f"{color}└{'─' * 40}┘{Colors.RESET}\n")
    
    def print_suggestion(self):
        """Print AI task suggestion"""
        suggestion = self.tp.suggest_next_task()
        
        if suggestion:
            print(f"\n{Colors.BOLD}{Colors.BRIGHT_CYAN}💡 AI Suggestion:{Colors.RESET}")
            print(f"   Next task: {Colors.BOLD}{suggestion.title}{Colors.RESET}")
            print(f"   Priority: {suggestion.get_priority_emoji()} {suggestion.priority.name}")
            if suggestion.ai_priority_score > 0:
                print(f"   AI Score: {suggestion.ai_priority_score:.0f}/100")
            print()
        else:
            print(f"\n{Colors.DIM}💡 No pending tasks to suggest.{Colors.RESET}\n")
    
    def print_help(self):
        """Print help information"""
        self.print_header("❓ Help")
        
        commands = [
            ("add <task>", "Add a new task (supports natural language)"),
            ("list", "List all pending tasks"),
            ("list all", "List all tasks including completed"),
            ("done <id>", "Mark task as completed"),
            ("delete <id>", "Delete a task"),
            ("search <query>", "Search tasks"),
            ("start <id>", "Start pomodoro for a task"),
            ("stop", "Stop current pomodoro"),
            ("pause", "Pause pomodoro"),
            ("resume", "Resume pomodoro"),
            ("stats", "Show statistics"),
            ("summary", "Show daily summary"),
            ("suggest", "Get AI task suggestion"),
            ("overdue", "Show overdue tasks"),
            ("help", "Show this help"),
            ("quit", "Exit TaskPilot"),
        ]
        
        print(f"{Colors.BOLD}Available Commands:{Colors.RESET}\n")
        for cmd, desc in commands:
            print(f"  {Colors.CYAN}{cmd:<15}{Colors.RESET} {desc}")
        
        print(f"\n{Colors.DIM}Examples:{Colors.RESET}")
        print(f"  {Colors.DIM}> add Finish report tomorrow high priority{Colors.RESET}")
        print(f"  {Colors.DIM}> add Buy milk today #personal{Colors.RESET}")
        print(f"  {Colors.DIM}> start 1{Colors.RESET}")
        print()
    
    def print_message(self, message: str, msg_type: str = "info"):
        """Print a formatted message"""
        colors = {
            "info": Colors.BLUE,
            "success": Colors.GREEN,
            "warning": Colors.YELLOW,
            "error": Colors.RED,
        }
        color = colors.get(msg_type, Colors.RESET)
        
        emojis = {
            "info": "ℹ️ ",
            "success": "✅ ",
            "warning": "⚠️ ",
            "error": "❌ ",
        }
        emoji = emojis.get(msg_type, "")
        
        print(f"{color}{emoji}{message}{Colors.RESET}")
    
    def get_input(self, prompt: str = "> ") -> str:
        """Get user input"""
        try:
            return input(f"{Colors.BOLD}{Colors.CYAN}{prompt}{Colors.RESET}").strip()
        except (EOFError, KeyboardInterrupt):
            return "quit"
    
    def confirm(self, message: str) -> bool:
        """Ask for confirmation"""
        response = input(f"{Colors.YELLOW}{message} (y/n): {Colors.RESET}").strip().lower()
        return response in ('y', 'yes')
    
    def interactive_mode(self):
        """Run interactive TUI mode"""
        self.clear()
        self.print_header("🎯 TaskPilot-CLI - AI Task Management")
        print(f"{Colors.DIM}Type 'help' for commands or 'quit' to exit.{Colors.RESET}\n")
        
        while True:
            try:
                command = self.get_input()
                
                if not command:
                    continue
                
                parts = command.split(maxsplit=1)
                cmd = parts[0].lower()
                arg = parts[1] if len(parts) > 1 else ""
                
                if cmd == "quit" or cmd == "exit":
                    self.print_message("Goodbye! 👋", "success")
                    break
                
                elif cmd == "help":
                    self.print_help()
                
                elif cmd == "add":
                    if arg:
                        task = self.tp.create_task_from_natural_language(arg)
                        self.print_message(f"Task created: {task.title}", "success")
                    else:
                        self.print_message("Please provide task description", "error")
                
                elif cmd == "list":
                    if arg == "all":
                        tasks = self.tp.list_tasks()
                    else:
                        tasks = self.tp.list_tasks("pending")
                    self.print_task_list(tasks, "📋 Your Tasks")
                
                elif cmd == "done":
                    if arg:
                        task = self.tp.complete_task(arg)
                        if task:
                            self.print_message(f"Completed: {task.title}", "success")
                        else:
                            self.print_message("Task not found", "error")
                    else:
                        self.print_message("Please provide task ID", "error")
                
                elif cmd == "delete":
                    if arg:
                        if self.confirm(f"Delete task {arg}?"):
                            if self.tp.delete_task(arg):
                                self.print_message("Task deleted", "success")
                            else:
                                self.print_message("Task not found", "error")
                    else:
                        self.print_message("Please provide task ID", "error")
                
                elif cmd == "search":
                    if arg:
                        tasks = self.tp.search_tasks(arg)
                        self.print_task_list(tasks, f"🔍 Search Results for '{arg}'")
                    else:
                        self.print_message("Please provide search query", "error")
                
                elif cmd == "start":
                    if arg:
                        try:
                            session = self.tp.start_pomodoro(arg)
                            self.print_message(f"Pomodoro started for task {arg}", "success")
                            self.print_pomodoro_status()
                        except Exception as e:
                            self.print_message(str(e), "error")
                    else:
                        self.print_message("Please provide task ID", "error")
                
                elif cmd == "stop":
                    session = self.tp.stop_pomodoro()
                    if session:
                        self.print_message("Pomodoro stopped", "success")
                    else:
                        self.print_message("No active pomodoro", "warning")
                
                elif cmd == "pause":
                    self.tp.pause_pomodoro()
                    self.print_message("Pomodoro paused", "info")
                
                elif cmd == "resume":
                    self.tp.resume_pomodoro()
                    self.print_message("Pomodoro resumed", "success")
                
                elif cmd == "status":
                    self.print_pomodoro_status()
                
                elif cmd == "stats":
                    self.print_stats()
                
                elif cmd == "summary":
                    summary = self.tp.get_daily_summary()
                    print(summary)
                
                elif cmd == "suggest":
                    self.print_suggestion()
                
                elif cmd == "overdue":
                    tasks = self.tp.get_overdue_tasks()
                    self.print_task_list(tasks, "⚠️ Overdue Tasks")
                
                else:
                    self.print_message(f"Unknown command: {cmd}", "error")
                    print(f"Type 'help' for available commands.")
            
            except KeyboardInterrupt:
                print()
                continue
            except Exception as e:
                self.print_message(f"Error: {e}", "error")