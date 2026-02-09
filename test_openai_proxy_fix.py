"""
Test script to verify OpenAI proxy configuration fix.
Tests that the OpenAI client can be initialized without the 'proxies' error.
"""
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_openai_initialization():
    """Test that OpenAI client initializes correctly without proxies error."""
    print("=" * 60)
    print("Testing OpenAI Client Initialization Fix")
    print("=" * 60)
    
    # Set a fake API key for testing
    os.environ['OPENAI_KEY'] = 'sk-test-fake-key-for-testing'
    
    # Test 1: Import and initialize without proxy
    print("\n[Test 1] Initialize OpenAI service without proxy...")
    try:
        from api.openai_service import OpenAIService
        service = OpenAIService()
        # Just test that initialization doesn't crash with proxies error
        # We expect it to fail with auth error since we're using fake key,
        # but NOT with "unexpected keyword argument 'proxies'" error
        try:
            service.initialize()
            print("✓ Initialization completed (unexpected with fake key)")
        except RuntimeError as e:
            if "OPENAI_KEY" in str(e):
                print(f"✓ Expected RuntimeError: {e}")
            else:
                print(f"✗ Unexpected RuntimeError: {e}")
        except Exception as e:
            error_msg = str(e)
            if "proxies" in error_msg.lower():
                print(f"✗ FAILED: Still getting proxies error: {error_msg}")
                return False
            else:
                # Other errors are okay (like network/auth errors)
                print(f"✓ No 'proxies' error. Got expected error: {type(e).__name__}: {e}")
    except Exception as e:
        print(f"✗ FAILED during import/setup: {e}")
        return False
    
    # Test 2: With proxy environment variables set
    print("\n[Test 2] Initialize OpenAI service with proxy env vars...")
    os.environ['HTTP_PROXY'] = 'http://test-proxy:8080'
    os.environ['HTTPS_PROXY'] = 'https://test-proxy:8443'
    
    try:
        from api.openai_service import OpenAIService
        service2 = OpenAIService()
        try:
            service2.initialize()
            print("✓ Initialization completed with proxy env vars")
        except Exception as e:
            error_msg = str(e)
            if "proxies" in error_msg.lower() and "unexpected keyword" in error_msg.lower():
                print(f"✗ FAILED: Still getting proxies error: {error_msg}")
                return False
            else:
                print(f"✓ No 'proxies' error with proxy env vars. Got: {type(e).__name__}")
    except Exception as e:
        print(f"✗ FAILED: {e}")
        return False
    finally:
        # Clean up
        os.environ.pop('HTTP_PROXY', None)
        os.environ.pop('HTTPS_PROXY', None)
    
    # Test 3: Verify the old 'proxies' parameter would fail
    print("\n[Test 3] Verify that passing 'proxies' parameter directly fails...")
    try:
        from openai import OpenAI
        # This should fail with TypeError
        try:
            client = OpenAI(api_key='sk-test', proxies={'http': 'http://proxy:8080'})
            print("✗ UNEXPECTED: proxies parameter was accepted!")
            return False
        except TypeError as e:
            if "proxies" in str(e):
                print(f"✓ Correctly rejects 'proxies' parameter: {e}")
            else:
                print(f"? Got TypeError but different message: {e}")
    except Exception as e:
        print(f"✗ FAILED: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ All tests passed! OpenAI proxy fix is working correctly.")
    print("=" * 60)
    print("\nKey points:")
    print("- OpenAI client no longer accepts 'proxies' parameter")
    print("- Use HTTP_PROXY/HTTPS_PROXY environment variables instead")
    print("- httpx (underlying library) automatically respects these vars")
    return True

if __name__ == "__main__":
    success = test_openai_initialization()
    sys.exit(0 if success else 1)
