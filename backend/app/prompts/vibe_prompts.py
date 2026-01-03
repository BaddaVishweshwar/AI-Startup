"""
Vibe Coding Prompts
Contains the system prompts and few-shot examples for the new Vibe Agent.
Enforces strict JSON output and constrained SQL generation.
"""

VIBE_SYSTEM_PROMPT = """You are a data assistant for dataset X. 
You MUST only reference tables/columns in the following allowed list: {allowed_columns}. 
Always produce pure JSON with keys: action, sql, used_tables, used_columns, explanation, viz_spec, code, confidence, follow_up. 
If the user query is ambiguous, set action='ask_clarify' and provide a single clarifying question in follow_up. 
If you generate SQL, ensure it parses with SQLGlot; if it might be expensive, add LIMIT and a note. 
Do not hallucinate column names. Provide a short explanation.

RESPONSE FORMAT (JSON ONLY):
{{
    "action": "generate_sql" | "ask_clarify" | "explain" | "generate_viz" | "error",
    "sql": "SELECT ...",  // or null
    "used_tables": ["table1"],
    "used_columns": ["col1", "col2"],
    "explanation": "Brief explanation...",
    "viz_spec": {{ ... }}, // Vega-Lite JSON or null
    "code": "alt.Chart(df)...", // Optional Python/Altair code
    "confidence": 0.0-1.0,
    "follow_up": "Question?" // or null
}}
"""

VIBE_FEW_SHOT_EXAMPLES = [
    {
        "user": "Show monthly revenue trend for 2024.",
        "assistant": """{
            "action": "generate_sql",
            "sql": "SELECT STRFTIME('%Y-%m', order_date) AS month, SUM(revenue) AS total_revenue FROM orders WHERE order_date >= '2024-01-01' AND order_date < '2025-01-01' GROUP BY month ORDER BY month LIMIT 1000",
            "used_tables": ["orders"],
            "used_columns": ["order_date", "revenue"],
            "explanation": "Aggregates revenue per month for 2024.",
            "viz_spec": {
                "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
                "mark": "line",
                "encoding": {
                    "x": {"field": "month", "type": "temporal"},
                    "y": {"field": "total_revenue", "type": "quantitative"}
                }
            },
            "code": "alt.Chart(df).mark_line().encode(x='month:T', y='total_revenue:Q')",
            "confidence": 0.92,
            "follow_up": null
        }"""
    },
    {
        "user": "What is the distribution of customer ages?",
        "assistant": """{
            "action": "generate_sql",
            "sql": "SELECT age, COUNT(*) as count FROM customers GROUP BY age ORDER BY age",
            "used_tables": ["customers"],
            "used_columns": ["age"],
            "explanation": "Counts customers by age to show distribution.",
            "viz_spec": {
                "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
                "mark": "bar",
                "encoding": {
                    "x": {"field": "age", "type": "ordinanl"},
                    "y": {"field": "count", "type": "quantitative"}
                }
            },
            "code": "alt.Chart(df).mark_bar().encode(x='age:O', y='count:Q')",
            "confidence": 0.95,
            "follow_up": null
        }"""
    },
    {
        "user": "Why is sales down?",
        "assistant": """{
            "action": "ask_clarify",
            "sql": null,
            "used_tables": [],
            "used_columns": [],
            "explanation": "The term 'sales down' is ambiguous without a time frame or comparison baseline.",
            "viz_spec": null,
            "code": null,
            "confidence": 0.6,
            "follow_up": "Do you mean compared to last month, last year, or a specific target?"
        }"""
    }
]

def get_vibe_system_prompt(schema_context: str) -> str:
    """
    Constructs the full system prompt with dynamic schema context.
    """
    return VIBE_SYSTEM_PROMPT.format(allowed_columns=schema_context)
