import os
import tempfile
from re import split
from datetime import datetime

""" Required """

""" Required """

BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Google Gemini API Key (optional - enables function calling capabilities)
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")

# CWA (Central Weather Administration) API Key for Taiwan earthquake data
CWA_API_KEY = os.environ.get("CWA_API_KEY", "")

# MCP Server URL for earthquake search tool
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "https://cwadayi-mcp-2.hf.space")

# Hugging Face Space URL for keep-alive ping (optional)
HF_SPACE_URL = os.getenv("HF_SPACE_URL", "")

# Static directory for temporary files (e.g., generated maps)
STATIC_DIR = os.getenv("STATIC_DIR", os.path.join(tempfile.gettempdir(), "static"))
os.makedirs(STATIC_DIR, exist_ok=True)

# API Endpoints
CWA_ALARM_API = "https://app-2.cwa.gov.tw/api/v1/earthquake/alarm/list"
CWA_SIGNIFICANT_API = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/E-A0015-001"
USGS_API_BASE_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"

# Current year for display
CURRENT_YEAR = datetime.now().year


""" Optional """

ALLOWED_USERS = split(r'[ ,;，；]+', os.getenv("ALLOWED_USERS", '').replace("@", "").lower())
ALLOWED_GROUPS = split(r'[ ,;，；]+', os.getenv("ALLOWED_GROUPS", '').replace("@", "").lower())

#Whether to push logs and enable some admin commands
IS_DEBUG_MODE = os.getenv("IS_DEBUG_MODE", '0')
#The target account that can execute administrator instructions and log push can use /get_my_info to obtain the ID.
ADMIN_ID = os.getenv("ADMIN_ID", "1234567890")

#Determines whether to verify identity. If 0, anyone can use the bot. It is enabled by default.
AUCH_ENABLE = os.getenv("AUCH_ENABLE", "1")

# API Access Token for webhook endpoint authentication (optional)
# If set, all POST/GET requests to the webhook must include a valid token header
API_ACCESS_TOKEN = os.getenv("API_ACCESS_TOKEN", "")

#"1"to use the same chat history in the group, "2"to record chat history individually for each person
GROUP_MODE = os.getenv("GROUP_MODE=", "1")

#After setting up 3 rounds of dialogue, prompt the user to start a new dialogue
prompt_new_threshold = int(3)

#The default prompt when the photo has no accompanying text
defaut_photo_caption = "描述這張圖片"

""" 以下是使用者相關文字 """
help_text = "您可以傳送文字或圖片給我。傳送圖片時，請在同一則訊息中附上文字說明。\n在群組中使用請 @機器人 或回覆機器人的任何訊息"
command_list = "/new 開始新對話\n/get_my_info 取得個人資訊\n/get_group_info 取得群組資訊（僅群組可用）\n/get_allowed_users 取得允許使用的用戶列表（僅管理員可用）\n/get_allowed_groups 取得允許使用的群組列表（僅管理員可用）\n/help 取得說明"
admin_auch_info = "您不是管理員，或管理員 ID 設定錯誤！"
debug_mode_info = "除錯模式未啟用！"
command_format_error_info = "指令格式錯誤"
command_invalid_error_info = "無效指令，使用 /help 取得說明"
user_no_permission_info = "您沒有使用此機器人的權限。"
group_no_permission_info = "此群組沒有使用此機器人的權限。"
gemini_err_info = f"處理您的請求時發生錯誤，請稍後再試。"
new_chat_info = "我們正在進行一個全新的對話。"
prompt_new_info = "輸入 /new 開始新對話。"
unable_to_recognize_content_sent = "無法識別您傳送的內容！"

""" 以下是紀錄相關文字 """
send_message_log = "傳送訊息，回傳內容為："
send_photo_log = "傳送圖片，回傳內容為："
unnamed_user = "未命名用戶"
unnamed_group = "未命名群組"
event_received = "收到事件"
group = "群組"
the_content_sent_is = "傳送內容為："
the_reply_content_is = "回覆內容為："
the_accompanying_message_is = "附加訊息為："
the_logarithm_of_historical_conversations_is = "歷史對話輪數為："
no_rights_to_use = "無使用權限"
send_unrecognized_content = "傳送了無法識別的內容"


""" read https://ai.google.dev/api/rest/v1/GenerationConfig """
generation_config = {
    "max_output_tokens": 1024,
}

""" read https://ai.google.dev/api/rest/v1/HarmCategory """
safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE"
    },
]
