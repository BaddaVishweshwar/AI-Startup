"""
Conversation Context Manager

Manages conversation history and context for multi-turn interactions.
Enables follow-up questions and context-aware analysis.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class ConversationManager:
    """Manages conversation history and context per session."""
    
    def __init__(self):
        """Initialize conversation manager."""
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.max_history = 10  # Keep last 10 exchanges
    
    def add_exchange(
        self,
        session_id: str,
        user_query: str,
        sql_query: Optional[str] = None,
        results: Optional[List[Dict[str, Any]]] = None,
        insights: Optional[str] = None,
        visualizations: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """
        Add a query-response exchange to conversation history.
        
        Args:
            session_id: Unique session identifier
            user_query: User's natural language question
            sql_query: Generated SQL query
            results: Query results (limited sample)
            insights: Generated insights
            visualizations: Visualization configs
        """
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "history": [],
                "dataset_id": None,
                "created_at": datetime.now().isoformat()
            }
        
        exchange = {
            "timestamp": datetime.now().isoformat(),
            "user_query": user_query,
            "sql_query": sql_query,
            "results_summary": self._summarize_results(results) if results else None,
            "insights": insights,
            "visualization_types": [v.get('type') for v in visualizations] if visualizations else []
        }
        
        self.sessions[session_id]["history"].append(exchange)
        
        # Keep only last N exchanges
        if len(self.sessions[session_id]["history"]) > self.max_history:
            self.sessions[session_id]["history"] = \
                self.sessions[session_id]["history"][-self.max_history:]
        
        logger.info(f"Added exchange to session {session_id}. Total: {len(self.sessions[session_id]['history'])}")
    
    def get_context(
        self,
        session_id: str,
        last_n: int = 3
    ) -> str:
        """
        Get formatted conversation context for prompts.
        
        Args:
            session_id: Session identifier
            last_n: Number of recent exchanges to include
            
        Returns:
            Formatted conversation history string
        """
        if session_id not in self.sessions:
            return "No previous conversation"
        
        history = self.sessions[session_id]["history"][-last_n:]
        
        if not history:
            return "No previous conversation"
        
        lines = ["Recent conversation:"]
        for i, exchange in enumerate(history, 1):
            lines.append(f"\n{i}. User: {exchange['user_query']}")
            if exchange.get('sql_query'):
                lines.append(f"   SQL: {exchange['sql_query'][:100]}...")
            if exchange.get('results_summary'):
                lines.append(f"   Results: {exchange['results_summary']}")
            if exchange.get('insights'):
                lines.append(f"   Insights: {exchange['insights'][:150]}...")
        
        return "\n".join(lines)
    
    def get_history(
        self,
        session_id: str,
        last_n: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get raw conversation history.
        
        Args:
            session_id: Session identifier
            last_n: Number of recent exchanges (None = all)
            
        Returns:
            List of exchange dictionaries
        """
        if session_id not in self.sessions:
            return []
        
        history = self.sessions[session_id]["history"]
        
        if last_n:
            return history[-last_n:]
        return history
    
    def set_dataset(self, session_id: str, dataset_id: int) -> None:
        """
        Set the active dataset for a session.
        
        Args:
            session_id: Session identifier
            dataset_id: Dataset ID
        """
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "history": [],
                "dataset_id": dataset_id,
                "created_at": datetime.now().isoformat()
            }
        else:
            self.sessions[session_id]["dataset_id"] = dataset_id
        
        logger.info(f"Set dataset {dataset_id} for session {session_id}")
    
    def get_dataset(self, session_id: str) -> Optional[int]:
        """
        Get the active dataset for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dataset ID or None
        """
        if session_id in self.sessions:
            return self.sessions[session_id].get("dataset_id")
        return None
    
    def clear_session(self, session_id: str) -> None:
        """
        Clear a session's history.
        
        Args:
            session_id: Session identifier
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Cleared session {session_id}")
    
    def cleanup_old_sessions(self, max_age_hours: int = 24) -> int:
        """
        Remove sessions older than max_age_hours.
        
        Args:
            max_age_hours: Maximum session age in hours
            
        Returns:
            Number of sessions removed
        """
        from datetime import timedelta
        
        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        removed = 0
        
        for session_id in list(self.sessions.keys()):
            created_at = datetime.fromisoformat(
                self.sessions[session_id]["created_at"]
            )
            if created_at < cutoff:
                del self.sessions[session_id]
                removed += 1
        
        if removed > 0:
            logger.info(f"Cleaned up {removed} old sessions")
        
        return removed
    
    def _summarize_results(self, results: List[Dict[str, Any]]) -> str:
        """
        Create a brief summary of query results.
        
        Args:
            results: Query result rows
            
        Returns:
            Summary string
        """
        if not results:
            return "No results"
        
        row_count = len(results)
        
        if row_count == 0:
            return "No results"
        elif row_count == 1:
            return f"1 row returned"
        else:
            return f"{row_count} rows returned"
    
    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """
        Get statistics about a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session statistics
        """
        if session_id not in self.sessions:
            return {"exists": False}
        
        session = self.sessions[session_id]
        
        return {
            "exists": True,
            "exchange_count": len(session["history"]),
            "dataset_id": session.get("dataset_id"),
            "created_at": session["created_at"],
            "last_query": session["history"][-1]["user_query"] if session["history"] else None
        }


# Singleton instance
conversation_manager = ConversationManager()
