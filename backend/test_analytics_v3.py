"""
Integration Test for Analytics Service V3

Quick test to verify the enhanced multi-agent pipeline is working correctly.
"""

import asyncio
import pandas as pd
from app.services.analytics_service_v3 import analytics_service_v3
from app.models import Dataset


async def test_analytics_v3():
    """Test the analytics service v3 with sample data."""
    
    # Create sample dataset
    sample_data = {
        'product': ['Widget A', 'Widget B', 'Widget C', 'Widget A', 'Widget B', 
                   'Widget C', 'Widget A', 'Widget B', 'Widget C', 'Widget A'],
        'date': ['2024-01-01', '2024-01-01', '2024-01-01', '2024-01-02', '2024-01-02',
                '2024-01-02', '2024-01-03', '2024-01-03', '2024-01-03', '2024-01-04'],
        'quantity': [5, 10, 15, 8, 12, 20, 6, 9, 18, 7],
        'price': [99.99, 149.99, 199.99, 99.99, 149.99, 199.99, 99.99, 149.99, 199.99, 99.99],
        'revenue': [499.95, 1499.90, 2999.85, 799.92, 1799.88, 3999.80, 599.94, 1349.91, 3599.82, 699.93]
    }
    
    df = pd.DataFrame(sample_data)
    
    # Create mock dataset object
    class MockDataset:
        id = 1
        table_name = "sales_data"
        schema = {"columns": list(sample_data.keys())}
    
    dataset = MockDataset()
    
    # Test query
    test_query = "What are the top 3 products by revenue?"
    
    print("=" * 80)
    print("TESTING ANALYTICS SERVICE V3")
    print("=" * 80)
    print(f"\nQuery: {test_query}\n")
    print("Running enhanced multi-agent pipeline...")
    print("-" * 80)
    
    try:
        # Execute analysis
        result = await analytics_service_v3.analyze(
            query=test_query,
            dataset=dataset,
            df=df,
            connection=None,
            context=None
        )
        
        # Display results
        print("\n✅ ANALYSIS COMPLETE!\n")
        
        if result.get('success'):
            print("📊 UNDERSTANDING:")
            print(f"   {result.get('understanding', 'N/A')}\n")
            
            print("🎯 APPROACH:")
            print(f"   {result.get('approach', 'N/A')}\n")
            
            print("🔍 EXPLORATORY STEPS:")
            for i, step in enumerate(result.get('exploratory_steps', []), 1):
                print(f"   {i}. {step.get('question', 'N/A')}")
                print(f"      Finding: {step.get('finding', 'N/A')}")
            print()
            
            print("💻 MAIN SQL:")
            sql_info = result.get('sql_query', {})
            print(f"   {sql_info.get('query', 'N/A')}\n")
            
            print("📈 RESULTS:")
            results = result.get('results', {})
            print(f"   Rows returned: {results.get('row_count', 0)}")
            print(f"   Columns: {', '.join(results.get('columns', []))}\n")
            
            print("📊 VISUALIZATIONS:")
            for i, viz in enumerate(result.get('visualizations', []), 1):
                print(f"   {i}. {viz.get('type', 'N/A')} - {viz.get('config', {}).get('title', 'N/A')}")
            print()
            
            print("💡 INSIGHTS:")
            insights = result.get('insights', {})
            print(f"   Summary: {insights.get('summary', 'N/A')}")
            print(f"   Key Findings: {len(insights.get('key_findings', []))} findings")
            if insights.get('recommendations'):
                print(f"   Recommendations: ✓")
            print()
            
            print("⏱️  PERFORMANCE:")
            metadata = result.get('metadata', {})
            print(f"   Total time: {metadata.get('total_execution_time_ms', 0)}ms")
            print(f"   Exploratory queries: {metadata.get('exploratory_queries_count', 0)}")
            print(f"   Visualizations: {metadata.get('visualizations_count', 0)}")
            
        else:
            print("❌ ANALYSIS FAILED")
            error = result.get('error', {})
            print(f"   Error: {error.get('message', 'Unknown error')}")
            print(f"   Details: {error.get('details', 'N/A')}")
        
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\nStarting Analytics Service V3 Integration Test...\n")
    asyncio.run(test_analytics_v3())
    print("\nTest complete!\n")
