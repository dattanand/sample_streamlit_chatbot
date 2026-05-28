from datetime import datetime
from typing import List, Dict

class ConversationMemory:
    """Maintains chat history and handles context for follow-up queries"""
    
    def __init__(self, max_history=10):
        self.history: List[Dict] = []
        self.max_history = max_history
        self.current_topic = None
        self.last_query_type = None
    
    def add_exchange(self, question: str, answer: str, query_type: str):
        """Add a question-answer exchange to history"""
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "answer": answer,
            "query_type": query_type
        })
        
        # Update current topic based on question
        self.current_topic = self._extract_topic(question)
        self.last_query_type = query_type
        
        # Trim history if too long
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
    
    def get_formatted_history(self) -> str:
        """Get formatted chat history for context"""
        if not self.history:
            return "No previous conversation."
        
        formatted = []
        for exchange in self.history:
            formatted.append(f"Customer: {exchange['question']}")
            formatted.append(f"Support: {exchange['answer']}\n")
        
        return "\n".join(formatted)
    
    def get_context_for_followup(self, current_query: str) -> str:
        """Get context to help resolve follow-up queries"""
        if not self.history:
            return ""
        
        context_parts = []
        
        # Add last exchange if relevant
        if self.history:
            last = self.history[-1]
            context_parts.append(f"Previous topic: {last['question'][:100]}")
            context_parts.append(f"Last query type: {last['query_type']}")
        
        # Detect if this is a follow-up (short, referring to previous)
        if len(current_query.split()) < 8 and any(word in current_query.lower() for word in ["it", "this", "that", "still", "again"]):
            context_parts.append("This appears to be a follow-up question.")
        
        return "\n".join(context_parts) if context_parts else ""
    
    def clear(self):
        """Clear conversation history"""
        self.history = []
        self.current_topic = None
        self.last_query_type = None
    
    def _extract_topic(self, question: str) -> str:
        """Extract main topic from question"""
        # Simple topic extraction based on keywords
        product_keywords = ["galaxy", "s23", "s24", "tv", "watch", "buds", "tablet"]
        
        for keyword in product_keywords:
            if keyword.lower() in question.lower():
                return keyword
        
        issue_keywords = ["battery", "screen", "sound", "camera", "overheating"]
        for keyword in issue_keywords:
            if keyword.lower() in question.lower():
                return f"{keyword}_issue"
        
        return "general"