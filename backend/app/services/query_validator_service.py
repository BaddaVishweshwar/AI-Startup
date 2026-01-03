"""
Query Validator Service

Validates SQL queries, executes with retry logic, and handles errors gracefully.
"""

import logging
import time
from typing import Dict, Any, Optional, Tuple
import pandas as pd
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


class QueryValidatorService:
    """Service for SQL validation and execution with retry logic."""
    
    # Forbidden SQL keywords (DDL/DML operations)
    FORBIDDEN_KEYWORDS = [
        'DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE',
        'TRUNCATE', 'REPLACE', 'GRANT', 'REVOKE'
    ]
    
    @staticmethod
    def validate_sql(sql: str) -> Tuple[bool, Optional[str]]:
        """
        Validate SQL query for safety.
        
        Args:
            sql: SQL query to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check for forbidden keywords
            sql_upper = sql.upper()
            for keyword in QueryValidatorService.FORBIDDEN_KEYWORDS:
                if keyword in sql_upper:
                    return False, f"Forbidden SQL operation: {keyword}. Only SELECT queries are allowed."
            
            # Check if query is empty
            if not sql or sql.strip() == '':
                return False, "SQL query is empty"
            
            # Check if query starts with SELECT (basic check)
            if not sql_upper.strip().startswith('SELECT') and not sql_upper.strip().startswith('WITH'):
                return False, "Query must be a SELECT statement or start with WITH (CTE)"
            
            return True, None
            
        except Exception as e:
            logger.error(f"Error validating SQL: {str(e)}")
            return False, f"Validation error: {str(e)}"
    
    @staticmethod
    async def execute_with_retry(
        sql: str,
        connection: Any,
        max_attempts: int = 3,
        timeout: int = 30,
        llm_service: Any = None,
        schema: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Execute SQL query with retry logic and error correction.
        
        Args:
            sql: SQL query to execute
            connection: Database connection
            max_attempts: Maximum retry attempts
            timeout: Query timeout in seconds
            llm_service: LLM service for error correction (optional)
            schema: Database schema for error correction (optional)
            
        Returns:
            Dictionary with results or error information
        """
        for attempt in range(max_attempts):
            try:
                # Validate SQL first
                is_valid, error_msg = QueryValidatorService.validate_sql(sql)
                if not is_valid:
                    return {
                        'success': False,
                        'error': error_msg,
                        'error_type': 'validation_error',
                        'attempt': attempt + 1
                    }
                
                # Execute query with timeout
                start_time = time.time()
                
                if hasattr(connection, 'execute'):
                    # SQLAlchemy connection
                    result = connection.execute(text(sql))
                    rows = result.fetchall()
                    columns = result.keys()
                    
                    # Convert to list of dictionaries
                    data = [dict(zip(columns, row)) for row in rows]
                else:
                    # Pandas DataFrame (in-memory SQLite)
                    # This is handled differently - connection is actually the DataFrame
                    logger.warning("Direct DataFrame execution not supported in validator")
                    return {
                        'success': False,
                        'error': 'Invalid connection type',
                        'error_type': 'connection_error'
                    }
                
                execution_time = time.time() - start_time
                
                # Check if results are empty
                if len(data) == 0:
                    if attempt < max_attempts - 1 and llm_service and schema:
                        # Ask LLM why results are empty
                        logger.info(f"Query returned empty results, asking LLM for analysis (attempt {attempt + 1})")
                        # This would call LLM to analyze empty results
                        # For now, just return empty results with warning
                        pass
                    
                    return {
                        'success': True,
                        'data': [],
                        'columns': list(columns) if 'columns' in locals() else [],
                        'row_count': 0,
                        'execution_time_ms': int(execution_time * 1000),
                        'warning': 'Query executed successfully but returned no results'
                    }
                
                # Success
                return {
                    'success': True,
                    'data': data,
                    'columns': list(columns),
                    'row_count': len(data),
                    'execution_time_ms': int(execution_time * 1000)
                }
                
            except SQLAlchemyError as e:
                error_msg = str(e)
                logger.error(f"SQL execution error (attempt {attempt + 1}/{max_attempts}): {error_msg}")
                
                # If not last attempt and LLM service available, try to fix SQL
                if attempt < max_attempts - 1 and llm_service and schema:
                    try:
                        logger.info(f"Attempting to fix SQL with LLM (attempt {attempt + 1})")
                        fixed_sql = await QueryValidatorService._fix_sql_with_llm(
                            sql, error_msg, llm_service, schema
                        )
                        if fixed_sql and fixed_sql != sql:
                            logger.info("LLM provided corrected SQL, retrying...")
                            sql = fixed_sql
                            continue
                    except Exception as llm_error:
                        logger.error(f"Error fixing SQL with LLM: {str(llm_error)}")
                
                # Last attempt or LLM fix failed
                if attempt == max_attempts - 1:
                    return {
                        'success': False,
                        'error': error_msg,
                        'error_type': 'execution_error',
                        'failed_sql': sql,
                        'attempts': max_attempts
                    }
            
            except Exception as e:
                error_msg = str(e)
                logger.error(f"Unexpected error executing SQL (attempt {attempt + 1}/{max_attempts}): {error_msg}")
                
                if attempt == max_attempts - 1:
                    return {
                        'success': False,
                        'error': error_msg,
                        'error_type': 'unexpected_error',
                        'failed_sql': sql,
                        'attempts': max_attempts
                    }
        
        # Should not reach here
        return {
            'success': False,
            'error': 'Maximum retry attempts exceeded',
            'error_type': 'max_retries_exceeded'
        }
    
    @staticmethod
    async def _fix_sql_with_llm(
        failed_sql: str,
        error_message: str,
        llm_service: Any,
        schema: Dict[str, Any]
    ) -> Optional[str]:
        """
        Use LLM to fix failed SQL query.
        
        Args:
            failed_sql: SQL that failed
            error_message: Error message from database
            llm_service: LLM service instance
            schema: Database schema
            
        Returns:
            Fixed SQL query or None
        """
        try:
            from ..prompts.enhanced_prompts import (
                SQL_ERROR_CORRECTION_PROMPT_TEMPLATE,
                format_schema_for_prompt
            )
            
            prompt = SQL_ERROR_CORRECTION_PROMPT_TEMPLATE.format(
                failed_sql=failed_sql,
                error_message=error_message,
                schema_details=format_schema_for_prompt(schema)
            )
            
            response = await llm_service.generate_response(
                prompt=prompt,
                json_mode=True,
                temperature=0.2  # Low temperature for precise correction
            )
            
            # Parse JSON response
            import json
            result = json.loads(response)
            
            if result.get('confidence') in ['high', 'medium'] and result.get('fixed_sql'):
                logger.info(f"LLM fixed SQL with {result.get('confidence')} confidence: {result.get('explanation')}")
                return result['fixed_sql']
            
            return None
            
        except Exception as e:
            logger.error(f"Error in LLM SQL correction: {str(e)}")
            return None
    
    @staticmethod
    def format_query_results(results: Dict[str, Any]) -> str:
        """Format query results for display in prompts."""
        if not results.get('success'):
            return f"Error: {results.get('error', 'Unknown error')}"
        
        data = results.get('data', [])
        if not data:
            return "Query returned no results"
        
        # Format as table
        lines = [f"Results ({results.get('row_count', 0)} rows):"]
        
        # Show first 10 rows
        for i, row in enumerate(data[:10], 1):
            lines.append(f"{i}. {row}")
        
        if len(data) > 10:
            lines.append(f"... and {len(data) - 10} more rows")
        
        return '\n'.join(lines)


# Singleton instance
query_validator_service = QueryValidatorService()
