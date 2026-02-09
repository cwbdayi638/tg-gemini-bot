from time import sleep
import pandas as pd

from .auth import is_admin
from .config import *
from .printLog import send_log
from .telegram import send_message

# Import new services
try:
    from .cwa_service import fetch_cwa_alarm_list, fetch_significant_earthquakes, fetch_latest_significant_earthquake
    from .usgs_service import fetch_global_last24h_text, fetch_taiwan_df_this_year, fetch_global_earthquakes_by_date
    from .plotting_service import create_and_save_map, create_global_earthquake_map
    from .ai_service import generate_ai_text
    SERVICES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Some services not available: {e}")
    SERVICES_AVAILABLE = False

# Import Taiwan earthquake catalog service
try:
    from .taiwan_eq_service import fetch_taiwan_eq_data, filter_taiwan_eq, format_taiwan_eq_text
    from .taiwan_eq_plotting import create_taiwan_eq_map
    TW_EQ_SERVICE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Taiwan earthquake catalog service not available: {e}")
    TW_EQ_SERVICE_AVAILABLE = False

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


def help():
    help_message = f"{help_text}\n\n{command_list}"
    if SERVICES_AVAILABLE:
        earthquake_commands = (
            "\n\n🌍 地震資訊服務：\n"
            "/eq_latest - 最新顯著地震報告（含圖片）\n"
            "/eq_global - 全球近 24 小時地震（USGS）\n"
            "/eq_taiwan - 台灣今年地震列表（USGS）\n"
            "/eq_alert - 中央氣象署地震速報\n"
            "/eq_significant - 中央氣象署過去 7 天顯著地震\n"
            "/eq_map - 地震查詢服務連結\n"
            "/eq_ai <問題> - AI 智慧地震查詢\n"
            "/eq_query <起始日期> <結束日期> <最小規模> - 查詢全球地震\n"
            "  範例：/eq_query 2024-07-01 2024-07-07 5.0\n"
            "/eq_tw_query <條件> - 台灣地震目錄查詢（含地圖）\n"
            "  範例：/eq_tw_query 2024-01-01 2024-06-30 4.5\n"
            "  格式：起始日期 結束日期 [最小規模] [最大規模] [最小深度] [最大深度]"
        )
        help_message = help_message + earthquake_commands
    
    if WEB_SEARCH_AVAILABLE or MCP_WEB_SEARCH_AVAILABLE:
        web_search_commands = (
            "\n\n🔍 網頁搜尋：\n"
            "/search <關鍵字> - 搜尋網頁\n"
            "/websearch <關鍵字> - 搜尋網頁（別名）"
        )
        if MCP_WEB_SEARCH_AVAILABLE:
            web_search_commands += "\n（已啟用 MCP 增強搜尋）"
        help_message = help_message + web_search_commands
    
    return help_message



def get_my_info(id):
    return f"您的 Telegram ID 是：`{id}`"

def get_group_info(type, chat_id):
    if type == "supergroup":
        return f"此群組 ID 是：`{chat_id}`"
    return "請在群組中使用此指令"

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
    """取得最新的顯著地震資訊（含圖片）。"""
    if not SERVICES_AVAILABLE:
        return "地震資訊服務無法使用。"
    try:
        latest_eq = fetch_latest_significant_earthquake()
        if not latest_eq:
            return "✅ 目前沒有最新的顯著地震報告。"

        mag_str = f"{latest_eq['Magnitude']:.1f}" if latest_eq.get('Magnitude') is not None else "—"
        depth_str = f"{latest_eq['Depth']:.0f}" if latest_eq.get('Depth') is not None else "—"
        
        result = (
            f"🚨 中央氣象署最新顯著地震\n"
            f"----------------------------------\n"
            f"時間：{latest_eq.get('TimeStr', '—')}\n"
            f"位置：{latest_eq.get('Location', '—')}\n"
            f"規模：M{mag_str} | 深度：{depth_str} 公里\n"
            f"報告：{latest_eq.get('URL', '無')}"
        )
        
        if latest_eq.get("ImageURL"):
            result += f"\n\n圖片：{latest_eq['ImageURL']}"
        
        return result
    except Exception as e:
        return f"❌ 查詢最新地震失敗：{e}"

def get_global_earthquakes():
    """取得全球近 24 小時的地震資訊。"""
    if not SERVICES_AVAILABLE:
        return "地震資訊服務無法使用。"
    return fetch_global_last24h_text()

def get_taiwan_earthquakes():
    """取得台灣今年的地震資訊。"""
    if not SERVICES_AVAILABLE:
        return "地震資訊服務無法使用。"
    result = fetch_taiwan_df_this_year()
    if isinstance(result, pd.DataFrame):
        count = len(result)
        lines = [f"🇹🇼 台灣地區今年顯著地震（M≥5.0），共 {count} 筆記錄（{CURRENT_YEAR}）：", "-" * 20]
        for _, row in result.head(15).iterrows():
            t = row["time_utc"].strftime("%Y-%m-%d %H:%M")
            lines.append(
                f"規模：{row['magnitude']:.1f} | 時間：{t} (UTC)\n"
                f"位置：{row['place']}\n"
                f"報告連結：{row.get('url', '無')}"
            )
        if count > 15:
            lines.append(f"...（另有 {count-15} 筆記錄）")
        return "\n\n".join(lines)
    else:
        return result

def get_earthquake_alerts():
    """取得中央氣象署地震速報。"""
    if not SERVICES_AVAILABLE:
        return "地震資訊服務無法使用。"
    return fetch_cwa_alarm_list(limit=5)

def get_significant_earthquakes():
    """取得中央氣象署過去 7 天的顯著地震。"""
    if not SERVICES_AVAILABLE:
        return "地震資訊服務無法使用。"
    return fetch_significant_earthquakes(limit=5)

def get_earthquake_map():
    """取得地震查詢服務連結。"""
    return f"🗺️ 外部地震查詢服務\n\n請造訪：\n{MCP_SERVER_URL}"

def process_earthquake_ai(question: str):
    """處理 AI 地震查詢。"""
    if not SERVICES_AVAILABLE:
        return "AI 服務無法使用。"
    if not question:
        return "請提供問題，例如：/eq_ai 台灣最高的山是什麼？"
    return generate_ai_text(question)

def process_earthquake_query(args: str, chat_id=None):
    """處理全球地震查詢，並生成震央地圖。"""
    if not SERVICES_AVAILABLE:
        return "地震資訊服務無法使用。"
    
    if not args or not args.strip():
        return (
            "請提供查詢參數：起始日期、結束日期、最小規模\n\n"
            "格式：/eq_query <起始日期> <結束日期> <最小規模>\n"
            "範例：/eq_query 2024-07-01 2024-07-07 5.0\n\n"
            "說明：\n"
            "- 日期格式：YYYY-MM-DD\n"
            "- 規模範圍：0-10"
        )
    
    parts = args.strip().split()
    if len(parts) < 3:
        return (
            "參數不足！需要提供：起始日期、結束日期、最小規模\n\n"
            "格式：/eq_query <起始日期> <結束日期> <最小規模>\n"
            "範例：/eq_query 2024-07-01 2024-07-07 5.0"
        )
    
    start_date = parts[0]
    end_date = parts[1]
    min_magnitude = parts[2]
    
    text, earthquakes = fetch_global_earthquakes_by_date(start_date, end_date, min_magnitude)
    
    # Generate and send epicenter map if we have data and a chat_id
    if earthquakes and chat_id:
        try:
            from .telegram import send_photo_file
            min_mag = float(min_magnitude)
            filepath = create_global_earthquake_map(earthquakes, start_date, end_date, min_mag)
            if filepath:
                send_photo_file(chat_id, filepath, caption=f"🗺️ 震央分布圖 {start_date} ~ {end_date} (M≥{min_mag})")
        except Exception as e:
            print(f"Failed to generate/send earthquake map: {e}")
    
    return text

def process_taiwan_eq_query(args: str, chat_id=None):
    """處理台灣地震目錄查詢（含 Plotly 地圖）。

    格式: /eq_tw_query <起始日期> <結束日期> [最小規模] [最大規模] [最小深度] [最大深度]
    範例: /eq_tw_query 2024-01-01 2024-06-30 4.5
    """
    if not TW_EQ_SERVICE_AVAILABLE:
        return "台灣地震目錄查詢服務無法使用。"

    if not args or not args.strip():
        return (
            "📖 台灣地震目錄查詢\n\n"
            "格式：/eq_tw_query <起始日期> <結束日期> [最小規模] [最大規模] [最小深度] [最大深度]\n\n"
            "範例：\n"
            "  /eq_tw_query 2024-01-01 2024-06-30\n"
            "  /eq_tw_query 2024-01-01 2024-03-31 4.5\n"
            "  /eq_tw_query 2024-01-01 2024-12-31 4.0 6.0 0 100\n\n"
            "說明：\n"
            "  - 日期格式：YYYY-MM-DD\n"
            "  - 規模與深度為可選參數\n"
            "  - 資料來源：CWA 台灣地震目錄"
        )

    parts = args.strip().split()
    if len(parts) < 2:
        return (
            "參數不足！至少需要提供起始日期與結束日期。\n\n"
            "格式：/eq_tw_query <起始日期> <結束日期> [最小規模] [最大規模] [最小深度] [最大深度]\n"
            "範例：/eq_tw_query 2024-01-01 2024-06-30 4.5"
        )

    start_date = parts[0]
    end_date = parts[1]
    try:
        min_ml = float(parts[2]) if len(parts) > 2 else None
        max_ml = float(parts[3]) if len(parts) > 3 else None
        min_depth = float(parts[4]) if len(parts) > 4 else None
        max_depth = float(parts[5]) if len(parts) > 5 else None
    except ValueError:
        return "❌ 數值參數格式錯誤！規模與深度請輸入數字（例如：4.5）"

    # Validate dates
    from datetime import datetime as _dt
    try:
        sd = _dt.strptime(start_date, "%Y-%m-%d")
        ed = _dt.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        return "❌ 日期格式錯誤！請使用 YYYY-MM-DD（例如：2024-01-01）"
    if sd > ed:
        return "❌ 起始日期不能晚於結束日期。"

    # Fetch & filter
    try:
        df = fetch_taiwan_eq_data()
    except RuntimeError as e:
        return f"❌ {e}"

    df = filter_taiwan_eq(
        df,
        start_date=start_date,
        end_date=end_date,
        min_ml=min_ml,
        max_ml=max_ml,
        min_depth=min_depth,
        max_depth=max_depth,
    )

    # Build filter description
    desc_parts = [f"{start_date} ~ {end_date}"]
    if min_ml is not None:
        desc_parts.append(f"ML≥{min_ml}")
    if max_ml is not None:
        desc_parts.append(f"ML≤{max_ml}")
    if min_depth is not None:
        desc_parts.append(f"深度≥{min_depth}km")
    if max_depth is not None:
        desc_parts.append(f"深度≤{max_depth}km")
    filters_desc = "，".join(desc_parts)

    text = format_taiwan_eq_text(df, filters_desc)

    # Generate Plotly map and send as photo
    if not df.empty and chat_id:
        try:
            from .telegram import send_photo_file
            title = f"台灣地震分布圖（{filters_desc}）"
            filepath = create_taiwan_eq_map(df, title=title)
            if filepath:
                send_photo_file(chat_id, filepath, caption=f"🗺️ {title}")
        except Exception as e:
            print(f"Failed to generate/send Taiwan earthquake map: {e}")

    return text

def perform_web_search(query: str):
    """執行網頁搜尋。"""
    if not query or not query.strip():
        return "請提供搜尋關鍵字，例如：/search Python 教學"
    
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
        return "網頁搜尋服務無法使用。"
    
    try:
        # Perform search with Bing engine (most reliable)
        results = web_search(query.strip(), limit=5, engines=["bing"])
        return format_search_results(results, query.strip())
    except Exception as e:
        return f"❌ 網頁搜尋失敗：{e}"


def speed_test(id):
    """速度測試指令（彩蛋）。"""
    send_message(id, "開始測速")
    sleep(5)
    return "測試完成，您的 5G 速度為：\n**114514B/s**"

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

    # 地震資訊服務指令
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
        # 擷取問題
        question = command[5:].strip()  # 移除 "eq_ai" 前綴
        return process_earthquake_ai(question)
    
    elif command.startswith("eq_query"):
        # 擷取查詢參數
        args = command[8:].strip()  # 移除 "eq_query" 前綴
        return process_earthquake_query(args, chat_id=chat_id)

    elif command.startswith("eq_tw_query"):
        # 台灣地震目錄查詢
        args = command[11:].strip()  # 移除 "eq_tw_query" 前綴
        return process_taiwan_eq_query(args, chat_id=chat_id)

    # 網頁搜尋指令
    elif command.startswith("search") or command.startswith("websearch"):
        # 擷取搜尋關鍵字
        if command.startswith("websearch"):
            query = command[9:].strip()  # 移除 "websearch" 前綴
        else:
            query = command[6:].strip()  # 移除 "search" 前綴
        return perform_web_search(query)

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
