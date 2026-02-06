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
    SERVICES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Some services not available: {e}")
    SERVICES_AVAILABLE = False


def help():
    base_help = f"{help_text}\n\n{command_list}"
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
        return base_help + earthquake_commands
    return base_help



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
