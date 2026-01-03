"""
SQL Validation Service

Validates generated SQL queries before execution to ensure:
- Intent match (does SQL answer the question?)
- Aggregation correctness
- Table and column validity
- Ordering logic
- Self-critique and correction
"""

import logging
import json
from typing import Dict, Any, Optional, List
from ..services.ollama_service import ollama_service
from ..prompts.camelai_prompts import MASTER_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


SQL_VALIDATION_PROMPT = """
TASK: Validate if this SQL correctly answers the question

QUESTION: "{question}"
INTENT: {intent_type}
GENERATED SQL:
{sql}

SCHEMA:
{schema_summary}

VALIDATION CHECKS:
1. ✓ Does SQL answer the question completely?
2. ✓ Are aggregations correct (SUM, AVG, COUNT)?
3. ✓ Is GROUP BY needed and present?
4. ✓ Is ORDER BY meaningful for the question?
5. ✓ Are all column names valid (exist in schema)?
6. ✓ Is table name "data" (not ActualData, sales_data, etc.)?
7. ✓ Are column names with special characters quoted?
8. ✓ Are there any logic errors?
9. ✓ Are ALL requested columns included? (check question for "and", "with", etc.)
10. ✓ Is window function usage optimal? (avoid OVER() when simple aggregation works)

LOGICAL OPTIMALITY CHECKS:
- If question asks for "TV, Radio, AND Newspaper" → SQL must include ALL three
- If simple SUM/AVG works → don't use window functions (SUM() OVER())
- If ranking needed → use ROW_NUMBER() or RANK()
- If comparing multiple items → ensure all are in SELECT clause

EXAMPLES OF ISSUES:

Bad: SELECT * FROM ActualData
Fix: SELECT * FROM data

Bad: SELECT "Sales" FROM data (missing aggregation for "total sales")
Fix: SELECT SUM("Sales ($)") as total_sales FROM data

Bad: SELECT product, revenue FROM data GROUP BY product (revenue not aggregated)
Fix: SELECT product, SUM(revenue) as total_revenue FROM data GROUP BY product

Bad: SELECT SUM("TV Budget") OVER() as total_tv FROM data (unnecessary window function)
Fix: SELECT SUM("TV Budget") as total_tv FROM data

Bad: SELECT "TV Budget", "Radio Budget" FROM data (question asked for TV, Radio, AND Newspaper)
Fix: SELECT "TV Budget", "Radio Budget", "Newspaper Budget" FROM data

EXAMPLES OF ISSUES:

Bad: SELECT * FROM ActualData
Fix: SELECT * FROM data

Bad: SELECT "Sales" FROM data (missing aggregation for "total sales")
Fix: SELECT SUM("Sales ($)") as total_sales FROM data

Bad: SELECT product, revenue FROM data GROUP BY product (revenue not aggregated)
Fix: SELECT product, SUM(revenue) as total_revenue FROM data GROUP BY product

YOUR TURN:
Analyze the SQL above and return JSON:

{{
  "is_valid": true/false,
  "confidence": 0.95,
  "issues": [
    "Issue 1: description",
    "Issue 2: description"
  ],
  "suggestions": "How to fix the SQL",
  "corrected_sql": "Fixed SQL query if issues found, otherwise null"
}}

If SQL is perfect, return:
{{
  "is_valid": true,
  "confidence": 0.95,
  "issues": [],
  "suggestions": null,
  "corrected_sql": null
}}
"""


class SQLValidatorService:
    """Validates and critiques generated SQL queries."""
    
    @staticmethod
    async def validate(
        sql: str,
        question: str,
        intent_type: str,
        schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate SQL query against question and schema.
        
        Args:
            sql: Generated SQL query
            question: Original user question
            intent_type: Query intent (comparison, trend, ranking, etc.)
            schema: Dataset schema information
            
        Returns:
            Validation result with issues and corrections
        """
        try:
            # Format schema summary
            schema_summary = SQLValidatorService._format_schema_summary(schema)
            
            # Create validation prompt
            prompt = SQL_VALIDATION_PROMPT.format(
                question=question,
                intent_type=intent_type,
                sql=sql,
                schema_summary=schema_summary
            )
            
            # Generate validation with LLM
            response = ollama_service.generate_response(
                prompt=prompt,
                system_prompt=MASTER_SYSTEM_PROMPT,
                json_mode=True,
                temperature=0.2,  # Low temperature for consistent validation
                task_type='error_correction'
            )
            
            # Parse result
            result = json.loads(response)
            
            # Log validation result
            if result.get('is_valid'):
                logger.info(f"✅ SQL validation passed (confidence: {result.get('confidence', 0)})")
            else:
                logger.warning(f"⚠️ SQL validation failed: {result.get('issues', [])}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error validating SQL: {str(e)}")
            # Default to valid on error (don't block execution)
            return {
                "is_valid": True,
                "confidence": 0.5,
                "issues": [],
                "suggestions": None,
                "corrected_sql": None,
                "validation_error": str(e)
            }
    
    @staticmethod
    def _format_schema_summary(schema: Dict[str, Any]) -> str:
        """Format schema for validation prompt."""
        if not schema or not schema.get('columns'):
            return "No schema available"
        
        lines = ["Table: data"]
        lines.append("\nColumns:")
        
        for col in schema.get('columns', []):  # Show ALL columns (no limit)
            col_name = col.get('name', 'unknown')
            col_type = col.get('type', 'unknown')
            lines.append(f'  - "{col_name}" ({col_type})')
        
        return "\n".join(lines)
    
    @staticmethod
    async def validate_and_correct(
        sql: str,
        question: str,
        intent_type: str,
        schema: Dict[str, Any],
        max_attempts: int = 2
    ) -> Dict[str, Any]:
        """
        Validate SQL and auto-correct if issues found.
        
        Args:
            sql: Generated SQL query
            question: Original user question
            intent_type: Query intent
            schema: Dataset schema
            max_attempts: Maximum correction attempts
            
        Returns:
            Final SQL with validation status
        """
        current_sql = sql
        attempts = 0
        
        while attempts < max_attempts:
            # Validate current SQL
            validation = await SQLValidatorService.validate(
                sql=current_sql,
                question=question,
                intent_type=intent_type,
                schema=schema
            )
            
            # If valid, return
            if validation.get('is_valid'):
                return {
                    "sql": current_sql,
                    "is_valid": True,
                    "attempts": attempts,
                    "final_validation": validation
                }
            
            # If corrected SQL provided, try it
            if validation.get('corrected_sql'):
                logger.info(f"🔄 Attempting SQL correction (attempt {attempts + 1}/{max_attempts})")
                current_sql = validation['corrected_sql']
                attempts += 1
            else:
                # No correction available, return original with issues
                logger.warning(f"❌ SQL validation failed, no correction available")
                return {
                    "sql": current_sql,
                    "is_valid": False,
                    "attempts": attempts,
                    "final_validation": validation
                }
        
        # Max attempts reached
        logger.warning(f"⚠️ Max validation attempts reached ({max_attempts})")
        return {
            "sql": current_sql,
            "is_valid": False,
            "attempts": attempts,
            "final_validation": validation
        }


# Singleton instance
sql_validator = SQLValidatorService()
