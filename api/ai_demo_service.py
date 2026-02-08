"""
AI Demo Service - Manages GitHub Copilot AI productivity tips
Shows 5 practical applications in random order without repetition per user
"""
import random
from typing import Dict, Set

# 5 practical GitHub Copilot AI agent productivity applications
AI_DEMO_TIPS = [
    {
        "title": "1. 智能代碼生成與自動完成",
        "description": """**應用場景：** 快速實現業務邏輯和重複性代碼

**使用方式：**
• 撰寫描述性的註解或函數名稱，Copilot 會自動建議完整的實現
• 範例：輸入 `def calculate_fibonacci(n):` Copilot 會建議完整的斐波那契數列實現
• 可以處理常見的演算法、資料結構和設計模式

**生產力提升：**
✓ 減少 50-70% 的基礎代碼編寫時間
✓ 避免重複造輪子，專注於核心業務邏輯
✓ 自動遵循當前項目的編碼風格和慣例

**實際案例：**
需要實現一個 API 端點時，只需寫註解 "# Create REST API endpoint for user registration"，Copilot 會生成包含驗證、錯誤處理的完整代碼。"""
    },
    {
        "title": "2. 即時代碼審查與錯誤偵測",
        "description": """**應用場景：** 在編碼過程中即時發現潛在問題

**使用方式：**
• Copilot 會分析你的代碼並標記可能的錯誤、安全漏洞或效能問題
• 提供即時的改進建議和最佳實踐
• 自動檢測邏輯錯誤、null 指針、資源洩漏等常見問題

**生產力提升：**
✓ 在撰寫階段就避免 Bug，減少 Debug 時間達 40%
✓ 學習最佳實踐，持續提升代碼質量
✓ 減少代碼審查的往返次數

**實際案例：**
當你忘記關閉文件句柄或資料庫連接時，Copilot 會提醒使用 `with` 語句或 try-finally 塊，確保資源正確釋放。"""
    },
    {
        "title": "3. 智能重構與代碼優化",
        "description": """**應用場景：** 改善既有代碼的結構和性能

**使用方式：**
• 選擇需要重構的代碼區塊，要求 Copilot 提供優化建議
• 使用 Copilot Chat："/explain" 理解代碼，"/fix" 修復問題
• 請求將重複代碼提取為函數或類別

**生產力提升：**
✓ 快速識別並消除代碼異味（Code Smells）
✓ 自動應用設計模式和重構技術
✓ 提升代碼可讀性和可維護性達 60%

**實際案例：**
有一段包含多個巢狀 if-else 的複雜邏輯，詢問 Copilot "How can I refactor this code to use strategy pattern?"，它會提供使用策略模式重構的完整方案。"""
    },
    {
        "title": "4. 多語言與框架快速學習",
        "description": """**應用場景：** 加速學習新技術棧和跨語言開發

**使用方式：**
• 在新語言或框架中，用自然語言描述你想實現的功能
• 詢問 Copilot 特定框架的最佳實踐和慣用模式
• 請求代碼範例和實作指南

**生產力提升：**
✓ 縮短新技術學習曲線達 70%
✓ 快速理解 API 使用方式和框架特性
✓ 跨語言開發時保持高效率

**實際案例：**
從 Python 轉到 Go 語言時，詢問 "How to implement concurrent HTTP requests in Go?"，Copilot 會提供使用 goroutines 和 channels 的地道 Go 代碼範例。"""
    },
    {
        "title": "5. 自動化測試與文檔生成",
        "description": """**應用場景：** 快速建立完整的測試覆蓋和項目文檔

**使用方式：**
• 在函數上方註解 "# Write unit tests for this function"，Copilot 生成測試案例
• 要求生成 README、API 文檔、註解等文檔內容
• 自動生成邊界條件和異常情況的測試

**生產力提升：**
✓ 測試編寫時間減少 60%，覆蓋率提升
✓ 自動生成清晰的文檔和註解
✓ 確保測試的全面性和邊界條件處理

**實際案例：**
寫完一個複雜的資料處理函數後，註解 "# Generate comprehensive unit tests including edge cases"，Copilot 會生成包括空輸入、大數據、異常值等多種測試案例的完整測試套件。"""
    }
]

class AIDemoManager:
    """Manages AI demo tips display with per-user tracking to avoid repetition"""
    
    def __init__(self):
        # Track which tips have been shown to each user
        # Key: user_id/chat_id, Value: set of shown tip indices
        self.user_shown_tips: Dict[str, Set[int]] = {}
    
    def get_random_tip(self, user_id: str) -> str:
        """
        Get a random tip that hasn't been shown to this user yet.
        Resets if all tips have been shown.
        
        Args:
            user_id: Unique identifier for the user/chat
            
        Returns:
            Formatted tip text
        """
        # Initialize user tracking if not exists
        if user_id not in self.user_shown_tips:
            self.user_shown_tips[user_id] = set()
        
        shown_tips = self.user_shown_tips[user_id]
        
        # If all tips shown, reset for this user
        if len(shown_tips) >= len(AI_DEMO_TIPS):
            shown_tips.clear()
        
        # Get list of tips not yet shown
        available_indices = [i for i in range(len(AI_DEMO_TIPS)) if i not in shown_tips]
        
        # Select random tip from available ones
        selected_index = random.choice(available_indices)
        shown_tips.add(selected_index)
        
        # Format and return the tip
        tip = AI_DEMO_TIPS[selected_index]
        result = f"🤖 **GitHub Copilot AI 高生產力應用**\n\n"
        result += f"**{tip['title']}**\n\n"
        result += tip['description']
        result += f"\n\n_已顯示 {len(shown_tips)}/{len(AI_DEMO_TIPS)} 個應用案例_"
        
        return result

# Global instance
ai_demo_manager = AIDemoManager()

def get_ai_demo_tip(user_id: str) -> str:
    """
    Get a random AI demo tip for the user.
    
    Args:
        user_id: Unique identifier for the user/chat
        
    Returns:
        Formatted tip text
    """
    return ai_demo_manager.get_random_tip(user_id)
