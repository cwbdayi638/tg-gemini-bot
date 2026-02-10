# ai_service.py - Enhanced AI service for earthquake queries
import json
import re
import requests
from datetime import datetime, timedelta
from gradio_client import Client

from .config import MCP_SERVER_URL

# Ollama server configuration
OLLAMA_BASE_URL = "https://fgs.zeabur.app"
OLLAMA_MODEL = "smollm:135m"
OLLAMA_PROMPT_TEMPLATE = "Context:\n{context}\n\nQuestion: {prompt}\n\nPlease provide a concise and informative answer based on the context provided."

# Track if model has been pulled
_ollama_model_pulled = False

# Tool function for earthquake search
def call_mcp_earthquake_search(
    start_date: str,
    end_date: str,
    min_magnitude: float = 4.5,
    max_magnitude: float = 8.0
) -> str:
    """Search for earthquake events based on specified conditions (time, magnitude) from remote server."""
    try:
        print(f"--- Calling remote earthquake MCP server ---")
        print(f"    Query conditions: {start_date} to {end_date}, magnitude {min_magnitude} and above")

        client = Client(src=MCP_SERVER_URL)
        result = client.predict(
            param_0=start_date, param_1="00:00:00",
            param_2=end_date, param_3="23:59:59",
            param_4=21.0, param_5=26.0, # Default Taiwan latitude
            param_6=119.0, param_7=123.0, # Default Taiwan longitude
            param_8=0.0, param_9=100.0,
            param_10=min_magnitude, param_11=max_magnitude,
            api_name="/gradio_fetch_and_plot_data"
        )
        dataframe_dict = result[0]
        data = dataframe_dict.get('data', [])

        if not data:
            print("--- MCP server returned: no matching earthquakes found ---")
            return "Query completed, but no earthquake data matching the conditions was found."

        headers = dataframe_dict.get('headers', [])
        formatted_results = [dict(zip(headers, row)) for row in data]
        print(f"--- MCP server successfully returned {len(data)} records ---")
        return json.dumps(formatted_results, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Failed to call MCP server: {e}")
        return f"Tool execution failed, error message: {e}"

def _parse_date_from_question(question: str) -> tuple:
    """Parse dates from natural language question."""
    current_date = datetime.now()
    question_lower = question.lower()
    
    # Default to last 7 days
    start_date = (current_date - timedelta(days=7)).strftime("%Y-%m-%d")
    end_date = current_date.strftime("%Y-%m-%d")
    
    # Check for specific patterns
    if "yesterday" in question_lower or "昨天" in question_lower:
        date = current_date - timedelta(days=1)
        start_date = date.strftime("%Y-%m-%d")
        end_date = date.strftime("%Y-%m-%d")
    elif "today" in question_lower or "今天" in question_lower:
        start_date = current_date.strftime("%Y-%m-%d")
        end_date = current_date.strftime("%Y-%m-%d")
    elif "last week" in question_lower or "上週" in question_lower or "上周" in question_lower:
        start_date = (current_date - timedelta(days=14)).strftime("%Y-%m-%d")
        end_date = (current_date - timedelta(days=7)).strftime("%Y-%m-%d")
    elif "this month" in question_lower or "這個月" in question_lower or "这个月" in question_lower:
        start_date = current_date.replace(day=1).strftime("%Y-%m-%d")
        end_date = current_date.strftime("%Y-%m-%d")
    elif "last month" in question_lower or "上個月" in question_lower or "上个月" in question_lower:
        first_day_this_month = current_date.replace(day=1)
        last_month = first_day_this_month - timedelta(days=1)
        start_date = last_month.replace(day=1).strftime("%Y-%m-%d")
        end_date = last_month.strftime("%Y-%m-%d")
    
    # Check for year patterns
    year_match = re.search(r'20\d{2}', question)
    if year_match:
        year = year_match.group()
        start_date = f"{year}-01-01"
        end_date = f"{year}-12-31"
    
    # Check for specific month patterns (e.g., "2024年4月" or "April 2024")
    month_year_match = re.search(r'(20\d{2})[年\-](0?[1-9]|1[0-2])', question)
    if month_year_match:
        import calendar
        year = int(month_year_match.group(1))
        month = int(month_year_match.group(2))
        start_date = f"{year}-{month:02d}-01"
        # Get last day of month
        last_day = calendar.monthrange(year, month)[1]
        end_date = f"{year}-{month:02d}-{last_day}"
    
    return start_date, end_date

def _parse_magnitude_from_question(question: str) -> tuple:
    """Parse magnitude requirements from question."""
    min_magnitude = 4.5
    max_magnitude = 8.0
    
    # Look for magnitude patterns
    mag_match = re.search(r'[Mm](?:agnitude|规模|規模)?[>≥]?\s*(\d+(?:\.\d+)?)', question)
    if mag_match:
        min_magnitude = float(mag_match.group(1))
    
    mag_range_match = re.search(r'[Mm](?:agnitude|规模|規模)?\s*(\d+(?:\.\d+)?)\s*[-到至]\s*(\d+(?:\.\d+)?)', question)
    if mag_range_match:
        min_magnitude = float(mag_range_match.group(1))
        max_magnitude = float(mag_range_match.group(2))
    
    return min_magnitude, max_magnitude

def _should_search_earthquakes(question: str) -> bool:
    """Determine if the question requires earthquake search."""
    earthquake_keywords = [
        'earthquake', 'earthquakes', 'seismic', 'tremor',
        '地震', '震度', '規模', '规模', 'magnitude'
    ]
    return any(keyword in question.lower() for keyword in earthquake_keywords)

def _call_ollama_llm(prompt: str, context: str = "") -> str:
    """Call Ollama LLM for text generation."""
    global _ollama_model_pulled
    
    try:
        # Only pull the model once per session
        if not _ollama_model_pulled:
            pull_url = f"{OLLAMA_BASE_URL}/api/pull"
            pull_payload = {"name": OLLAMA_MODEL}
            
            print(f"--- Ensuring Ollama model {OLLAMA_MODEL} is available ---")
            try:
                pull_response = requests.post(pull_url, json=pull_payload, timeout=30)
                # Ollama pull endpoint returns streaming responses, we just need to ensure it starts
                print(f"Model pull initiated: {pull_response.status_code}")
                _ollama_model_pulled = True
            except Exception as e:
                print(f"Warning: Could not verify model availability: {e}")
                # Continue anyway - model might already be available
        
        # Generate response using Ollama
        generate_url = f"{OLLAMA_BASE_URL}/api/generate"
        
        # Combine context and prompt if context is provided
        full_prompt = prompt
        if context:
            full_prompt = OLLAMA_PROMPT_TEMPLATE.format(context=context, prompt=prompt)
        
        generate_payload = {
            "model": OLLAMA_MODEL,
            "prompt": full_prompt,
            "stream": False
        }
        
        print(f"--- Calling Ollama API at {generate_url} ---")
        response = requests.post(generate_url, json=generate_payload, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        generated_text = result.get("response", "")
        
        print(f"--- Ollama API returned successfully ---")
        return generated_text.strip()
        
    except requests.exceptions.Timeout as e:
        print(f"Timeout calling Ollama API: {e}")
        return f"Error: Request timed out. The Ollama server took too long to respond. Please try again later."
    except requests.exceptions.RequestException as e:
        print(f"Error calling Ollama API: {e}")
        return f"Error: Could not connect to Ollama server. {str(e)}"
    except Exception as e:
        print(f"Unexpected error with Ollama: {e}")
        return f"Error: {str(e)}"

# Main AI text generation function
def generate_ai_text(user_prompt: str) -> str:
    """Generate AI response with earthquake search capability using Ollama LLM."""
    
    # Check if this is an earthquake-related question
    if _should_search_earthquakes(user_prompt):
        try:
            # Parse parameters from the question
            start_date, end_date = _parse_date_from_question(user_prompt)
            min_magnitude, max_magnitude = _parse_magnitude_from_question(user_prompt)
            
            # Call the earthquake search
            earthquake_data = call_mcp_earthquake_search(
                start_date=start_date,
                end_date=end_date,
                min_magnitude=min_magnitude,
                max_magnitude=max_magnitude
            )
            
            # Parse the JSON response
            if "no earthquake data matching" in earthquake_data.lower():
                context = f"Searched for earthquakes from {start_date} to {end_date} with magnitude ≥{min_magnitude}, but no matching earthquakes were found."
                return f"🌍 {_call_ollama_llm(user_prompt, context)}"
            
            try:
                eq_list = json.loads(earthquake_data)
                if not eq_list:
                    return f"🌍 No earthquakes found for the specified criteria."
                
                # Format earthquake data as context
                context = f"Earthquake Search Results ({start_date} to {end_date}, M≥{min_magnitude}):\n\n"
                context += f"Found {len(eq_list)} earthquake(s):\n\n"
                
                # Include all earthquakes in context for LLM
                for i, eq in enumerate(eq_list, 1):
                    time_str = eq.get('Time', 'Unknown')
                    location = eq.get('Location', 'Unknown')
                    magnitude = eq.get('Magnitude', 'N/A')
                    depth = eq.get('Depth', 'N/A')
                    
                    context += f"{i}. Time: {time_str}, Location: {location}, Magnitude: M{magnitude}, Depth: {depth} km\n"
                
                # Use Ollama to generate a natural language response
                llm_response = _call_ollama_llm(user_prompt, context)
                
                # Format the final response
                response = f"🌍 {llm_response}"
                
                return response
                
            except json.JSONDecodeError:
                # If JSON parsing fails, use LLM with raw data
                llm_response = _call_ollama_llm(user_prompt, f"Earthquake data retrieved:\n{earthquake_data}")
                return f"🌍 {llm_response}"
                
        except Exception as e:
            print(f"Error processing earthquake question: {e}")
            return f"🤖 I encountered an error while searching for earthquake data: {e}\n\nPlease try using specific commands like /eq_latest or /eq_global instead."
    
    # For non-earthquake questions, use Ollama LLM directly
    llm_response = _call_ollama_llm(user_prompt)
    
    if llm_response.startswith("Error:"):
        # If Ollama fails, return a helpful message
        response_text = (
            f"🤖 I'm an assistant for this Telegram bot. You asked: '{user_prompt}'\n\n"
            "I can help you with:\n"
            "• Earthquake information (use /eq_latest, /eq_global, /eq_taiwan)\n"
            "• Web search (use /search <query>)\n\n"
            "For earthquake-specific questions, please mention 'earthquake' or '地震' in your question."
        )
        return response_text
    
    return f"🤖 {llm_response}"
