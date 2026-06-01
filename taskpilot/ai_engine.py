"""
AI Engine for TaskPilot-CLI
Zero external dependencies - uses rule-based AI for priority calculation
and natural language processing
"""

import re
from datetime import datetime, timedelta
from typing import List, Tuple, Optional, Dict, Any
from .models import Task, Priority


class AIEngine:
    """
    AI-powered task analysis engine
    Uses rule-based algorithms for zero-dependency operation
    """
    
    # Keywords for priority detection
    URGENT_KEYWORDS = [
        "urgent", "asap", "immediately", "critical", "emergency",
        "紧急", "立即", "马上", "关键", "重要", "deadline", "today", "tomorrow"
    ]
    
    HIGH_KEYWORDS = [
        "important", "high priority", "significant", "crucial",
        "重要", "高优先级", "关键", "必须", "need to", "should"
    ]
    
    LOW_KEYWORDS = [
        "low priority", "whenever", "someday", "maybe", "if time",
        "低优先级", "有空", "以后", "或许", "optional", "optional"
    ]
    
    # Keywords for time estimation
    TIME_PATTERNS = {
        r"(\d+)\s*hour": lambda x: int(x) * 60,
        r"(\d+)\s*hr": lambda x: int(x) * 60,
        r"(\d+)\s*min": lambda x: int(x),
        r"(\d+)\s*m": lambda x: int(x),
        r"half hour": lambda x: 30,
        r"quarter hour": lambda x: 15,
    }
    
    # Due date patterns
    DATE_PATTERNS = {
        r"today": lambda: datetime.now(),
        r"tomorrow": lambda: datetime.now() + timedelta(days=1),
        r"next week": lambda: datetime.now() + timedelta(days=7),
        r"in (\d+) days": lambda x: datetime.now() + timedelta(days=int(x)),
        r"in (\d+) day": lambda x: datetime.now() + timedelta(days=int(x)),
    }
    
    def __init__(self):
        """Initialize AI engine"""
        pass
    
    def analyze_task(self, title: str, description: str = "") -> Dict[str, Any]:
        """
        Analyze task text and return AI insights
        
        Returns:
            Dict with keys: priority, estimated_minutes, due_date, tags, confidence
        """
        text = f"{title} {description}".lower()
        
        # Detect priority
        priority = self._detect_priority(text)
        
        # Estimate time
        estimated_minutes = self._estimate_time(text)
        
        # Parse due date
        due_date = self._parse_due_date(text)
        
        # Extract tags
        tags = self._extract_tags(text)
        
        # Calculate priority score
        priority_score = self._calculate_priority_score(
            priority, due_date, estimated_minutes, text
        )
        
        return {
            "priority": priority,
            "estimated_minutes": estimated_minutes,
            "due_date": due_date,
            "tags": tags,
            "priority_score": priority_score,
        }
    
    def _detect_priority(self, text: str) -> Priority:
        """Detect task priority from text"""
        text_lower = text.lower()
        
        # Check for urgent keywords
        for keyword in self.URGENT_KEYWORDS:
            if keyword in text_lower:
                return Priority.URGENT
        
        # Check for high priority keywords
        for keyword in self.HIGH_KEYWORDS:
            if keyword in text_lower:
                return Priority.HIGH
        
        # Check for low priority keywords
        for keyword in self.LOW_KEYWORDS:
            if keyword in text_lower:
                return Priority.LOW
        
        return Priority.MEDIUM
    
    def _estimate_time(self, text: str) -> int:
        """Estimate task duration in minutes"""
        text_lower = text.lower()
        
        for pattern, converter in self.TIME_PATTERNS.items():
            match = re.search(pattern, text_lower)
            if match:
                if match.groups():
                    return converter(match.group(1))
                else:
                    return converter()
        
        # Default to 25 minutes (standard pomodoro)
        return 25
    
    def _parse_due_date(self, text: str) -> Optional[datetime]:
        """Parse due date from text"""
        text_lower = text.lower()
        
        for pattern, converter in self.DATE_PATTERNS.items():
            match = re.search(pattern, text_lower)
            if match:
                if match.groups():
                    return converter(match.group(1))
                else:
                    return converter()
        
        return None
    
    def _extract_tags(self, text: str) -> List[str]:
        """Extract hashtags and category keywords as tags"""
        tags = []
        
        # Extract hashtags
        hashtags = re.findall(r'#(\w+)', text)
        tags.extend(hashtags)
        
        # Common category keywords
        categories = {
            "work": ["work", "job", "project", "meeting", "client", "老板", "工作", "项目", "会议"],
            "personal": ["personal", "home", "family", "私人", "家庭", "个人"],
            "study": ["study", "learn", "course", "book", "学习", "课程", "读书"],
            "health": ["health", "exercise", "gym", "doctor", "健康", "锻炼", "医生"],
            "finance": ["finance", "money", "budget", "tax", "财务", "钱", "预算"],
            "dev": ["code", "programming", "bug", "feature", "代码", "编程", "开发"],
            "urgent": ["urgent", "asap", "critical", "紧急", "立即"],
        }
        
        text_lower = text.lower()
        for category, keywords in categories.items():
            if any(kw in text_lower for kw in keywords):
                if category not in tags:
                    tags.append(category)
        
        return list(set(tags))  # Remove duplicates
    
    def _calculate_priority_score(self, priority: Priority, 
                                   due_date: Optional[datetime],
                                   estimated_minutes: int,
                                   text: str) -> float:
        """
        Calculate AI priority score (0-100)
        Higher score = more urgent/important
        """
        score = 0.0
        
        # Base score from priority level
        priority_scores = {
            Priority.URGENT: 80,
            Priority.HIGH: 60,
            Priority.MEDIUM: 40,
            Priority.LOW: 20,
        }
        score += priority_scores.get(priority, 40)
        
        # Adjust for due date
        if due_date:
            now = datetime.now()
            days_until_due = (due_date - now).days
            
            if days_until_due < 0:
                # Overdue - boost score significantly
                score += 20
            elif days_until_due == 0:
                # Due today
                score += 15
            elif days_until_due == 1:
                # Due tomorrow
                score += 10
            elif days_until_due <= 3:
                # Due within 3 days
                score += 5
        
        # Adjust for urgency keywords
        urgency_boost = sum(1 for kw in self.URGENT_KEYWORDS if kw in text)
        score += min(urgency_boost * 2, 10)  # Cap at 10 points
        
        # Normalize to 0-100
        return min(max(score, 0), 100)
    
    def sort_tasks_by_priority(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks by AI-calculated priority"""
        return sorted(tasks, key=lambda t: (
            -t.ai_priority_score,  # Higher score first
            -t.priority.value,      # Higher priority first
            t.due_date or datetime.max,  # Earlier due date first
        ))
    
    def suggest_next_task(self, tasks: List[Task]) -> Optional[Task]:
        """
        Suggest the next task to work on based on AI analysis
        """
        # Filter pending and in-progress tasks
        active_tasks = [t for t in tasks if t.status.value in ("pending", "in_progress")]
        
        if not active_tasks:
            return None
        
        # Sort by priority
        sorted_tasks = self.sort_tasks_by_priority(active_tasks)
        
        return sorted_tasks[0] if sorted_tasks else None
    
    def generate_daily_summary(self, tasks: List[Task], 
                                completed_today: int,
                                pomodoro_sessions: int) -> str:
        """Generate AI-powered daily summary"""
        pending = [t for t in tasks if t.status.value == "pending"]
        overdue = [t for t in tasks if t.is_overdue()]
        high_priority = [t for t in tasks if t.priority in (Priority.HIGH, Priority.URGENT)]
        
        summary_parts = []
        
        # Header
        summary_parts.append(f"📊 Daily Summary - {datetime.now().strftime('%Y-%m-%d')}")
        summary_parts.append("=" * 40)
        
        # Stats
        summary_parts.append(f"✅ Tasks completed today: {completed_today}")
        summary_parts.append(f"🍅 Pomodoro sessions: {pomodoro_sessions}")
        summary_parts.append(f"⏳ Pending tasks: {len(pending)}")
        
        # Warnings
        if overdue:
            summary_parts.append(f"⚠️  Overdue tasks: {len(overdue)}")
        
        # Recommendations
        if high_priority:
            summary_parts.append(f"🔥 High priority tasks: {len(high_priority)}")
        
        # Next task suggestion
        next_task = self.suggest_next_task(tasks)
        if next_task:
            summary_parts.append(f"💡 Suggested next: {next_task.title}")
        
        return "\n".join(summary_parts)
    
    def parse_natural_language(self, text: str) -> Dict[str, Any]:
        """
        Parse natural language task input
        
        Examples:
        - "Buy milk tomorrow high priority"
        - "Finish report by Friday 2 hours"
        - "Call mom today #personal"
        """
        result = {
            "title": text,
            "description": "",
            "priority": Priority.MEDIUM,
            "due_date": None,
            "estimated_minutes": 25,
            "tags": [],
        }
        
        # Extract due date phrases and remove them from title
        text_lower = text.lower()
        for pattern, converter in self.DATE_PATTERNS.items():
            match = re.search(pattern, text_lower)
            if match:
                result["due_date"] = converter() if not match.groups() else converter(match.group(1))
                # Remove date phrase from title
                result["title"] = re.sub(pattern, "", text_lower, flags=re.IGNORECASE).strip()
        
        # Detect priority
        result["priority"] = self._detect_priority(text)
        
        # Estimate time
        result["estimated_minutes"] = self._estimate_time(text)
        
        # Extract tags
        result["tags"] = self._extract_tags(text)
        
        # Clean up title
        result["title"] = result["title"].strip()
        # Capitalize first letter
        if result["title"]:
            result["title"] = result["title"][0].upper() + result["title"][1:]
        
        return result