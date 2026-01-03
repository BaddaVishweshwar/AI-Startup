"""
Data Quality Service

Analyzes data quality and generates warnings for:
- NULL values
- Outliers
- Row count issues
- Duplicate detection
- Overall quality score
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class DataQualityService:
    """Analyzes data quality and generates warnings."""
    
    @staticmethod
    def analyze(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Comprehensive data quality analysis.
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Quality report with score and warnings
        """
        try:
            report = {
                "timestamp": datetime.now().isoformat(),
                "row_count": len(df),
                "column_count": len(df.columns),
                "quality_score": 100,  # Start at 100, deduct for issues
                "warnings": [],
                "column_quality": {},
                "recommendations": []
            }
            
            # Check row count
            if len(df) == 0:
                report["warnings"].append("⚠️ Dataset is empty")
                report["quality_score"] = 0
                return report
            
            if len(df) < 10:
                report["warnings"].append(f"⚠️ Very small dataset ({len(df)} rows) - insights may not be reliable")
                report["quality_score"] -= 20
            
            # Analyze each column
            for col in df.columns:
                col_quality = DataQualityService._analyze_column(df[col])
                report["column_quality"][col] = col_quality
                
                # Add warnings for issues
                if col_quality["null_percentage"] > 50:
                    report["warnings"].append(f"⚠️ Column '{col}' has {col_quality['null_percentage']:.1f}% NULL values")
                    report["quality_score"] -= 10
                elif col_quality["null_percentage"] > 20:
                    report["warnings"].append(f"ℹ️ Column '{col}' has {col_quality['null_percentage']:.1f}% NULL values")
                    report["quality_score"] -= 5
                
                # Outlier warnings
                if col_quality.get("outlier_count", 0) > 0:
                    outlier_pct = (col_quality["outlier_count"] / len(df)) * 100
                    if outlier_pct > 10:
                        report["warnings"].append(f"ℹ️ Column '{col}' has {col_quality['outlier_count']} outliers ({outlier_pct:.1f}%)")
            
            # Check for duplicates
            duplicate_count = df.duplicated().sum()
            if duplicate_count > 0:
                dup_pct = (duplicate_count / len(df)) * 100
                report["warnings"].append(f"ℹ️ Found {duplicate_count} duplicate rows ({dup_pct:.1f}%)")
                report["quality_score"] -= min(10, dup_pct)
            
            # Generate recommendations
            if report["quality_score"] < 80:
                report["recommendations"].append("Consider data cleaning before analysis")
            
            if any(col_quality["null_percentage"] > 20 for col_quality in report["column_quality"].values()):
                report["recommendations"].append("Handle NULL values with COALESCE or filtering")
            
            # Ensure score doesn't go below 0
            report["quality_score"] = max(0, report["quality_score"])
            
            logger.info(f"📊 Data quality score: {report['quality_score']}/100")
            
            return report
            
        except Exception as e:
            logger.error(f"Error analyzing data quality: {str(e)}")
            return {
                "quality_score": 50,
                "warnings": [f"⚠️ Quality analysis failed: {str(e)}"],
                "error": str(e)
            }
    
    @staticmethod
    def _analyze_column(series: pd.Series) -> Dict[str, Any]:
        """Analyze a single column."""
        analysis = {
            "dtype": str(series.dtype),
            "null_count": int(series.isnull().sum()),
            "null_percentage": float((series.isnull().sum() / len(series)) * 100),
            "unique_count": int(series.nunique())
        }
        
        # Numeric column analysis
        if pd.api.types.is_numeric_dtype(series):
            non_null = series.dropna()
            if len(non_null) > 0:
                analysis.update({
                    "min": float(non_null.min()),
                    "max": float(non_null.max()),
                    "mean": float(non_null.mean()),
                    "median": float(non_null.median()),
                    "std": float(non_null.std()) if len(non_null) > 1 else 0
                })
                
                # Outlier detection using IQR method
                Q1 = non_null.quantile(0.25)
                Q3 = non_null.quantile(0.75)
                IQR = Q3 - Q1
                
                outliers = non_null[(non_null < Q1 - 1.5 * IQR) | (non_null > Q3 + 1.5 * IQR)]
                analysis["outlier_count"] = len(outliers)
        
        return analysis
    
    @staticmethod
    def format_warnings_for_user(report: Dict[str, Any]) -> str:
        """Format quality warnings for user display."""
        if not report.get("warnings"):
            return "✅ Data quality is good"
        
        lines = [f"📊 Data Quality Score: {report['quality_score']}/100"]
        lines.append("\nWarnings:")
        for warning in report["warnings"]:
            lines.append(f"  {warning}")
        
        if report.get("recommendations"):
            lines.append("\nRecommendations:")
            for rec in report["recommendations"]:
                lines.append(f"  • {rec}")
        
        return "\n".join(lines)


# Singleton instance
data_quality_service = DataQualityService()
