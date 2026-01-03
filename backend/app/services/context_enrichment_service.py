"""
Context Enrichment Service

Enriches schema with comprehensive context including sample data, column statistics,
and business logic patterns for enhanced LLM prompting.
"""

import pandas as pd
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy import text
from datetime import datetime

logger = logging.getLogger(__name__)


class ContextEnrichmentService:
    """Service to enrich schema with comprehensive context for LLM prompts."""
    
    @staticmethod
    def enrich_schema_context(
        df: pd.DataFrame,
        table_name: str = "data",
        connection: Any = None
    ) -> Dict[str, Any]:
        """
        Enrich schema with comprehensive context.
        
        Args:
            df: DataFrame to analyze
            table_name: Name of the table
            connection: Database connection (optional)
            
        Returns:
            Enriched schema dictionary with samples, statistics, and patterns
        """
        try:
            schema = {
                'table_name': table_name,
                'columns': [],
                'row_count': len(df),
                'sample_data': [],
                'column_statistics': {},
                'business_patterns': []
            }
            
            # Get sample data (first 5 rows)
            schema['sample_data'] = ContextEnrichmentService._get_sample_data(df)
            
            # Analyze each column
            for col in df.columns:
                col_info = ContextEnrichmentService._analyze_column(df, col)
                schema['columns'].append(col_info)
                
                # Get detailed statistics for this column
                stats = ContextEnrichmentService._get_column_statistics(df, col)
                schema['column_statistics'][col] = stats
            
            # Detect business logic patterns
            schema['business_patterns'] = ContextEnrichmentService._detect_business_patterns(df)
            
            # Detect date range if temporal columns exist
            date_cols = [col for col in df.columns if pd.api.types.is_datetime64_any_dtype(df[col])]
            if date_cols:
                schema['date_range'] = ContextEnrichmentService._get_date_range(df, date_cols[0])
            
            logger.info(f"Enriched schema for {table_name} with {len(schema['columns'])} columns")
            return schema
            
        except Exception as e:
            logger.error(f"Error enriching schema context: {str(e)}")
            # Return basic schema on error
            return {
                'table_name': table_name,
                'columns': [{'name': col, 'type': str(df[col].dtype)} for col in df.columns],
                'row_count': len(df)
            }
    
    @staticmethod
    def _get_sample_data(df: pd.DataFrame, limit: int = 5) -> List[Dict[str, Any]]:
        """Get sample rows from DataFrame."""
        try:
            sample_df = df.head(limit)
            # Convert to list of dictionaries, handling NaN and datetime
            samples = []
            for _, row in sample_df.iterrows():
                row_dict = {}
                for col, val in row.items():
                    if pd.isna(val):
                        row_dict[col] = None
                    elif isinstance(val, (pd.Timestamp, datetime)):
                        row_dict[col] = val.strftime('%Y-%m-%d %H:%M:%S')
                    elif isinstance(val, (int, float, str, bool)):
                        row_dict[col] = val
                    else:
                        row_dict[col] = str(val)
                samples.append(row_dict)
            return samples
        except Exception as e:
            logger.error(f"Error getting sample data: {str(e)}")
            return []
    
    @staticmethod
    def _analyze_column(df: pd.DataFrame, col: str) -> Dict[str, Any]:
        """Analyze a single column and return metadata."""
        try:
            col_data = df[col]
            
            # Infer data type
            dtype = str(col_data.dtype)
            inferred_type = ContextEnrichmentService._infer_semantic_type(col_data)
            
            # Get sample values (non-null, unique)
            sample_values = col_data.dropna().unique()[:10].tolist()
            
            # Handle datetime conversion for samples
            if pd.api.types.is_datetime64_any_dtype(col_data):
                sample_values = [v.strftime('%Y-%m-%d') if isinstance(v, pd.Timestamp) else str(v) 
                               for v in sample_values]
            
            return {
                'name': col,
                'type': dtype,
                'semantic_type': inferred_type,
                'sample_values': sample_values,
                'nullable': bool(col_data.isna().any())
            }
        except Exception as e:
            logger.error(f"Error analyzing column {col}: {str(e)}")
            return {'name': col, 'type': 'unknown'}
    
    @staticmethod
    def _infer_semantic_type(series: pd.Series) -> str:
        """Infer semantic type of a column."""
        if pd.api.types.is_datetime64_any_dtype(series):
            return 'DATE'
        elif pd.api.types.is_numeric_dtype(series):
            # Check if it's an ID column
            if series.name and ('id' in series.name.lower() or series.name.lower().endswith('_id')):
                return 'ID'
            # Check if it's a boolean (0/1)
            if series.dropna().isin([0, 1]).all():
                return 'BOOLEAN'
            # Check if it's an integer
            if pd.api.types.is_integer_dtype(series):
                return 'INTEGER'
            return 'NUMERIC'
        elif pd.api.types.is_string_dtype(series) or pd.api.types.is_object_dtype(series):
            # Check if it's a category (low cardinality)
            unique_ratio = series.nunique() / len(series) if len(series) > 0 else 0
            if unique_ratio < 0.05:  # Less than 5% unique values
                return 'CATEGORY'
            return 'TEXT'
        else:
            return 'UNKNOWN'
    
    @staticmethod
    def _get_column_statistics(df: pd.DataFrame, col: str) -> Dict[str, Any]:
        """Get detailed statistics for a column."""
        try:
            col_data = df[col]
            stats = {}
            
            # Common statistics
            stats['distinct_count'] = int(col_data.nunique())
            stats['null_count'] = int(col_data.isna().sum())
            stats['null_percentage'] = float((col_data.isna().sum() / len(col_data)) * 100) if len(col_data) > 0 else 0
            
            # Numeric statistics
            if pd.api.types.is_numeric_dtype(col_data):
                stats['min_value'] = float(col_data.min()) if not col_data.isna().all() else None
                stats['max_value'] = float(col_data.max()) if not col_data.isna().all() else None
                stats['mean_value'] = float(col_data.mean()) if not col_data.isna().all() else None
                stats['median_value'] = float(col_data.median()) if not col_data.isna().all() else None
            
            # Categorical statistics (top values)
            if stats['distinct_count'] < 100:  # Only for low cardinality
                value_counts = col_data.value_counts().head(10)
                stats['top_values'] = [
                    {'value': str(val), 'count': int(count)} 
                    for val, count in value_counts.items()
                ]
            
            # Date statistics
            if pd.api.types.is_datetime64_any_dtype(col_data):
                if not col_data.isna().all():
                    stats['min_date'] = col_data.min().strftime('%Y-%m-%d')
                    stats['max_date'] = col_data.max().strftime('%Y-%m-%d')
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting statistics for column {col}: {str(e)}")
            return {}
    
    @staticmethod
    def _detect_business_patterns(df: pd.DataFrame) -> List[str]:
        """Detect common business logic patterns in the data."""
        patterns = []
        
        try:
            # Pattern 1: Revenue = Price × Quantity
            if all(col in df.columns for col in ['price', 'quantity', 'revenue']):
                patterns.append("Revenue appears to be calculated as price × quantity")
            
            # Pattern 2: Total = Sum of parts
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            if 'total' in [c.lower() for c in numeric_cols]:
                patterns.append("Total column detected - may be sum of other numeric columns")
            
            # Pattern 3: Date-based columns
            date_cols = [col for col in df.columns if pd.api.types.is_datetime64_any_dtype(df[col])]
            if len(date_cols) > 1:
                patterns.append(f"Multiple date columns detected: {', '.join(date_cols)}")
            
            # Pattern 4: ID columns
            id_cols = [col for col in df.columns if 'id' in col.lower()]
            if id_cols:
                patterns.append(f"ID columns detected: {', '.join(id_cols)} - likely foreign keys")
            
            # Pattern 5: Category columns
            category_cols = []
            for col in df.columns:
                if pd.api.types.is_object_dtype(df[col]) or pd.api.types.is_string_dtype(df[col]):
                    unique_ratio = df[col].nunique() / len(df) if len(df) > 0 else 0
                    if unique_ratio < 0.05:
                        category_cols.append(col)
            
            if category_cols:
                patterns.append(f"Category columns detected: {', '.join(category_cols)}")
            
        except Exception as e:
            logger.error(f"Error detecting business patterns: {str(e)}")
        
        return patterns
    
    @staticmethod
    def _get_date_range(df: pd.DataFrame, date_col: str) -> Dict[str, str]:
        """Get date range for a temporal column."""
        try:
            col_data = df[date_col].dropna()
            if len(col_data) > 0:
                return {
                    'min': col_data.min().strftime('%Y-%m-%d'),
                    'max': col_data.max().strftime('%Y-%m-%d'),
                    'column': date_col
                }
        except Exception as e:
            logger.error(f"Error getting date range: {str(e)}")
        
        return {}


# Singleton instance
context_enrichment_service = ContextEnrichmentService()
