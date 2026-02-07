#!/usr/bin/env python3
"""
Simple test script to verify Copilot integration can be imported.
This is a basic smoke test to ensure the module structure is correct.

Note: This does not actually test the Copilot SDK functionality as that
requires the GitHub Copilot CLI to be installed and authenticated.
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that modules can be imported."""
    print("Testing module imports...")
    
    try:
        from api import copilot_service
        print("✅ Successfully imported copilot_service")
        print(f"   COPILOT_AVAILABLE: {copilot_service.COPILOT_AVAILABLE}")
        
        # Test that classes and functions exist
        assert hasattr(copilot_service, 'CopilotService'), "CopilotService class not found"
        assert hasattr(copilot_service, 'copilot_chat_sync'), "copilot_chat_sync function not found"
        assert hasattr(copilot_service, 'clear_copilot_session_sync'), "clear_copilot_session_sync function not found"
        assert hasattr(copilot_service, 'get_copilot_service'), "get_copilot_service function not found"
        print("✅ All expected classes and functions are present")
        
    except Exception as e:
        print(f"❌ Failed to import copilot_service: {e}")
        return False
    
    try:
        from api import command
        print("✅ Successfully imported command module")
        
        # Check that Copilot-related functions exist
        assert hasattr(command, 'copilot_chat'), "copilot_chat function not found"
        assert hasattr(command, 'copilot_new_conversation'), "copilot_new_conversation function not found"
        assert hasattr(command, 'copilot_help'), "copilot_help function not found"
        print("✅ All Copilot command handlers are present")
        
    except Exception as e:
        print(f"❌ Failed to import command module: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_stub_functions():
    """Test that stub functions work when SDK is not available."""
    print("\nTesting stub functions...")
    
    try:
        from api.copilot_service import COPILOT_AVAILABLE
        if not COPILOT_AVAILABLE:
            print("⚠️  Copilot SDK not available, testing stub functions...")
            from api.command import copilot_chat_sync, clear_copilot_session_sync
            
            # Test stub functions don't raise errors
            result = copilot_chat_sync("test_chat", "test message")
            assert isinstance(result, str), "copilot_chat_sync should return string"
            print(f"   copilot_chat_sync returned: {result[:50]}...")
            
            result = clear_copilot_session_sync("test_chat")
            assert isinstance(result, bool), "clear_copilot_session_sync should return bool"
            print(f"   clear_copilot_session_sync returned: {result}")
            
            print("✅ Stub functions work correctly")
        else:
            print("ℹ️  Copilot SDK is available, skipping stub function tests")
    except Exception as e:
        print(f"❌ Stub function test failed: {e}")
        return False
    
    return True

def test_help_text():
    """Test that help text includes Copilot commands."""
    print("\nTesting help text...")
    
    try:
        from api.command import help, COPILOT_AVAILABLE
        help_text = help()
        
        if COPILOT_AVAILABLE:
            assert "copilot" in help_text.lower(), "Help text should include copilot commands when available"
            print("✅ Help text includes Copilot commands")
        else:
            print("ℹ️  Copilot SDK not available, help text may not include Copilot commands")
        
        print(f"   Help text length: {len(help_text)} characters")
    except Exception as e:
        print(f"❌ Help text test failed: {e}")
        return False
    
    return True

def main():
    """Run all tests."""
    print("=" * 60)
    print("Copilot Integration Smoke Tests")
    print("=" * 60)
    
    results = []
    
    results.append(("Import Test", test_imports()))
    results.append(("Stub Functions Test", test_stub_functions()))
    results.append(("Help Text Test", test_help_text()))
    
    print("\n" + "=" * 60)
    print("Test Results:")
    print("=" * 60)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
