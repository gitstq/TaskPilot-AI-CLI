"""
TaskPilot-CLI Entry Point
"""

import sys
import argparse
from .core import TaskPilot
from .tui import TUI


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="🎯 TaskPilot-CLI - Lightweight Terminal AI Task Management Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                              # Launch interactive mode
  %(prog)s add "Finish report tomorrow" # Add task with natural language
  %(prog)s list                         # List all pending tasks
  %(prog)s done task_abc123             # Mark task as completed
  %(prog)s stats                        # Show statistics

For more help in interactive mode, type 'help'.
        """
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new task")
    add_parser.add_argument("text", nargs="+", help="Task description (supports natural language)")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List tasks")
    list_parser.add_argument("--all", "-a", action="store_true", help="List all tasks including completed")
    list_parser.add_argument("--status", "-s", choices=["pending", "in_progress", "completed", "archived"],
                            help="Filter by status")
    
    # Done command
    done_parser = subparsers.add_parser("done", help="Mark task as completed")
    done_parser.add_argument("task_id", help="Task ID")
    
    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a task")
    delete_parser.add_argument("task_id", help="Task ID")
    delete_parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search tasks")
    search_parser.add_argument("query", help="Search query")
    
    # Stats command
    subparsers.add_parser("stats", help="Show statistics")
    
    # Summary command
    subparsers.add_parser("summary", help="Show daily summary")
    
    # Suggest command
    subparsers.add_parser("suggest", help="Get AI task suggestion")
    
    # Overdue command
    subparsers.add_parser("overdue", help="Show overdue tasks")
    
    # Pomodoro commands
    pomodoro_parser = subparsers.add_parser("pomodoro", help="Pomodoro timer commands")
    pomodoro_subparsers = pomodoro_parser.add_subparsers(dest="pomodoro_action")
    
    pomodoro_start = pomodoro_subparsers.add_parser("start", help="Start pomodoro for a task")
    pomodoro_start.add_argument("task_id", help="Task ID")
    
    pomodoro_subparsers.add_parser("stop", help="Stop current pomodoro")
    pomodoro_subparsers.add_parser("pause", help="Pause pomodoro")
    pomodoro_subparsers.add_parser("resume", help="Resume pomodoro")
    pomodoro_subparsers.add_parser("status", help="Show pomodoro status")
    
    args = parser.parse_args()
    
    # Initialize TaskPilot
    tp = TaskPilot()
    tui = TUI(tp)
    
    # Interactive mode if no command
    if not args.command:
        tui.interactive_mode()
        return
    
    # Execute command
    try:
        if args.command == "add":
            text = " ".join(args.text)
            task = tp.create_task_from_natural_language(text)
            tui.print_message(f"Task created: {task.title}", "success")
            print(f"ID: {task.id}")
            print(f"Priority: {task.priority.name}")
            if task.due_date:
                print(f"Due: {task.due_date.strftime('%Y-%m-%d')}")
        
        elif args.command == "list":
            if args.all:
                tasks = tp.list_tasks()
                title = "📋 All Tasks"
            elif args.status:
                tasks = tp.list_tasks(args.status)
                title = f"📋 Tasks ({args.status})"
            else:
                tasks = tp.list_tasks("pending")
                title = "📋 Pending Tasks"
            
            tui.print_task_list(tasks, title)
        
        elif args.command == "done":
            task = tp.complete_task(args.task_id)
            if task:
                tui.print_message(f"Completed: {task.title}", "success")
            else:
                tui.print_message("Task not found", "error")
                sys.exit(1)
        
        elif args.command == "delete":
            if args.yes or tui.confirm(f"Delete task {args.task_id}?"):
                if tp.delete_task(args.task_id):
                    tui.print_message("Task deleted", "success")
                else:
                    tui.print_message("Task not found", "error")
                    sys.exit(1)
        
        elif args.command == "search":
            tasks = tp.search_tasks(args.query)
            tui.print_task_list(tasks, f"🔍 Search Results for '{args.query}'")
        
        elif args.command == "stats":
            tui.print_stats()
        
        elif args.command == "summary":
            summary = tp.get_daily_summary()
            print(summary)
        
        elif args.command == "suggest":
            tui.print_suggestion()
        
        elif args.command == "overdue":
            tasks = tp.get_overdue_tasks()
            tui.print_task_list(tasks, "⚠️ Overdue Tasks")
        
        elif args.command == "pomodoro":
            if args.pomodoro_action == "start":
                session = tp.start_pomodoro(args.task_id)
                tui.print_message(f"Pomodoro started for task {args.task_id}", "success")
                print(f"Session ID: {session.id}")
                print(f"Duration: {session.duration_minutes} minutes")
            
            elif args.pomodoro_action == "stop":
                session = tp.stop_pomodoro()
                if session:
                    tui.print_message("Pomodoro stopped", "success")
                    print(f"Completed: {session.completed}")
                else:
                    tui.print_message("No active pomodoro", "warning")
            
            elif args.pomodoro_action == "pause":
                tp.pause_pomodoro()
                tui.print_message("Pomodoro paused", "info")
            
            elif args.pomodoro_action == "resume":
                tp.resume_pomodoro()
                tui.print_message("Pomodoro resumed", "success")
            
            elif args.pomodoro_action == "status":
                tui.print_pomodoro_status()
            
            else:
                pomodoro_parser.print_help()
    
    except KeyboardInterrupt:
        print("\nInterrupted.")
        sys.exit(0)
    except Exception as e:
        tui.print_message(f"Error: {e}", "error")
        sys.exit(1)


if __name__ == "__main__":
    main()
