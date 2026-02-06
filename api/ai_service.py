# ai_service.py - Enhanced AI service with tool calling
import json
from datetime import datetime
import google.generativeai as genai
from gradio_client import Client

from .config import GOOGLE_API_KEY, MCP_SERVER_URL

# Configure Gemini API key (one-time setup)
if GOOGLE_API_KEY and "YOUR_GEMINI_API_KEY" not in GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

# Tool function for earthquake search
def call_mcp_earthquake_search(
    start_date: str,
    end_date: str,
    min_magnitude: float = 4.5,
    max_magnitude: float = 8.0
) -> str:
    """Search for earthquake events based on specified conditions (time, magnitude) from remote server."""
    try:
        print(f"--- Calling remote earthquake MCP server (triggered by Gemini) ---")
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

# Define tools for Gemini
earthquake_search_tool_declaration = {
    "name": "call_earthquake_search_tool",
    "description": "Search for earthquake events from Taiwan Central Weather Administration's database based on specified conditions (time, location, magnitude, etc.). Defaults to search Taiwan region.",
    "parameters": {
        "type": "OBJECT", "properties": {
            "start_date": {"type": "STRING", "description": "Start date for search (format 'YYYY-MM-DD'). Model should infer this date from user's question, e.g., from 'last year' or '2024' infer '2024-01-01'."},
            "end_date": {"type": "STRING", "description": "End date for search (format 'YYYY-MM-DD'). Model should infer this date from user's question, e.g., from 'yesterday' or '2024' infer '2024-12-31'."},
            "min_magnitude": {"type": "NUMBER", "description": "Minimum earthquake magnitude to search. If user doesn't specify, use default value 4.5."},
            "max_magnitude": {"type": "NUMBER", "description": "Maximum earthquake magnitude to search. Default is 8.0."},
        }, "required": ["start_date", "end_date"]
    }
}

available_tools = {"call_earthquake_search_tool": call_mcp_earthquake_search}

# Create Gemini model
model = None
if GOOGLE_API_KEY and "YOUR_GEMINI_API_KEY" not in GOOGLE_API_KEY:
    try:
        system_instruction = (
            "You are a helpful AI assistant. "
            "You have access to tools. When a tool returns data in JSON format, "
            "you must analyze the JSON data to fully answer the user's question. "
            "For example, if the user asks for the largest earthquake, use the search tool for the relevant date range "
            "and then find the entry with the highest magnitude from the JSON results before answering."
        )
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            tools=[earthquake_search_tool_declaration],
            system_instruction=system_instruction
        )
    except Exception as e:
        print(f"Failed to create Gemini model: {e}")

# Main AI text generation function
def generate_ai_text(user_prompt: str) -> str:
    """Generate AI response with optional tool calling."""
    if not model:
        return "🤖 AI (Gemini) service has not set API key, or key is invalid."
    try:
        print(f"--- Starting Gemini conversation, user input: '{user_prompt}' ---")
        chat = model.start_chat()
        response = chat.send_message(user_prompt)
        try:
            function_call = response.candidates[0].content.parts[0].function_call
        except (IndexError, AttributeError):
            function_call = None
        if not function_call:
            print("--- Gemini responded with text directly ---")
            return response.text
        
        print(f"--- Gemini requested tool call: {function_call.name} ---")
        tool_function = available_tools.get(function_call.name)
        if not tool_function:
            return f"Error: Model attempted to call a non-existent tool '{function_call.name}'."
        
        tool_result = tool_function(**dict(function_call.args))
        print("--- Returning tool result to Gemini ---")
        
        # Send function response back to Gemini
        response = chat.send_message(
            {"function_response": {"name": function_call.name, "response": {"result": tool_result}}}
        )
        
        print("--- Gemini generated final response based on tool result ---")
        return response.text
    except Exception as e:
        print(f"Error during Gemini AI interaction: {e}")
        return f"🤖 AI service error: {e}"
