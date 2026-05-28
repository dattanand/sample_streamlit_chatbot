import json
import os
from datetime import datetime

class KnowledgeBase:
    """Manages knowledge base entries and common solutions"""
    
    COMMON_SOLUTIONS = {
        "overheating": [
            "Close background apps",
            "Reduce screen brightness",
            "Disable unused connections (WiFi, Bluetooth, GPS)",
            "Check for software updates",
            "Avoid using phone while charging"
        ],
        "battery_drain": [
            "Check battery usage in settings",
            "Reduce screen timeout",
            "Disable background app refresh",
            "Enable power saving mode",
            "Calibrate battery (full discharge then full charge)"
        ],
        "wifi_issues": [
            "Restart the router",
            "Forget and reconnect to network",
            "Reset network settings",
            "Check for software updates"
        ]
    }
    
    @classmethod
    def get_common_solution(cls, issue_type: str) -> list:
        """Get common solutions for known issues"""
        issue_key = issue_type.lower().replace(" ", "_")
        
        for key, solutions in cls.COMMON_SOLUTIONS.items():
            if key in issue_key or issue_key in key:
                return solutions
        
        return None
    
    @classmethod
    def log_interaction(cls, query: str, query_type: str, answer: str, resolved: bool = None):
        """Log customer interactions for analysis"""
        log_file = "interaction_logs.json"
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "query_type": query_type,
            "answer_preview": answer[:200],
            "resolved": resolved
        }
        
        logs = []
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                logs = json.load(f)
        
        logs.append(log_entry)
        
        # Keep last 1000 logs
        if len(logs) > 1000:
            logs = logs[-1000:]
        
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)