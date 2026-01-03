"""
Analytics Service V3 - Preview Demo

This demonstrates the enhanced multi-agent pipeline structure and output format.
"""

# Sample response from Analytics Service V3
sample_response = {
    "query": "What are the top 10 products by revenue?",
    "success": True,
    
    # Step 1: Understanding
    "understanding": "User wants to identify the highest-revenue products to understand which items are driving the most sales",
    
    # Step 2: Approach
    "approach": "Aggregate total revenue by product, rank them in descending order, and return the top 10 performers with supporting metrics",
    
    # Step 3: Exploratory Steps (2-3 preliminary queries)
    "exploratory_steps": [
        {
            "question": "What is the overall data volume and date range?",
            "sql": "SELECT COUNT(*) as total_records, MIN(date) as earliest_date, MAX(date) as latest_date FROM data",
            "finding": "Dataset contains 5,000 sales records spanning from 2024-01-01 to 2024-12-31",
            "data_preview": [
                {"total_records": 5000, "earliest_date": "2024-01-01", "latest_date": "2024-12-31"}
            ]
        },
        {
            "question": "How many distinct products exist in the dataset?",
            "sql": "SELECT COUNT(DISTINCT product) as product_count FROM data",
            "finding": "Dataset contains 150 unique products across all categories",
            "data_preview": [
                {"product_count": 150}
            ]
        },
        {
            "question": "What is the revenue distribution across products?",
            "sql": "SELECT MIN(revenue) as min_rev, MAX(revenue) as max_rev, AVG(revenue) as avg_rev FROM data",
            "finding": "Revenue ranges from $10 to $9,999 per transaction, with an average of $450",
            "data_preview": [
                {"min_rev": 10.0, "max_rev": 9999.99, "avg_rev": 450.25}
            ]
        }
    ],
    
    # Step 4: Main SQL Query
    "sql_query": {
        "query": """-- Top 10 Products by Revenue Analysis
WITH product_revenue AS (
  SELECT 
    product,
    SUM(revenue) as total_revenue,
    COUNT(*) as order_count,
    AVG(revenue) as avg_order_value,
    SUM(quantity) as total_units_sold
  FROM data
  WHERE revenue IS NOT NULL
  GROUP BY product
)
SELECT 
  product,
  ROUND(total_revenue, 2) as total_revenue,
  order_count,
  ROUND(avg_order_value, 2) as avg_order_value,
  total_units_sold,
  ROUND(total_revenue * 100.0 / SUM(total_revenue) OVER (), 2) as revenue_share_pct
FROM product_revenue
ORDER BY total_revenue DESC
LIMIT 10""",
        "explanation": "This query uses a CTE to aggregate revenue metrics by product, then calculates each product's share of total revenue and ranks them. It includes supporting metrics like order count and average order value for deeper insights.",
        "complexity": "medium"
    },
    
    # Step 5: Query Results
    "results": {
        "data": [
            {"product": "Premium Widget Pro", "total_revenue": 1250000.00, "order_count": 2500, "avg_order_value": 500.00, "total_units_sold": 12500, "revenue_share_pct": 26.04},
            {"product": "Enterprise Suite", "total_revenue": 980000.00, "order_count": 1400, "avg_order_value": 700.00, "total_units_sold": 7000, "revenue_share_pct": 20.42},
            {"product": "Deluxe Package", "total_revenue": 750000.00, "order_count": 3000, "avg_order_value": 250.00, "total_units_sold": 15000, "revenue_share_pct": 15.63},
            {"product": "Professional Edition", "total_revenue": 620000.00, "order_count": 1550, "avg_order_value": 400.00, "total_units_sold": 9300, "revenue_share_pct": 12.92},
            {"product": "Standard Widget", "total_revenue": 450000.00, "order_count": 4500, "avg_order_value": 100.00, "total_units_sold": 22500, "revenue_share_pct": 9.38},
            {"product": "Advanced Kit", "total_revenue": 380000.00, "order_count": 950, "avg_order_value": 400.00, "total_units_sold": 5700, "revenue_share_pct": 7.92},
            {"product": "Basic Bundle", "total_revenue": 180000.00, "order_count": 3600, "avg_order_value": 50.00, "total_units_sold": 18000, "revenue_share_pct": 3.75},
            {"product": "Starter Pack", "total_revenue": 95000.00, "order_count": 1900, "avg_order_value": 50.00, "total_units_sold": 9500, "revenue_share_pct": 1.98},
            {"product": "Economy Option", "total_revenue": 60000.00, "order_count": 2000, "avg_order_value": 30.00, "total_units_sold": 10000, "revenue_share_pct": 1.25},
            {"product": "Value Pack", "total_revenue": 35000.00, "order_count": 1400, "avg_order_value": 25.00, "total_units_sold": 7000, "revenue_share_pct": 0.73}
        ],
        "columns": ["product", "total_revenue", "order_count", "avg_order_value", "total_units_sold", "revenue_share_pct"],
        "row_count": 10,
        "execution_time_ms": 45
    },
    
    # Step 6: Visualizations (2-3 charts)
    "visualizations": [
        {
            "type": "bar",
            "config": {
                "x_axis": "product",
                "y_axis": "total_revenue",
                "title": "Top 10 Products by Total Revenue",
                "x_label": "Product",
                "y_label": "Revenue ($)",
                "color_scheme": "blue",
                "sort": "descending"
            },
            "purpose": "Primary visualization showing revenue ranking"
        },
        {
            "type": "metric_cards",
            "config": {
                "metrics": [
                    {"label": "Total Revenue (Top 10)", "value": "$4,800,000", "trend": "+15%"},
                    {"label": "Average Order Value", "value": "$345", "trend": "+8%"},
                    {"label": "Top Product Share", "value": "26%", "trend": "stable"}
                ]
            },
            "purpose": "Key metrics summary"
        },
        {
            "type": "pie",
            "config": {
                "values": "revenue_share_pct",
                "labels": "product",
                "title": "Revenue Distribution - Top 10 Products",
                "color_scheme": "multi"
            },
            "purpose": "Show proportional revenue contribution"
        }
    ],
    "primary_visualization": 0,
    
    # Step 7: Executive Insights
    "insights": {
        "summary": "The top 10 products account for 67% of total revenue ($4.8M out of $7.2M), with Premium Widget Pro alone generating 26% of all sales. This reveals a highly concentrated revenue distribution with significant dependency on premium-tier products.",
        
        "key_findings": [
            "Premium Widget Pro dominates with $1.25M in revenue (26% market share) despite having only 2,500 orders",
            "Top 3 products (Premium Widget Pro, Enterprise Suite, Deluxe Package) generate 62% of total revenue",
            "Premium products ($400+ avg order value) account for 5 of the top 10 positions",
            "High-volume, low-price products (Standard Widget, Basic Bundle) rank in middle positions despite 4,500+ orders each",
            "Significant revenue concentration: top 10 products represent only 6.7% of product catalog but drive 67% of revenue"
        ],
        
        "detailed_analysis": "The data reveals a classic Pareto distribution where a small subset of premium products drives the majority of revenue. Premium Widget Pro stands out with an exceptional average order value of $500, indicating strong market positioning in the premium segment. The Enterprise Suite follows with even higher per-order value ($700) but lower volume, suggesting it targets a more selective customer base.\n\nInterestingly, while Standard Widget has the highest order count (4,500), it ranks only 5th in revenue due to its lower price point ($100 avg). This suggests a bifurcated market strategy is working: premium products for high-value customers and volume products for price-sensitive segments.\n\nThe revenue concentration presents both opportunity and risk. The top 3 products generating 62% of revenue indicates strong product-market fit in the premium segment, but also creates dependency risk. Any disruption to these key products could significantly impact overall business performance.",
        
        "recommendations": "1. **Protect Premium Position**: Invest heavily in maintaining quality and innovation for Premium Widget Pro and Enterprise Suite, as they are critical revenue drivers. Consider premium customer success programs to ensure retention.\n\n2. **Reduce Concentration Risk**: Develop 2-3 new products in the $300-600 price range to diversify revenue sources while maintaining premium positioning. Target the gap between Deluxe Package ($250) and Professional Edition ($400).\n\n3. **Optimize Volume Products**: Analyze why Standard Widget and Basic Bundle have high order counts but lower revenue contribution. Consider strategic price increases or bundling strategies to improve margins without sacrificing volume.\n\n4. **Expand Premium Portfolio**: Given the success of high-value products, explore opportunities to upsell existing customers from mid-tier to premium offerings through targeted campaigns highlighting ROI and advanced features."
    },
    
    # Step 8: Metadata
    "metadata": {
        "total_execution_time_ms": 3250,
        "exploratory_queries_count": 3,
        "visualizations_count": 3,
        "schema_columns": 5
    },
    
    "intent": {
        "primary_intent": "ranking",
        "confidence": 0.95,
        "requires_aggregation": True,
        "requires_time_series": False,
        "requires_comparison": False
    }
}


def print_preview():
    """Print a formatted preview of the Analytics Service V3 response."""
    
    print("\n" + "="*100)
    print("ANALYTICS SERVICE V3 - ENHANCED MULTI-AGENT PIPELINE PREVIEW")
    print("="*100)
    
    print(f"\n📝 USER QUERY: {sample_response['query']}")
    print(f"✅ STATUS: {'SUCCESS' if sample_response['success'] else 'FAILED'}")
    
    print("\n" + "-"*100)
    print("STAGE 1: UNDERSTANDING")
    print("-"*100)
    print(f"💡 {sample_response['understanding']}")
    
    print("\n" + "-"*100)
    print("STAGE 2: APPROACH")
    print("-"*100)
    print(f"🎯 {sample_response['approach']}")
    
    print("\n" + "-"*100)
    print("STAGE 3: EXPLORATORY ANALYSIS (3 preliminary queries)")
    print("-"*100)
    for i, step in enumerate(sample_response['exploratory_steps'], 1):
        print(f"\n{i}. {step['question']}")
        print(f"   SQL: {step['sql']}")
        print(f"   📊 Finding: {step['finding']}")
    
    print("\n" + "-"*100)
    print("STAGE 4: MAIN SQL QUERY")
    print("-"*100)
    print(sample_response['sql_query']['query'])
    print(f"\n💬 Explanation: {sample_response['sql_query']['explanation']}")
    print(f"⚡ Complexity: {sample_response['sql_query']['complexity']}")
    
    print("\n" + "-"*100)
    print("STAGE 5: QUERY RESULTS")
    print("-"*100)
    print(f"📊 Rows returned: {sample_response['results']['row_count']}")
    print(f"📋 Columns: {', '.join(sample_response['results']['columns'])}")
    print(f"⏱️  Execution time: {sample_response['results']['execution_time_ms']}ms")
    print("\nTop 3 Results:")
    for i, row in enumerate(sample_response['results']['data'][:3], 1):
        print(f"  {i}. {row['product']}: ${row['total_revenue']:,.2f} ({row['revenue_share_pct']}% share)")
    
    print("\n" + "-"*100)
    print("STAGE 6: VISUALIZATIONS (3 charts)")
    print("-"*100)
    for i, viz in enumerate(sample_response['visualizations'], 1):
        config = viz['config']
        title = config.get('title', 'Visualization')
        print(f"{i}. {viz['type'].upper()}: {title}")
        print(f"   Purpose: {viz['purpose']}")
    
    print("\n" + "-"*100)
    print("STAGE 7: EXECUTIVE INSIGHTS")
    print("-"*100)
    
    print("\n📊 EXECUTIVE SUMMARY:")
    print(f"   {sample_response['insights']['summary']}")
    
    print("\n🔍 KEY FINDINGS:")
    for i, finding in enumerate(sample_response['insights']['key_findings'], 1):
        print(f"   {i}. {finding}")
    
    print("\n📈 DETAILED ANALYSIS:")
    for paragraph in sample_response['insights']['detailed_analysis'].split('\n\n'):
        print(f"   {paragraph}\n")
    
    print("💡 RECOMMENDATIONS:")
    for rec in sample_response['insights']['recommendations'].split('\n\n'):
        if rec.strip():
            print(f"   {rec}\n")
    
    print("\n" + "-"*100)
    print("STAGE 8: PERFORMANCE METRICS")
    print("-"*100)
    metadata = sample_response['metadata']
    print(f"⏱️  Total execution time: {metadata['total_execution_time_ms']}ms")
    print(f"🔍 Exploratory queries executed: {metadata['exploratory_queries_count']}")
    print(f"📊 Visualizations generated: {metadata['visualizations_count']}")
    print(f"📋 Schema columns analyzed: {metadata['schema_columns']}")
    
    intent = sample_response['intent']
    print(f"\n🎯 Intent Classification: {intent['primary_intent']} (confidence: {intent['confidence']*100:.0f}%)")
    
    print("\n" + "="*100)
    print("COMPARISON: BEFORE vs AFTER")
    print("="*100)
    
    comparison = """
    BEFORE (V2):                          AFTER (V3):
    ────────────────────────────────────  ────────────────────────────────────
    • 1-2 LLM calls                       • 5-7 LLM calls
    • No exploratory phase                • 2-3 exploratory queries
    • Basic schema context                • Rich context (samples + stats)
    • Simple SQL                          • CTEs + comments + NULL handling
    • 1 visualization                     • 2-3 complementary charts
    • Basic summary                       • Executive narrative + recommendations
    • Fixed temperature (0.7)             • Task-specific (0.1-0.7)
    • Default context (2048)              • Large context (8192)
    • No retry logic                      • 3 attempts with LLM correction
    """
    print(comparison)
    
    print("\n" + "="*100)
    print("✅ ANALYTICS SERVICE V3 - READY FOR PRODUCTION!")
    print("="*100 + "\n")


if __name__ == "__main__":
    print_preview()
