from time import sleep
import pandas as pd

from .auth import is_admin
from .config import *
from .printLog import send_log
from .telegram import send_message

# Import new services
try:
    from .cwa_service import fetch_cwa_alarm_list, fetch_significant_earthquakes, fetch_latest_significant_earthquake
    from .usgs_service import fetch_global_last24h_text, fetch_taiwan_df_this_year
    from .plotting_service import create_and_save_map
    from .ai_service import generate_ai_text
    from .news_service import (
        fetch_tech_news, fetch_taiwan_news, fetch_global_news, fetch_general_news,
        fetch_tech_news_mcp, fetch_taiwan_news_mcp, fetch_global_news_mcp,
        fetch_cw_news, fetch_gvm_news, fetch_udn_finance_news, fetch_bbc_chinese_news, fetch_finance_news
    )
    SERVICES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Some services not available: {e}")
    SERVICES_AVAILABLE = False

# Import web search service
try:
    from .web_search_service import web_search, format_search_results
    WEB_SEARCH_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Web search service not available: {e}")
    WEB_SEARCH_AVAILABLE = False

# Import MCP web search service
try:
    from .mcp_web_search_service import mcp_web_search, format_mcp_search_results
    from .config import MCP_WEB_SEARCH_URL
    MCP_WEB_SEARCH_AVAILABLE = bool(MCP_WEB_SEARCH_URL)
except ImportError as e:
    print(f"Warning: MCP web search service not available: {e}")
    MCP_WEB_SEARCH_AVAILABLE = False

# Default search engines for MCP web search
DEFAULT_MCP_SEARCH_ENGINES = ["bing", "duckduckgo"]

# Import Copilot service
try:
    from .copilot_service import copilot_chat_sync, clear_copilot_session_sync, COPILOT_AVAILABLE
except ImportError as e:
    print(f"Warning: Copilot service not available: {e}")
    COPILOT_AVAILABLE = False
    # Define stub functions to prevent NameError
    def copilot_chat_sync(chat_id: str, message: str, model: str = "gpt-4o") -> str:
        return "❌ GitHub Copilot SDK is not available."
    def clear_copilot_session_sync(chat_id: str) -> bool:
        return False


def help():
    help_message = f"{help_text}\n\n{command_list}"
    if SERVICES_AVAILABLE:
        earthquake_commands = (
            "\n\nEarthquake Services:\n"
            "/eq_latest - Latest significant earthquake (with image)\n"
            "/eq_global - Global earthquakes in past 24h (USGS)\n"
            "/eq_taiwan - Taiwan earthquakes this year (USGS)\n"
            "/eq_alert - CWA earthquake early warnings\n"
            "/eq_significant - CWA significant earthquakes (past 7 days)\n"
            "/eq_map - Link to earthquake map service\n"
            "/eq_ai <question> - Ask AI about earthquakes"
        )
        news_commands = (
            "\n\nNews Services:\n"
            "/news - General news from multiple sources\n"
            "/news_tech - Technology news (Hacker News)\n"
            "/news_taiwan - Taiwan news (CNA)\n"
            "/news_global - Global news (BBC)\n"
            "/news_finance - Finance news from multiple sources\n"
            "/news_cw - CommonWealth Magazine (天下雜誌)\n"
            "/news_gvm - Global Views Monthly (遠見雜誌)\n"
            "/news_udn - Economic Daily News (經濟日報)\n"
            "/news_bbc_chinese - BBC Chinese (BBC中文網)"
        )
        help_message = help_message + earthquake_commands + news_commands
    
    if WEB_SEARCH_AVAILABLE or MCP_WEB_SEARCH_AVAILABLE:
        web_search_commands = (
            "\n\nWeb Search:\n"
            "/search <query> - Search the web using Bing\n"
            "/websearch <query> - Search the web (alias for /search)"
        )
        if MCP_WEB_SEARCH_AVAILABLE:
            web_search_commands += "\n(Enhanced with MCP web search)"
        help_message = help_message + web_search_commands
    
    if COPILOT_AVAILABLE:
        copilot_commands = (
            "\n\nGitHub Copilot AI:\n"
            "/copilot <message> - Chat with GitHub Copilot AI\n"
            "/copilot_new - Start a new conversation (clear history)\n"
            "/copilot_help - Get help about Copilot features"
        )
        help_message = help_message + copilot_commands
    
    return help_message



def get_my_info(id):
    return f"your telegram id is: `{id}`"

def get_group_info(type, chat_id):
    if type == "supergroup":
        return f"this group id is: `{chat_id}`"
    return "Please use this command in a group"

def get_allowed_users():
    send_log(f"```json\n{ALLOWED_USERS}```")
    return ""

def get_allowed_groups():
    send_log(f"```json\n{ALLOWED_GROUPS}```")
    return ""

def get_API_key():
    send_log(f"```json\n{GOOGLE_API_KEY}```")
    return ""

def get_latest_earthquake():
    """Get the latest significant earthquake with image."""
    if not SERVICES_AVAILABLE:
        return "Earthquake services not available."
    try:
        latest_eq = fetch_latest_significant_earthquake()
        if not latest_eq:
            return "✅ No recent significant earthquake reports."

        mag_str = f"{latest_eq['Magnitude']:.1f}" if latest_eq.get('Magnitude') is not None else "—"
        depth_str = f"{latest_eq['Depth']:.0f}" if latest_eq.get('Depth') is not None else "—"
        
        result = (
            f"🚨 CWA Latest Significant Earthquake\n"
            f"----------------------------------\n"
            f"Time: {latest_eq.get('TimeStr', '—')}\n"
            f"Location: {latest_eq.get('Location', '—')}\n"
            f"Magnitude: M{mag_str} | Depth: {depth_str} km\n"
            f"Report: {latest_eq.get('URL', 'None')}"
        )
        
        if latest_eq.get("ImageURL"):
            result += f"\n\nImage: {latest_eq['ImageURL']}"
        
        return result
    except Exception as e:
        return f"❌ Failed to query latest earthquake: {e}"

def get_global_earthquakes():
    """Get global earthquakes in the past 24 hours."""
    if not SERVICES_AVAILABLE:
        return "Earthquake services not available."
    return fetch_global_last24h_text()

def get_taiwan_earthquakes():
    """Get Taiwan earthquakes this year."""
    if not SERVICES_AVAILABLE:
        return "Earthquake services not available."
    result = fetch_taiwan_df_this_year()
    if isinstance(result, pd.DataFrame):
        count = len(result)
        lines = [f"🇹🇼 Taiwan Area Significant Earthquakes (M≥5.0) This Year ({CURRENT_YEAR}), Total {count} records:", "-" * 20]
        for _, row in result.head(15).iterrows():
            t = row["time_utc"].strftime("%Y-%m-%d %H:%M")
            lines.append(
                f"Magnitude: {row['magnitude']:.1f} | Date/Time: {t} (UTC)\n"
                f"Location: {row['place']}\n"
                f"Report Link: {row.get('url', 'None')}"
            )
        if count > 15:
            lines.append(f"... (plus {count-15} more records)")
        return "\n\n".join(lines)
    else:
        return result

def get_earthquake_alerts():
    """Get CWA earthquake early warnings."""
    if not SERVICES_AVAILABLE:
        return "Earthquake services not available."
    return fetch_cwa_alarm_list(limit=5)

def get_significant_earthquakes():
    """Get CWA significant earthquakes in the past 7 days."""
    if not SERVICES_AVAILABLE:
        return "Earthquake services not available."
    return fetch_significant_earthquakes(limit=5)

def get_earthquake_map():
    """Get link to earthquake map service."""
    return f"🗺️ External Earthquake Query Service\n\nPlease visit:\n{MCP_SERVER_URL}"

def process_earthquake_ai(question: str):
    """Process AI question about earthquakes."""
    if not SERVICES_AVAILABLE:
        return "AI service not available."
    if not question:
        return "Please provide a question, e.g.: /eq_ai What's the highest mountain in Taiwan?"
    return generate_ai_text(question)

def get_news(limit: int = 5):
    """Get general news from multiple sources."""
    if not SERVICES_AVAILABLE:
        return "News service not available."
    return fetch_general_news(limit)

def get_tech_news(limit: int = 5):
    """Get technology news."""
    if not SERVICES_AVAILABLE:
        return "News service not available."
    # Use RSS-only version
    return fetch_tech_news(limit)

def get_taiwan_news(limit: int = 5):
    """Get Taiwan news."""
    if not SERVICES_AVAILABLE:
        return "News service not available."
    # Use RSS-only version
    return fetch_taiwan_news(limit)

def get_global_news(limit: int = 5):
    """Get global news."""
    if not SERVICES_AVAILABLE:
        return "News service not available."
    # Use RSS-only version
    return fetch_global_news(limit)


def get_finance_news(limit: int = 5):
    """Get finance news from multiple sources."""
    if not SERVICES_AVAILABLE:
        return "News service not available."
    return fetch_finance_news(limit)


def get_cw_news(limit: int = 5):
    """Get CommonWealth Magazine news."""
    if not SERVICES_AVAILABLE:
        return "News service not available."
    return fetch_cw_news(limit)


def get_gvm_news(limit: int = 5):
    """Get Global Views Monthly news."""
    if not SERVICES_AVAILABLE:
        return "News service not available."
    return fetch_gvm_news(limit)


def get_udn_finance_news(limit: int = 5):
    """Get Economic Daily News."""
    if not SERVICES_AVAILABLE:
        return "News service not available."
    return fetch_udn_finance_news(limit)


def get_bbc_chinese_news(limit: int = 5):
    """Get BBC Chinese news."""
    if not SERVICES_AVAILABLE:
        return "News service not available."
    return fetch_bbc_chinese_news(limit)

def perform_web_search(query: str):
    """Perform web search."""
    if not query or not query.strip():
        return "Please provide a search query, e.g.: /search Python tutorial"
    
    # Try MCP web search first if available
    if MCP_WEB_SEARCH_AVAILABLE:
        try:
            results = mcp_web_search(query.strip(), limit=5, engines=DEFAULT_MCP_SEARCH_ENGINES)
            if results:
                return format_mcp_search_results(results, query.strip())
        except Exception as e:
            print(f"MCP web search failed: {e}")
    
    # Fallback to built-in web search
    if not WEB_SEARCH_AVAILABLE:
        return "Web search service not available."
    
    try:
        # Perform search with Bing engine (most reliable)
        results = web_search(query.strip(), limit=5, engines=["bing"])
        return format_search_results(results, query.strip())
    except Exception as e:
        return f"❌ Web search failed: {e}"

def copilot_chat(chat_id: str, message: str) -> str:
    """Chat with GitHub Copilot AI."""
    if not COPILOT_AVAILABLE:
        return "❌ GitHub Copilot SDK is not available. Please install it with: pip install github-copilot-sdk"
    
    if not message or not message.strip():
        return "Please provide a message, e.g.: /copilot How do I sort a list in Python?"
    
    try:
        response = copilot_chat_sync(str(chat_id), message.strip())
        return f"🤖 **GitHub Copilot:**\n\n{response}"
    except Exception as e:
        send_log(f"❌ Copilot chat error: {e}")
        return f"❌ Error communicating with Copilot: {str(e)}"

def copilot_new_conversation(chat_id: str) -> str:
    """Start a new Copilot conversation (clear history)."""
    if not COPILOT_AVAILABLE:
        return "❌ GitHub Copilot SDK is not available."
    
    try:
        success = clear_copilot_session_sync(str(chat_id))
        if success:
            return "✅ Started a new conversation. Previous chat history has been cleared."
        else:
            return "✅ Ready for a new conversation."
    except Exception as e:
        send_log(f"❌ Error clearing Copilot session: {e}")
        return f"❌ Error: {str(e)}"

def copilot_help() -> str:
    """Get help about Copilot features."""
    return (
        "🤖 **GitHub Copilot AI Help**\n\n"
        "GitHub Copilot is an AI-powered coding assistant that can help you with:\n\n"
        "• **Programming Questions**: Ask about syntax, algorithms, best practices\n"
        "• **Code Examples**: Request code snippets in any language\n"
        "• **Debugging Help**: Get assistance with error messages and bugs\n"
        "• **Explanations**: Understand complex code or concepts\n"
        "• **General Knowledge**: Ask questions about technology, tools, and more\n\n"
        "**Commands:**\n"
        "/copilot <message> - Ask Copilot anything\n"
        "/copilot_new - Start fresh (clears conversation history)\n"
        "/copilot_help - Show this help message\n\n"
        "**Examples:**\n"
        "• /copilot How do I reverse a string in JavaScript?\n"
        "• /copilot Explain what is a REST API\n"
        "• /copilot Write a Python function to find prime numbers\n\n"
        "**Note:** Conversations are maintained per chat. Use /copilot_new to start over."
    )


def speed_test(id):
    """ This command seems useless, but it must be included in every robot I make. """
    send_message(id, "开始测速")
    sleep(5)
    return "测试完成，您的5G速度为：\n**114514B/s**"

def send_message_test(id, command):
    if not is_admin(id):
        return admin_auch_info
    a = command.find(" ")
    b = command.find(" ", a + 1)
    if a == -1 or b == -1:
        return command_format_error_info
    to_id = command[a+1:b]
    text = command[b+1:]
    try:
        send_message(to_id, text)
    except Exception as e:
        send_log(f"err:\n{e}")
        return
    send_log("success")
    return ""

def excute_command(from_id, command, from_type, chat_id):
    if command.startswith("start") or command.startswith("help"):
        return help()

    elif command.startswith("get_my_info"):
        return get_my_info(from_id)

    elif command.startswith("get_group_info"):
        return get_group_info(from_type, chat_id)

    elif command.startswith("5g_test"):
        return speed_test(chat_id)

    elif command.startswith("send_message"):
        return send_message_test(from_id, command)

    # Earthquake service commands
    elif command.startswith("eq_latest"):
        return get_latest_earthquake()
    
    elif command.startswith("eq_global"):
        return get_global_earthquakes()
    
    elif command.startswith("eq_taiwan"):
        return get_taiwan_earthquakes()
    
    elif command.startswith("eq_alert"):
        return get_earthquake_alerts()
    
    elif command.startswith("eq_significant"):
        return get_significant_earthquakes()
    
    elif command.startswith("eq_map"):
        return get_earthquake_map()
    
    elif command.startswith("eq_ai"):
        # Extract question from command
        question = command[5:].strip()  # Remove "eq_ai" prefix
        return process_earthquake_ai(question)

    # News service commands
    elif command.startswith("news_tech"):
        return get_tech_news()
    
    elif command.startswith("news_taiwan"):
        return get_taiwan_news()
    
    elif command.startswith("news_global"):
        return get_global_news()
    
    elif command.startswith("news_finance"):
        return get_finance_news()
    
    elif command.startswith("news_cw"):
        return get_cw_news()
    
    elif command.startswith("news_gvm"):
        return get_gvm_news()
    
    elif command.startswith("news_udn"):
        return get_udn_finance_news()
    
    elif command.startswith("news_bbc_chinese"):
        return get_bbc_chinese_news()
    
    elif command.startswith("news"):
        return get_news()

    # Web search commands
    elif command.startswith("search") or command.startswith("websearch"):
        # Extract query from command
        if command.startswith("websearch"):
            query = command[9:].strip()  # Remove "websearch" prefix
        else:
            query = command[6:].strip()  # Remove "search" prefix
        return perform_web_search(query)

    # GitHub Copilot commands
    elif command.startswith("copilot_help"):
        return copilot_help()
    
    elif command.startswith("copilot_new"):
        return copilot_new_conversation(chat_id)
    
    elif command.startswith("copilot"):
        # Extract message from command
        message = command[8:].strip()  # Remove "copilot " prefix (7 chars + 1 space)
        return copilot_chat(chat_id, message)

    elif command in ["get_allowed_users", "get_allowed_groups", "get_api_key"]:
        if not is_admin(from_id):
            return admin_auch_info
        if IS_DEBUG_MODE == "0":
            return debug_mode_info

        if command == "get_allowed_users":
            return get_allowed_users()
        elif command == "get_allowed_groups":
            return get_allowed_groups
        elif command == "get_api_key":
            return get_API_key()

    else:
        return command_format_error_info
