# Analytics Service V3 - Integration Guide

## Quick Start

The enhanced multi-agent analytics pipeline (V3) is now integrated into your backend!

### What's New

✅ **5-7 LLM calls per query** (vs 1-2 before)  
✅ **2-3 exploratory queries** before main analysis  
✅ **Executive-level insights** with recommendations  
✅ **Multi-visualization** (2-3 complementary charts)  
✅ **Enhanced prompts** with rich context  
✅ **Retry logic** with LLM error correction  

### Files Modified

- `backend/app/routes/queries.py` - Updated to use `analytics_service_v3`

### Files Created

1. `backend/app/prompts/enhanced_prompts.py` - Prompt templates
2. `backend/app/services/context_enrichment_service.py` - Schema enrichment
3. `backend/app/services/query_validator_service.py` - SQL validation
4. `backend/app/services/response_formatter_service.py` - Response formatting
5. `backend/app/agents/enhanced_exploration_agent.py` - Exploratory queries
6. `backend/app/services/analytics_service_v3.py` - Main orchestrator

### Testing

Run the integration test:
```bash
cd backend
python test_analytics_v3.py
```

### API Usage

The `/queries/ask` endpoint now uses Analytics Service V3 automatically:

```bash
curl -X POST "http://localhost:8000/queries/ask" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_id": 1,
    "query": "What are the top 10 products by revenue?",
    "session_id": "optional-session-id"
  }'
```

### Response Structure

```json
{
  "id": 123,
  "natural_language_query": "What are the top 10 products by revenue?",
  "generated_sql": "WITH product_revenue AS (...) SELECT ...",
  "result_data": [...],
  "visualization_config": {
    "type": "bar",
    "config": {...}
  },
  "insights": "### 📊 Executive Summary\n...",
  "analysis_plan": {
    "understanding": "User wants to identify highest-revenue products",
    "approach": "Aggregate revenue by product and rank them",
    "exploratory_steps": [...]
  },
  "status": "success"
}
```

### Configuration

Task-specific temperatures are automatically applied:
- Planning: 0.5
- SQL Generation: 0.1
- Insights: 0.7

Context window: 8192 tokens  
Max response: 2048 tokens

### Rollback (if needed)

To revert to the previous version, change line 212 in `queries.py`:

```python
# From:
analysis_response = await analytics_service_v3.analyze(...)

# To:
analysis_response = analytics_service_v2.analyze(...)
```

---

**Status:** ✅ Ready to use  
**Version:** 3.0  
**Date:** 2026-01-03
