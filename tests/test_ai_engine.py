"""
Unit tests for AI Engine
"""

import unittest
from datetime import datetime
from taskpilot.ai_engine import AIEngine
from taskpilot.models import Priority


class TestAIEngine(unittest.TestCase):
    """Test AI Engine"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.ai = AIEngine()
    
    def test_detect_priority_urgent(self):
        """Test urgent priority detection"""
        text = "This is urgent and needs to be done asap"
        priority = self.ai._detect_priority(text)
        self.assertEqual(priority, Priority.URGENT)
    
    def test_detect_priority_high(self):
        """Test high priority detection"""
        text = "This is important and high priority"
        priority = self.ai._detect_priority(text)
        self.assertEqual(priority, Priority.HIGH)
    
    def test_detect_priority_low(self):
        """Test low priority detection"""
        text = "This is low priority and can be done whenever"
        priority = self.ai._detect_priority(text)
        self.assertEqual(priority, Priority.LOW)
    
    def test_detect_priority_medium(self):
        """Test medium priority (default)"""
        text = "This is a normal task"
        priority = self.ai._detect_priority(text)
        self.assertEqual(priority, Priority.MEDIUM)
    
    def test_estimate_time(self):
        """Test time estimation"""
        # Should detect hours
        self.assertEqual(self.ai._estimate_time("2 hours"), 120)
        self.assertEqual(self.ai._estimate_time("1 hr"), 60)
        
        # Should detect minutes
        self.assertEqual(self.ai._estimate_time("30 min"), 30)
        self.assertEqual(self.ai._estimate_time("15 m"), 15)
        
        # Default
        self.assertEqual(self.ai._estimate_time("some task"), 25)
    
    def test_extract_tags(self):
        """Test tag extraction"""
        text = "Finish the report #work #urgent and send to boss"
        tags = self.ai._extract_tags(text)
        
        self.assertIn("work", tags)
        self.assertIn("urgent", tags)
    
    def test_analyze_task(self):
        """Test full task analysis"""
        result = self.ai.analyze_task(
            "Finish urgent report tomorrow",
            "This is critical for the meeting"
        )
        
        self.assertIn("priority", result)
        self.assertIn("estimated_minutes", result)
        self.assertIn("tags", result)
        self.assertIn("priority_score", result)
    
    def test_parse_natural_language(self):
        """Test natural language parsing"""
        text = "Buy milk today #personal high priority"
        result = self.ai.parse_natural_language(text)
        
        self.assertEqual(result["title"], "Buy milk")
        self.assertIn("personal", result["tags"])
        self.assertEqual(result["priority"], Priority.HIGH)


if __name__ == "__main__":
    unittest.main()