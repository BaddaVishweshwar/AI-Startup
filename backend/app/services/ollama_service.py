import ollama
from typing import Dict, Any, Optional
import json
import re
from ..config import settings
import logging

logger = logging.getLogger(__name__)

class OllamaService:
    """
    Hybrid LLM Service.
    Supports local Ollama models AND external OpenAI-compatible providers (GPT-4o, GitHub Models).
    """
    
    def __init__(self):
        self.provider = "ollama"
        self.client = None
        self.model_name = settings.OLLAMA_MODEL
        
        # Check for OpenAI/GitHub Models configuration
        if settings.OPENAI_API_KEY:
            try:
                from openai import OpenAI
                self.provider = "openai"
                self.model_name = settings.OPENAI_MODEL
                
                # Configure client (support custom base URL for GitHub Models)
                client_args = {"api_key": settings.OPENAI_API_KEY}
                if settings.OPENAI_API_BASE:
                    client_args["base_url"] = settings.OPENAI_API_BASE
                    
                self.client = OpenAI(**client_args)
                logger.info(f"🚀 Using OpenAI Provider: {self.model_name}")
            except ImportError:
                logger.error("❌ openai package not installed. Falling back to Ollama.")
                self.provider = "ollama"
        
        # Fallback to Ollama
        if self.provider == "ollama":
            self.client = ollama.Client(host=settings.OLLAMA_HOST)
            logger.info(f"🦙 Using Ollama Provider: {self.model_name}")

    def check_availability(self) -> bool:
        """Check if LLM service is configured and available"""
        if self.provider == "openai":
            return bool(settings.OPENAI_API_KEY)
        else:
            # For Ollama, we could check connectivity, but for now just config
            return True

    def generate_response(self, prompt: str, system_prompt: str = None, json_mode: bool = False, temperature: float = 0.7) -> str:
        """Unified generation method"""
        
        if self.provider == "openai":
            import openai
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response_format = {"type": "json_object"} if json_mode else None
            
            try:
                completion = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=temperature,
                    response_format=response_format
                )
                return completion.choices[0].message.content
            except (openai.AuthenticationError, openai.APIConnectionError, openai.APIError) as e:
                logger.warning(f"⚠️ OpenAI Error: {e}. Falling back to Ollama.")
                self.provider = "ollama"
                self.model_name = settings.OLLAMA_MODEL
                self.client = ollama.Client(host=settings.OLLAMA_HOST)
                # Retry with Ollama
                return self.generate_response(prompt, system_prompt, json_mode, temperature)
            except Exception as e:
                logger.error(f"OpenAI Generation Error: {e}")
                raise e

        # Ollama Implementation
        options = {"temperature": temperature}
        if json_mode:
            options["format"] = "json"
            
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"System: {system_prompt}\n\nUser: {prompt}"
        
        response = self.client.generate(
            model=self.model_name,
            prompt=full_prompt,
            options=options
        )
        return response['response']

    # ------------------------------------------------------------------
    # Legacy Methods (Refactored to use generic generate_response)
    # ------------------------------------------------------------------

    def generate_analysis_plan(
        self, 
        natural_query: str, 
        schema: Dict[str, Any],
        sample_data: list,
        related_expertise: list = []
    ) -> Dict[str, Any]:
        """Generate a professional analysis plan"""
        
        schema_desc = self._format_schema(schema)
        sample_desc = self._format_sample_data(sample_data)
        
        expertise_desc = ""
        if related_expertise:
            expertise_desc = "\nExamples of past successful queries:\n"
            for exp in related_expertise:
                expertise_desc += f"User: {exp['query']}\nSQL:\n```sql\n{exp['sql']}\n```\n"
        
        system_prompt = "You are a Senior Data Analyst. Answer the user's question with professional-grade analysis."
        prompt = f"""
1. INTENT: Decision between chart/viz OR data records.
2. SQL: Write DuckDB SQL for 'data' table. Limit 500.
3. CLEANING: Python code for pandas 'df'.
4. VISUALIZATION: Plot on matplotlib 'ax' if needed, else leave empty.

Schema:
{schema_desc}

Sample:
{sample_desc}
{expertise_desc}

User Question: {natural_query}

Output Format:
SQL:
```sql
<sql here>
```

PYTHON:
```python
# Cleaning
<cleaning steps>

# Visualization
<plotting logic using ax or leave empty>
```
"""
        try:
            full_text = self.generate_response(prompt, system_prompt=system_prompt, temperature=0.1)
            
            sql_query = self._extract_sql(full_text)
            python_code = self._extract_python(full_text)
            
            return {
                "success": True,
                "sql": sql_query,
                "python": python_code,
                "error": None
            }
        except Exception as e:
            return {"success": False, "sql": None, "python": None, "error": str(e)}

    def generate_eda_report(
        self,
        schema: Dict[str, Any],
        sample_data: list
    ) -> Dict[str, Any]:
        """Generate a comprehensive EDA report"""
        schema_desc = self._format_schema(schema)
        sample_desc = self._format_sample_data(sample_data)
        
        system_prompt = "You are a Lead Data Scientist. Perform a comprehensive Exploratory Data Analysis (EDA)."
        prompt = f"""
Dataset Schema:
{schema_desc}

Sample Data:
{sample_desc}

Provide a structured EDA report and Python code for key visualizations.
You are provided with a pandas DataFrame 'df' and a matplotlib axis 'ax'.
DO NOT create new figures or axes. Use 'ax'.

Output Format:
REPORT:
- Data Overview
- Potential Data Quality Issues
- Key Correlations
- Recommended Cleaning steps

PYTHON:
```python
# Cleaning (if needed on df)
# Plotting (on ax)
```
"""
        try:
            full_text = self.generate_response(prompt, system_prompt=system_prompt, temperature=0.2)
            
            report = full_text.split("PYTHON:")[0].replace("REPORT:", "").strip()
            python_code = self._extract_python(full_text)
            
            return {
                "success": True,
                "report": report,
                "python": python_code,
                "error": None
            }
        except Exception as e:
            return {"success": False, "report": None, "python": None, "error": str(e)}

    def generate_insights(
        self,
        query: str,
        result_data: list,
        chart_type: Optional[str] = None
    ) -> str:
        """Generate high-level business insights"""
        
        limited_data = result_data[:10] # Larger context allowed for GPT
        
        system_prompt = "You are a Management Consultant."
        prompt = f"""
Provide a sharp, executive summary of this data.

**CONTEXT**
User Question: "{query}"
Data Preview: {json.dumps(limited_data, default=str)}

**INSTRUCTIONS**
1. **EXECUTIVE SUMMARY**: 1-2 sentence high-level takeaway.
2. **KEY FINDINGS**: Detailed bulleted list with bold emphasis.
3. **METRIC SUMMARY TABLE**: Clean Markdown table for key numbers.
4. **ACTIONABLE RECOMMENDATIONS**: Specific steps based on data.

Format Structure:
### 📊 Executive Summary
<summary>

### 🔍 Key Findings
- **<point>**: <detail>

### 📈 Metric Summary
| Dimension | Metric |
| :--- | :--- |
| ... | ... |

### 💡 Recommendations
- **<step>**: <reason>
"""
        try:
             return self.generate_response(prompt, system_prompt=system_prompt, temperature=0.3)
        except Exception as e:
            return "Insights unavailable."

    # ------------------------------------------------------------------
    # Compatibility Layer for Agents
    # Agents call client.generate(model=..., prompt=..., options=...) directly
    # We must patch this if using OpenAI
    # ------------------------------------------------------------------
    
    def generate(self, model: str, prompt: str, options: dict = None) -> Dict[str, str]:
        """
        Compatibility method to mimic ollama.generate signature.
        Used by the new agent system (SchemaAnalyzer, QueryPlanner, etc.)
        """
        temp = options.get("temperature", 0.7) if options else 0.7
        
        # Check if json mode is requested via options or prompt
        json_mode = False
        if options and options.get("format") == "json":
            json_mode = True
        
        response_text = self.generate_response(prompt, temperature=temp, json_mode=json_mode)
        
        # Return in Ollama format: {'response': '...'}
        return {'response': response_text}

    def _extract_section(self, text: str, section_name: str) -> str:
        """Extract a named section (e.g., 'STRATEGY:') from text"""
        if section_name not in text:
            return ""
        
        parts = text.split(section_name)
        if len(parts) < 2:
            return ""
            
        content = parts[1].split("\n\n")[0].split("SQL:")[0].split("PYTHON:")[0].strip()
        return content

    def _format_schema(self, schema: Dict[str, Any]) -> str:
        return "\n".join([f"  - {k}: {v}" for k, v in schema.items()])
    
    def _format_sample_data(self, sample_data: list) -> str:
        return json.dumps(sample_data[:3], indent=2)

    def _extract_sql(self, text: str) -> str:
        matches = re.findall(r"```(?:sql)?\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE)
        if matches:
            return matches[-1].strip()
            
        # Fallback: Look for raw SELECT statement
        select_pattern = r"(SELECT\s+[\s\S]+?\s+FROM\s+[\s\S]+?;)"
        raw_matches = re.findall(select_pattern, text, re.IGNORECASE)
        if raw_matches:
             return raw_matches[-1].strip()

        # SUPER FALLBACK: Find "SELECT" case-insensitive
        parts = re.split(r"SELECT\s", text, flags=re.IGNORECASE)
        if len(parts) > 1:
            return ("SELECT " + parts[-1]).strip()

        return text.strip()

    def _extract_python(self, text: str) -> str:
        import textwrap
        python_section = text.split("PYTHON:")[-1] if "PYTHON:" in text else text
        matches = re.findall(r"```(?:python)?\s*(.*?)\s*```", python_section, re.DOTALL | re.IGNORECASE)
        return textwrap.dedent(matches[0]).strip() if matches else ""

# Singleton instance
ollama_service = OllamaService()
