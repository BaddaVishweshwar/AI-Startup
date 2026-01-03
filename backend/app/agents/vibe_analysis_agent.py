import logging
import json
import time
import base64
from typing import Dict, Any, List, Optional
import pandas as pd
import sqlglot
from sqlglot import exp
try:
    import vl_convert as vlc
except ImportError:
    vlc = None
import pandas as pd
import sqlglot
from sqlglot import exp

from ..services.vector_service import vector_service
from ..services.ollama_service import ollama_service
from ..services.data_service import data_service
from ..prompts.vibe_prompts import get_vibe_system_prompt, VIBE_FEW_SHOT_EXAMPLES

logger = logging.getLogger(__name__)

class VibeAnalysisAgent:
    """
    Vibe Analysis Agent:
    - Context Retrieval (RAG)
    - Structured JSON Generation
    - SQL Validation (SQLGlot)
    - Deterministic Execution (DuckDB)
    - Auto-Repair Loop
    """
    
    def analyze(self, query: str, df: pd.DataFrame, dataset_id: str, history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Main entry point for "Vibe" analysis.
        """
        start_time = time.time()
        
        # 1. Retrieve Context (Grounding)
        context_docs = vector_service.retrieve_context(dataset_id, query)
        schema_context = "\n".join(context_docs) if context_docs else "No schema context found."
        
        # 2. Build System Prompt
        system_prompt = get_vibe_system_prompt(schema_context)
        
        # 3. Construct Messages (System + Few-Shot + History + User)
        prompt_text = ""
        # Add few-shot examples as "user/assistant" interaction simulation if model supports it, 
        # or append to system prompt. For simplicity with OllamaService, we'll append to prompt or rely on system prompt.
        # Let's append few-shots to system prompt or just assume the model follows the instruction.
        # Better: Include few-shot in the prompt text.
        
        few_shots = "\n\nEXAMPLES:\n"
        for ex in VIBE_FEW_SHOT_EXAMPLES:
            few_shots += f"User: {ex['user']}\nAssistant: {ex['assistant']}\n"
            
        full_prompt = f"{few_shots}\n\nUser: {query}"
        
        # 4. Generate & Loop (Validation/Repair)
        max_retries = 2
        last_error = None
        current_prompt = full_prompt
        
        for attempt in range(max_retries + 1):
            logger.info(f"🔄 Vibe Agent Attempt {attempt+1}")
            
            # Call LLM
            response_text = ollama_service.generate_response(
                prompt=current_prompt,
                system_prompt=system_prompt,
                json_mode=True,
                temperature=0.1
            )
            
            # Parse JSON
            try:
                response = json.loads(response_text)
            except json.JSONDecodeError:
                logger.error("❌ Failed to parse JSON response")
                last_error = "Invalid JSON output"
                current_prompt = f"{full_prompt}\n\nSYSTEM: Your last response was not valid JSON. Please output strict JSON."
                continue
                
            action = response.get("action")
            
            if action == "generate_sql":
                sql = response.get("sql")
                if not sql:
                     last_error = "Action is generate_sql but SQL is empty"
                     continue
                     
                # Validate SQL with SQLGlot
                try:
                    parsed = sqlglot.parse_one(sql)
                    # Extract tables to ensure we register the DF correctly
                    tables = [t.name for t in parsed.find_all(exp.Table)]
                    main_table = tables[0] if tables else "data"
                except Exception as e:
                    logger.warning(f"❌ SQL Syntax Error: {e}")
                    last_error = f"SQL Syntax Error: {str(e)}"
                    current_prompt = f"{full_prompt}\n\nSYSTEM: You generated invalid SQL: {sql}\nError: {str(e)}\nPlease fix it."
                    continue
                
                # Execute in DuckDB (Sandbox)
                # We need to handle the table name mapping. 
                # DataService registers 'data' by default. We might need to replace table name in SQL or register df as that name.
                # Easiest: Replace table name in SQL with 'data'
                # OR: Custom execution where we register df as `main_table`
                
                logger.info(f"🚀 Executing SQL: {sql}")
                exec_result = self._execute_safe(sql, df, main_table)
                
                if not exec_result["success"]:
                    logger.warning(f"❌ Runtime Error: {exec_result['error']}")
                    last_error = f"Runtime SQL Error: {exec_result['error']}"
                    current_prompt = f"{full_prompt}\n\nSYSTEM: SQL execution failed: {sql}\nError: {exec_result['error']}\nPlease fix the SQL."
                    continue
                
                # Success! Attach results
                response["execution_result"] = exec_result
                
                # Check consistency (optional: simple check if 'row_count' matches explanation)
                # ... 
                
                # SERVER-SIDE VISUALIZATION RENDERING
                viz_spec = response.get("viz_spec")
                if viz_spec and exec_result.get("data") and vlc:
                    try:
                        # Inject data into spec
                        viz_spec["data"] = {"values": exec_result["data"]}
                        
                        # Render to PNG
                        png_data = vlc.vegalite_to_png(viz_spec, scale=2)
                        if png_data:
                            response["image_base64"] = base64.b64encode(png_data).decode("utf-8")
                            logger.info("✅ Generated Server-Side Chart Image")
                    except Exception as ve:
                         logger.warning(f"⚠️ Failed to render Vega-Lite spec: {ve}")

                return response
                
            elif action in ["ask_clarify", "error", "explain"]:
                # No execution needed
                return response
            
            # If viz_spec is present but no SQL? (Phase 4)
            # Usually follows SQL.
            
        # If exhausted retries
        return {
            "action": "error",
            "error": f"Failed after {max_retries} attempts. Last error: {last_error}"
        }

    def _execute_safe(self, sql: str, df: pd.DataFrame, table_name: str) -> Dict[str, Any]:
        """
        Execute SQL with DuckDB, registering the DF as `table_name`.
        """
        import duckdb
        try:
            con = duckdb.connect(database=':memory:')
            con.register(table_name, df)
            
            # Add LIMIT if not present (safety)
            if "limit" not in sql.lower():
                sql += " LIMIT 1000"
                
            # Run
            result_df = con.execute(sql).df()
            con.close()
            
            return {
                "success": True,
                "data": result_df.to_dict('records'),
                "columns": list(result_df.columns),
                "row_count": len(result_df)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

vibe_agent = VibeAnalysisAgent()
