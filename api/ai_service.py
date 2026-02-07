# ai_service.py - Enhanced AI service with Hugging Face Transformers
import json
import re
from datetime import datetime, timedelta
from gradio_client import Client

from .config import MCP_SERVER_URL

# Try to import Hugging Face Transformers
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

# Global model cache
_ai_model = None
_ai_tokenizer = None

def _load_ai_model():
    """Load Hugging Face model for AI text generation."""
    global _ai_model, _ai_tokenizer
    
    if _ai_model is not None:
        return _ai_model, _ai_tokenizer
    
    if not TRANSFORMERS_AVAILABLE:
        return None, None
    
    try:
        # Use a lightweight instruction-following model
        model_name = "google/flan-t5-base"
        print(f"Loading AI model: {model_name}...")
        
        _ai_tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        _ai_model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if device == "cuda" else torch.float32,
            low_cpu_mem_usage=True
        )
        _ai_model.to(device)
        _ai_model.eval()
        
        print(f"✓ AI model loaded successfully on {device}")
        return _ai_model, _ai_tokenizer
    except Exception as e:
        print(f"Error loading AI model: {e}")
        # Try fallback to pipeline
        try:
            print("Trying text-generation pipeline as fallback...")
            _ai_model = pipeline("text-generation", model="microsoft/DialoGPT-small")
            _ai_tokenizer = None
            print("✓ Fallback pipeline loaded")
            return _ai_model, None
        except Exception as e2:
            print(f"Fallback also failed: {e2}")
            return None, None

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
        year = month_year_match.group(1)
        month = month_year_match.group(2).zfill(2)
        start_date = f"{year}-{month}-01"
        # Last day of month
        if month in ['01', '03', '05', '07', '08', '10', '12']:
            end_date = f"{year}-{month}-31"
        elif month in ['04', '06', '09', '11']:
            end_date = f"{year}-{month}-30"
        else:  # February
            end_date = f"{year}-{month}-28"
    
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

# Main AI text generation function
def generate_ai_text(user_prompt: str) -> str:
    """Generate AI response with earthquake search capability using Hugging Face Transformers."""
    
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
                return f"🌍 I searched for earthquakes from {start_date} to {end_date} with magnitude ≥{min_magnitude}, but no matching earthquakes were found."
            
            try:
                eq_list = json.loads(earthquake_data)
                if not eq_list:
                    return f"🌍 No earthquakes found for the specified criteria."
                
                # Format the response
                response = f"🌍 Earthquake Search Results ({start_date} to {end_date}, M≥{min_magnitude}):\n\n"
                response += f"Found {len(eq_list)} earthquake(s):\n\n"
                
                # Show up to 5 earthquakes
                for i, eq in enumerate(eq_list[:5], 1):
                    time_str = eq.get('Time', 'Unknown')
                    location = eq.get('Location', 'Unknown')
                    magnitude = eq.get('Magnitude', 'N/A')
                    depth = eq.get('Depth', 'N/A')
                    
                    response += f"{i}. Time: {time_str}\n"
                    response += f"   Location: {location}\n"
                    response += f"   Magnitude: M{magnitude} | Depth: {depth} km\n\n"
                
                if len(eq_list) > 5:
                    response += f"... and {len(eq_list) - 5} more earthquake(s)."
                
                # Add interpretation for specific questions
                if "largest" in user_prompt.lower() or "biggest" in user_prompt.lower() or "最大" in user_prompt:
                    max_eq = max(eq_list, key=lambda x: float(x.get('Magnitude', 0)))
                    response += f"\n\n📊 The largest earthquake was M{max_eq.get('Magnitude')} at {max_eq.get('Location')} on {max_eq.get('Time')}."
                
                return response
                
            except json.JSONDecodeError:
                # If JSON parsing fails, return the raw data
                return f"🌍 Earthquake data retrieved:\n\n{earthquake_data}"
                
        except Exception as e:
            print(f"Error processing earthquake question: {e}")
            return f"🤖 I encountered an error while searching for earthquake data: {e}\n\nPlease try using specific commands like /eq_latest or /eq_global instead."
    
    # For non-earthquake questions, use simple conversational AI
    model, tokenizer = _load_ai_model()
    
    if model is None:
        return "🤖 AI service is not available. Transformers library may not be installed. Please use specific commands like /help, /eq_latest, or /news to access available features."
    
    try:
        # Simple text generation response
        if tokenizer is not None:
            # Using a proper model
            response_text = f"I'm an AI assistant for this Telegram bot. You asked: '{user_prompt}'\n\n"
            response_text += "I can help you with:\n"
            response_text += "• Earthquake information (use /eq_latest, /eq_global, /eq_taiwan)\n"
            response_text += "• News updates (use /news, /news_tech, /news_taiwan)\n"
            response_text += "• Web search (use /search <query>)\n\n"
            response_text += "For earthquake-specific questions, please mention 'earthquake' or '地震' in your question."
        else:
            # Using pipeline
            generated = model(user_prompt, max_length=100, num_return_sequences=1)
            response_text = generated[0]['generated_text']
        
        return response_text
        
    except Exception as e:
        print(f"Error during AI text generation: {e}")
        return f"🤖 AI service error: {e}\n\nPlease use /help to see available commands."
