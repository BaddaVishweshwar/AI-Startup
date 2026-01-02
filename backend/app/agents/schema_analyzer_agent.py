"""
Schema Analyzer Agent

Performs deep schema analysis using deterministic pandas operations.
NO LLM involvement - pure computation for accuracy.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List
import logging
from . import SchemaAnalysis, ColumnMetadata, ColumnType

logger = logging.getLogger(__name__)


class SchemaAnalyzerAgent:
    """
    Analyzes dataset schema to extract:
    - Column types (numeric, categorical, datetime, boolean, text)
    - Missing value percentages
    - Cardinality (unique values)
    - Potential relationships
    - Aggregation feasibility
    
    This is DETERMINISTIC - no LLM calls, only pandas operations.
    """
    
    @staticmethod
    def analyze(df: pd.DataFrame, schema: Dict[str, str]) -> SchemaAnalysis:
        """
        Perform comprehensive schema analysis
        
        Args:
            df: DataFrame to analyze
            schema: Basic schema dict from data service
            
        Returns:
            SchemaAnalysis with detailed metadata
        """
        logger.info(f"🔍 Analyzing schema for {len(df)} rows, {len(df.columns)} columns")
        
        columns_metadata = {}
        numeric_cols = []
        categorical_cols = []
        datetime_cols = []
        
        for col in df.columns:
            metadata = SchemaAnalyzerAgent._analyze_column(df, col)
            columns_metadata[col] = metadata
            
            # Categorize columns
            if metadata.type == ColumnType.NUMERIC:
                numeric_cols.append(col)
            elif metadata.type == ColumnType.CATEGORICAL:
                categorical_cols.append(col)
            elif metadata.type == ColumnType.DATETIME:
                datetime_cols.append(col)
        
        # Detect potential relationships (foreign keys)
        relationships = SchemaAnalyzerAgent._detect_relationships(df, columns_metadata)
        
        # Calculate data quality score
        quality_score = SchemaAnalyzerAgent._calculate_quality_score(columns_metadata)
        
        analysis = SchemaAnalysis(
            columns=columns_metadata,
            total_rows=len(df),
            numeric_columns=numeric_cols,
            categorical_columns=categorical_cols,
            datetime_columns=datetime_cols,
            potential_relationships=relationships,
            data_quality_score=quality_score
        )
        
        logger.info(f"✅ Schema analysis complete: {len(numeric_cols)} numeric, "
                   f"{len(categorical_cols)} categorical, {len(datetime_cols)} datetime columns")
        
        return analysis
    
    @staticmethod
    def _analyze_column(df: pd.DataFrame, col: str) -> ColumnMetadata:
        """Analyze a single column"""
        series = df[col]
        total_count = len(series)
        
        # Missing values
        missing_count = series.isna().sum()
        missing_pct = (missing_count / total_count * 100) if total_count > 0 else 0
        
        # Unique values
        unique_count = series.nunique()
        
        # Determine column type
        col_type = SchemaAnalyzerAgent._detect_column_type(series)
        
        # Sample values (non-null)
        sample_values = series.dropna().head(5).tolist()
        
        # Determine if aggregatable and groupable
        is_aggregatable = col_type == ColumnType.NUMERIC
        is_groupable = col_type in [ColumnType.CATEGORICAL, ColumnType.DATETIME, ColumnType.BOOLEAN]
        
        # Calculate stats based on type
        min_val, max_val, avg_val, std_val = None, None, None, None
        
        if col_type == ColumnType.NUMERIC:
            try:
                # Ensure we strictly operate on numeric data (exclude NaNs properly)
                clean_series = series.dropna()
                if not clean_series.empty:
                    min_val = float(clean_series.min())
                    max_val = float(clean_series.max())
                    avg_val = float(clean_series.mean())
                    std_val = float(clean_series.std())
            except Exception as e:
                logger.warning(f"Failed to calc numeric stats for {col}: {e}")
        
        elif col_type == ColumnType.DATETIME:
            try:
                clean_series = series.dropna()
                if not clean_series.empty:
                    # Convert to datetime if not already (safeguard)
                    if not pd.api.types.is_datetime64_any_dtype(clean_series):
                         clean_series = pd.to_datetime(clean_series, errors='coerce').dropna()
                    
                    if not clean_series.empty:
                        min_val = clean_series.min()
                        max_val = clean_series.max()
                        # Convert to string for JSON serialization
                        min_val = min_val.isoformat() if hasattr(min_val, 'isoformat') else str(min_val)
                        max_val = max_val.isoformat() if hasattr(max_val, 'isoformat') else str(max_val)
            except Exception as e:
                logger.warning(f"Failed to calc datetime stats for {col}: {e}")

        
        # Calculate top values for categorical or low-cardinality columns
        top_values = []
        if col_type in [ColumnType.CATEGORICAL, ColumnType.BOOLEAN] or (col_type == ColumnType.NUMERIC and unique_count <= 10):
            try:
                value_counts = series.value_counts().head(5)
                for value, count in value_counts.items():
                    percentage = (count / total_count * 100) if total_count > 0 else 0
                    top_values.append({
                        "value": str(value),  # Convert to string for JSON serialization
                        "count": int(count),
                        "percentage": round(percentage, 2)
                    })
            except Exception as e:
                logger.warning(f"Failed to calc top values for {col}: {e}")
        
        return ColumnMetadata(
            name=col,
            type=col_type,
            missing_percentage=round(missing_pct, 2),
            unique_count=unique_count,
            sample_values=sample_values,
            is_aggregatable=is_aggregatable,
            is_groupable=is_groupable,
            min_value=min_val,
            max_value=max_val,
            avg_value=avg_val,
            std_dev=std_val,
            top_values=top_values
        )
    
    @staticmethod
    def _detect_column_type(series: pd.Series) -> ColumnType:
        """Detect the semantic type of a column"""
        dtype = series.dtype
        
        # Datetime
        if pd.api.types.is_datetime64_any_dtype(dtype):
            return ColumnType.DATETIME
        
        # Try to parse as datetime if string
        if dtype == 'object':
            # Sample a few non-null values
            sample = series.dropna().head(10)
            if len(sample) > 0:
                try:
                    pd.to_datetime(sample)
                    return ColumnType.DATETIME
                except:
                    pass
        
        # Boolean
        if pd.api.types.is_bool_dtype(dtype):
            return ColumnType.BOOLEAN
        
        # Check if object column contains only True/False/None
        if dtype == 'object':
            unique_vals = set(series.dropna().unique())
            if unique_vals.issubset({True, False, 'True', 'False', 'true', 'false', 1, 0}):
                return ColumnType.BOOLEAN
        
        # Numeric
        if pd.api.types.is_numeric_dtype(dtype):
            return ColumnType.NUMERIC
        
        # Categorical (low cardinality string)
        if dtype == 'object':
            unique_count = series.nunique()
            total_count = len(series)
            cardinality_ratio = unique_count / total_count if total_count > 0 else 0
            
            # If less than 50% unique values and less than 100 unique, treat as categorical
            if cardinality_ratio < 0.5 and unique_count < 100:
                return ColumnType.CATEGORICAL
        
        # Default to TEXT for high-cardinality strings
        return ColumnType.TEXT
    
    @staticmethod
    def _detect_relationships(df: pd.DataFrame, columns_metadata: Dict[str, ColumnMetadata]) -> List[Dict[str, str]]:
        """
        Detect potential foreign key relationships
        
        Simple heuristic: if column A's values are a subset of column B's values,
        A might reference B
        """
        relationships = []
        
        # Only check categorical columns with reasonable cardinality
        categorical_cols = [
            col for col, meta in columns_metadata.items()
            if meta.type == ColumnType.CATEGORICAL and 5 < meta.unique_count < 1000
        ]
        
        for i, col_a in enumerate(categorical_cols):
            for col_b in categorical_cols[i+1:]:
                values_a = set(df[col_a].dropna().unique())
                values_b = set(df[col_b].dropna().unique())
                
                # Check if A is subset of B
                if values_a.issubset(values_b) and len(values_a) > 0:
                    relationships.append({
                        "from_column": col_a,
                        "to_column": col_b,
                        "relationship_type": "potential_foreign_key"
                    })
                # Check if B is subset of A
                elif values_b.issubset(values_a) and len(values_b) > 0:
                    relationships.append({
                        "from_column": col_b,
                        "to_column": col_a,
                        "relationship_type": "potential_foreign_key"
                    })
        
        return relationships[:5]  # Limit to top 5 to avoid noise
    
    @staticmethod
    def _calculate_quality_score(columns_metadata: Dict[str, ColumnMetadata]) -> float:
        """
        Calculate overall data quality score (0-1)
        
        Factors:
        - Missing value percentage
        - Column type detection success
        """
        if not columns_metadata:
            return 0.0
        
        total_missing_pct = sum(meta.missing_percentage for meta in columns_metadata.values())
        avg_missing_pct = total_missing_pct / len(columns_metadata)
        
        # Score: 1.0 = no missing values, 0.0 = all missing
        quality_score = max(0.0, 1.0 - (avg_missing_pct / 100))
        
        return round(quality_score, 2)
    
    @staticmethod
    def get_enriched_schema_prompt(schema_analysis: 'SchemaAnalysis', df: pd.DataFrame = None) -> str:
        """
        Generate a rich, multi-line schema description for LLM prompts.
        
        Returns formatted string with column details, stats, samples, and top values.
        """
        lines = ["**SCHEMA WITH FULL CONTEXT**", ""]
        lines.append(f"Dataset: {schema_analysis.total_rows} rows, {len(schema_analysis.columns)} columns")
        lines.append(f"Data Quality Score: {schema_analysis.data_quality_score}/1.0")
        lines.append("")
        
        for col_name, col_meta in schema_analysis.columns.items():
            lines.append(f"Column: {col_name} ({col_meta.type.value})")
            
            # Numeric columns
            if col_meta.type.value in ['NUMERIC']:
                if col_meta.min_value is not None and col_meta.max_value is not None:
                    lines.append(f"  - Range: {col_meta.min_value} to {col_meta.max_value}")
                if col_meta.avg_value is not None:
                    std_str = f" ± {col_meta.std_dev:.2f}" if col_meta.std_dev else ""
                    lines.append(f"  - Average: {col_meta.avg_value:.2f}{std_str}")
            
            # Datetime columns
            elif col_meta.type.value == 'DATETIME':
                if col_meta.min_value and col_meta.max_value:
                    lines.append(f"  - Date Range: {col_meta.min_value} to {col_meta.max_value}")
            
            # Missing and uniqueness (all types)
            lines.append(f"  - Missing: {col_meta.missing_percentage}%")
            lines.append(f"  - Distinct values: {col_meta.unique_count}")
            
            # Top values for categorical/low-cardinality
            if col_meta.top_values:
                lines.append(f"  - Top values:")
                for top_val in col_meta.top_values[:5]:
                    lines.append(f"    • {top_val['value']}: {top_val['count']} ({top_val['percentage']}%)")
            
            # Sample values
            if col_meta.sample_values:
                sample_str = ", ".join(str(v)[:50] for v in col_meta.sample_values[:5])  # Limit string length
                lines.append(f"  - Sample values: [{sample_str}]")
            
            lines.append("")
        
        return "\n".join(lines)



# Singleton instance
schema_analyzer = SchemaAnalyzerAgent()
