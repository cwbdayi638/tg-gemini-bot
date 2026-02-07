# ai_service.py - Enhanced AI service for earthquake queries
import json
import re
from datetime import datetime, timedelta
from gradio_client import Client

from .config import MCP_SERVER_URL

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

# Main AI text generation function
def generate_ai_text(user_prompt: str) -> str:
    """Generate AI response with earthquake search capability."""
    
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
    
    # For non-earthquake questions, return a helpful message
    response_text = (
        f"🤖 I'm an assistant for this Telegram bot. You asked: '{user_prompt}'\n\n"
        "I can help you with:\n"
        "• Earthquake information (use /eq_latest, /eq_global, /eq_taiwan)\n"
        "• News updates (use /news, /news_tech, /news_taiwan)\n"
        "• Web search (use /search <query>)\n\n"
        "For earthquake-specific questions, please mention 'earthquake' or '地震' in your question."
    )
    
    return response_text
