"""
GitHub Copilot SDK service for Telegram bot.
Provides AI-powered conversation capabilities using GitHub Copilot.
"""
import asyncio
import os
import stat
from pathlib import Path
from typing import Optional
from .printLog import send_log

# Try to import copilot SDK
# Note: The package is 'github-copilot-sdk' but imports as 'copilot'
try:
    from copilot import CopilotClient
    COPILOT_AVAILABLE = True
except ImportError:
    COPILOT_AVAILABLE = False
    print("Warning: GitHub Copilot SDK not available. Install with: pip install github-copilot-sdk")


def _fix_copilot_binary_permissions():
    """
    Fix permissions for the Copilot CLI binary bundled with the SDK.
    The github-copilot-sdk package includes a binary that may not have execute permissions.
    This function ensures the binary is executable before attempting to use it.
    """
    if not COPILOT_AVAILABLE:
        return False
    
    try:
        import copilot
        copilot_pkg_dir = Path(copilot.__file__).parent
        copilot_binary = copilot_pkg_dir / "bin" / "copilot"
        
        if copilot_binary.exists():
            current_permissions = copilot_binary.stat().st_mode
            # Check if executable bit is not set for user
            if not (current_permissions & stat.S_IXUSR):
                # Add execute permissions for user, group, and others
                new_permissions = current_permissions | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
                copilot_binary.chmod(new_permissions)
                send_log(f"✅ Fixed Copilot binary permissions: {copilot_binary}")
                return True
            return True  # Already executable
        else:
            send_log(f"⚠️  Copilot binary not found at expected location: {copilot_binary}")
            return False
    except Exception as e:
        send_log(f"⚠️  Could not fix Copilot binary permissions: {e}")
        return False


class CopilotService:
    """Service for managing GitHub Copilot SDK interactions."""
    
    def __init__(self):
        self.client: Optional[CopilotClient] = None
        self.sessions = {}  # Store sessions by chat_id
        self._initialized = False
    
    async def initialize(self):
        """Initialize the Copilot client."""
        if not COPILOT_AVAILABLE:
            raise RuntimeError("GitHub Copilot SDK is not available")
        
        if self._initialized:
            return
        
        try:
            # Fix binary permissions before initializing
            _fix_copilot_binary_permissions()
            
            # Create and start the Copilot client
            self.client = CopilotClient({
                "log_level": "info",
                "auto_start": True,
                "auto_restart": True,
            })
            await self.client.start()
            self._initialized = True
            send_log("✅ Copilot SDK initialized successfully")
        except PermissionError as e:
            error_msg = (
                f"❌ Permission error with Copilot binary: {e}\n"
                "This may happen if the github-copilot-sdk binary doesn't have execute permissions.\n"
                "Try running: pip install --force-reinstall github-copilot-sdk"
            )
            send_log(error_msg)
            raise RuntimeError(error_msg) from e
        except Exception as e:
            send_log(f"❌ Failed to initialize Copilot SDK: {e}")
            raise
    
    async def get_or_create_session(self, chat_id: str, model: str = "gpt-4o"):
        """Get or create a session for a chat."""
        if not self._initialized:
            await self.initialize()
        
        # Check if session exists and is still valid
        if chat_id in self.sessions:
            return self.sessions[chat_id]
        
        try:
            # Create a new session
            session = await self.client.create_session({
                "model": model,
                "streaming": False,  # We'll use non-streaming for simplicity
            })
            self.sessions[chat_id] = session
            return session
        except Exception as e:
            send_log(f"❌ Failed to create Copilot session: {e}")
            raise
    
    async def chat(self, chat_id: str, prompt: str, model: str = "gpt-4o") -> str:
        """
        Send a prompt to Copilot and get the response.
        
        Args:
            chat_id: Unique identifier for the chat session
            prompt: User's message/question
            model: Model to use (default: gpt-4o)
        
        Returns:
            AI response text
        """
        try:
            session = await self.get_or_create_session(chat_id, model)
            
            # Get the current event loop for this async context
            loop = asyncio.get_running_loop()
            
            # Event to signal completion (explicitly tied to this loop)
            done = asyncio.Event()
            response_text = []
            error_occurred = False
            error_message = None
            
            def on_event(event):
                nonlocal error_occurred, error_message
                try:
                    if event.type.value == "assistant.message":
                        response_text.append(event.data.content)
                    elif event.type.value == "session.idle":
                        # Use call_soon_threadsafe to safely set the event from any thread
                        loop.call_soon_threadsafe(done.set)
                    elif event.type.value == "error":
                        error_occurred = True
                        error_message = str(event.data) if hasattr(event, 'data') else "Unknown error"
                        # Use call_soon_threadsafe to safely set the event from any thread
                        loop.call_soon_threadsafe(done.set)
                except Exception as e:
                    error_occurred = True
                    error_message = str(e)
                    # Use call_soon_threadsafe to safely set the event from any thread
                    loop.call_soon_threadsafe(done.set)
            
            # Register event handler
            session.on(on_event)
            
            # Send the prompt
            await session.send({"prompt": prompt})
            
            # Wait for completion with timeout
            try:
                await asyncio.wait_for(done.wait(), timeout=60.0)
            except asyncio.TimeoutError:
                return "⏱️ Request timed out. Please try again."
            
            if error_occurred:
                return f"❌ Error: {error_message or 'Unknown error occurred'}"
            
            if response_text:
                return response_text[0]
            else:
                return "❌ No response received from Copilot"
                
        except PermissionError as e:
            send_log(f"❌ Copilot permission error: {e}")
            return (
                "❌ Error: Permission denied when accessing Copilot binary.\n"
                "The fix has been applied. Please try the command again.\n"
                "If the issue persists, contact the bot administrator."
            )
        except Exception as e:
            send_log(f"❌ Copilot chat error: {e}")
            # Check if it's a permission-related error in the message
            error_str = str(e)
            if "Permission denied" in error_str or "Errno 13" in error_str:
                return (
                    "❌ Error: Permission denied when accessing Copilot binary.\n"
                    "The fix has been applied. Please try the command again.\n"
                    "If the issue persists, contact the bot administrator."
                )
            return f"❌ Error communicating with Copilot: {error_str}"
    
    async def clear_session(self, chat_id: str):
        """Clear/delete a session for a specific chat."""
        if chat_id in self.sessions:
            try:
                session = self.sessions[chat_id]
                await session.destroy()
                del self.sessions[chat_id]
                return True
            except Exception as e:
                send_log(f"❌ Failed to clear Copilot session: {e}")
                return False
        return False
    
    async def shutdown(self):
        """Shutdown the Copilot client and clean up all sessions."""
        if not self._initialized:
            return
        
        try:
            # Destroy all sessions
            for chat_id in list(self.sessions.keys()):
                await self.clear_session(chat_id)
            
            # Stop the client
            if self.client:
                await self.client.stop()
                self.client = None
            
            self._initialized = False
            send_log("✅ Copilot SDK shutdown complete")
        except Exception as e:
            send_log(f"❌ Error during Copilot shutdown: {e}")


# Global service instance
_copilot_service = None


def get_copilot_service() -> CopilotService:
    """Get the global Copilot service instance."""
    global _copilot_service
    if _copilot_service is None:
        _copilot_service = CopilotService()
    return _copilot_service


def _run_async_in_sync(coro):
    """
    Helper function to run async code in a sync context.
    Ensures proper event loop management to prevent event loop conflicts.
    """
    try:
        # Try to get the existing event loop
        loop = asyncio.get_event_loop()
        # Check if the loop is closed or if we're in a different thread's loop
        if loop.is_closed():
            # If closed, create a new one and set it
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        # Check if loop is already running (e.g., in Jupyter or async context)
        elif loop.is_running():
            # If the loop is running, create a new event loop and run the coroutine there
            # This can happen if called from within another async context
            loop = asyncio.new_event_loop()
            try:
                return loop.run_until_complete(coro)
            finally:
                loop.close()
        return loop.run_until_complete(coro)
    except RuntimeError as e:
        # If there's no event loop in this thread, create one
        # This catches the specific case: "There is no current event loop in thread"
        error_str = str(e).lower()
        if "no current event loop" in error_str or "no running event loop" in error_str:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(coro)
        # Re-raise if it's a different RuntimeError
        raise


def copilot_chat_sync(chat_id: str, prompt: str, model: str = "gpt-4o") -> str:
    """
    Synchronous wrapper for Copilot chat.
    This function handles async operations in a sync context.
    """
    if not COPILOT_AVAILABLE:
        return "❌ GitHub Copilot SDK is not installed. Please install it with: pip install github-copilot-sdk"
    
    try:
        service = get_copilot_service()
        return _run_async_in_sync(service.chat(chat_id, prompt, model))
    except Exception as e:
        send_log(f"❌ Copilot sync chat error: {e}")
        return f"❌ Error: {str(e)}"


def clear_copilot_session_sync(chat_id: str) -> bool:
    """Synchronous wrapper for clearing a Copilot session."""
    if not COPILOT_AVAILABLE:
        return False
    
    try:
        service = get_copilot_service()
        return _run_async_in_sync(service.clear_session(chat_id))
    except Exception as e:
        send_log(f"❌ Error clearing Copilot session: {e}")
        return False
