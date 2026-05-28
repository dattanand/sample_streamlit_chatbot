import re
from enum import Enum

class QueryType(Enum):
    TROUBLESHOOTING = "troubleshooting"
    PRODUCT_COMPARISON = "comparison"
    GENERAL = "general"

class QueryClassifier:
    """Classifies user queries into troubleshooting, comparison, or general categories"""
    
    # Troubleshooting keywords
    TROUBLESHOOTING_KEYWORDS = [
        "overheat", "overheating", "hot", "battery drain", "not charging",
        "won't turn on", "won't start", "freezing", "lag", "slow", "crash",
        "error", "issue", "problem", "not working", "failing", "stuck",
        "blank screen", "black screen", "no sound", "no audio", "bluetooth",
        "wifi", "connection", "restart", "reset", "fix", "repair"
    ]
    
    # Comparison keywords
    COMPARISON_KEYWORDS = [
        "compare", "vs", "versus", "difference", "better", "which",
        "between", "compared to", "or", "advantages", "disadvantages"
    ]
    
    @classmethod
    def classify(cls, query: str) -> QueryType:
        """
        Classify query based on keyword matching and patterns
        Returns QueryType enum value
        """
        query_lower = query.lower()
        
        # Check for troubleshooting first (more specific)
        if any(keyword in query_lower for keyword in cls.TROUBLESHOOTING_KEYWORDS):
            return QueryType.TROUBLESHOOTING
        
        # Check for comparison
        if any(keyword in query_lower for keyword in cls.COMPARISON_KEYWORDS):
            return QueryType.PRODUCT_COMPARISON
        
        # Default to general
        return QueryType.GENERAL
    
    @classmethod
    def classify_with_llm(cls, query: str, llm_client) -> QueryType:
        """
        Use Azure OpenAI for more sophisticated classification (fallback/alternative)
        This is kept for compatibility but the main app uses a direct function
        """
        prompt = f"""
        Classify the following customer support query into exactly ONE category:
        
        Categories:
        - TROUBLESHOOTING: Issues, problems, errors, device not working properly
        - PRODUCT_COMPARISON: Comparing two or more products, asking which is better
        - GENERAL: Questions about features, specifications, general information
        
        Query: "{query}"
        
        Output only the category name (TROUBLESHOOTING/PRODUCT_COMPARISON/GENERAL):
        """
        
        try:
            response = llm_client.invoke(prompt)
            result = response.content.strip().upper()
            
            if result == "TROUBLESHOOTING":
                return QueryType.TROUBLESHOOTING
            elif result == "PRODUCT_COMPARISON":
                return QueryType.PRODUCT_COMPARISON
            else:
                return QueryType.GENERAL
        except:
            # Fallback to rule-based
            return cls.classify(query)