"""
Test script to verify all news functions are working correctly.
This script tests that the news service functions properly handle RSS feeds
and return appropriate responses even when network access is restricted.
"""

def test_news_service_imports():
    """Test that all news service functions can be imported."""
    try:
        from api.news_service import (
            fetch_tech_news, fetch_taiwan_news, fetch_global_news, fetch_general_news,
            fetch_cw_news, fetch_gvm_news, fetch_udn_finance_news, 
            fetch_bbc_chinese_news, fetch_finance_news
        )
        print("✅ All news_service functions imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import news_service functions: {e}")
        return False


def test_command_imports():
    """Test that all command functions can be imported."""
    try:
        from api.command import (
            get_tech_news, get_taiwan_news, get_global_news, get_news,
            get_finance_news, get_cw_news, get_gvm_news, 
            get_udn_finance_news, get_bbc_chinese_news
        )
        print("✅ All command news functions imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import command functions: {e}")
        return False


def test_news_functions_execution():
    """Test that all news functions execute without errors."""
    from api.news_service import (
        fetch_tech_news, fetch_taiwan_news, fetch_global_news, fetch_general_news,
        fetch_cw_news, fetch_gvm_news, fetch_udn_finance_news, 
        fetch_bbc_chinese_news, fetch_finance_news
    )
    
    functions = [
        ('Tech News', fetch_tech_news),
        ('Taiwan News', fetch_taiwan_news),
        ('Global News', fetch_global_news),
        ('General News', fetch_general_news),
        ('CW News', fetch_cw_news),
        ('GVM News', fetch_gvm_news),
        ('UDN Finance', fetch_udn_finance_news),
        ('BBC Chinese', fetch_bbc_chinese_news),
        ('Finance News', fetch_finance_news),
    ]
    
    all_passed = True
    for name, func in functions:
        try:
            result = func(limit=1)
            if isinstance(result, str) and len(result) > 0:
                print(f"✅ {name} function works correctly")
            else:
                print(f"❌ {name} function returned invalid result")
                all_passed = False
        except Exception as e:
            print(f"❌ {name} function failed: {e}")
            all_passed = False
    
    return all_passed


def test_command_routing():
    """Test that command routing works for news commands."""
    from api.command import excute_command
    
    commands = [
        'news', 'news_tech', 'news_taiwan', 'news_global', 'news_finance',
        'news_cw', 'news_gvm', 'news_udn', 'news_bbc_chinese'
    ]
    
    all_passed = True
    for cmd in commands:
        try:
            result = excute_command(
                from_id='test_user', 
                command=cmd, 
                from_type='private', 
                chat_id='test_chat'
            )
            if isinstance(result, str) and len(result) > 0:
                print(f"✅ Command /{cmd} routes correctly")
            else:
                print(f"❌ Command /{cmd} returned invalid result")
                all_passed = False
        except Exception as e:
            print(f"❌ Command /{cmd} failed: {e}")
            all_passed = False
    
    return all_passed


def test_dependencies():
    """Test that all required dependencies are installed."""
    dependencies = [
        ('feedparser', 'feedparser'),
        ('beautifulsoup4', 'bs4'),
        ('lxml', 'lxml'),
        ('requests', 'requests'),
        ('pandas', 'pandas'),
    ]
    
    all_installed = True
    for name, import_name in dependencies:
        try:
            __import__(import_name)
            print(f"✅ {name} is installed")
        except ImportError:
            print(f"❌ {name} is NOT installed")
            all_installed = False
    
    return all_installed


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing News Functions")
    print("=" * 60)
    
    tests = [
        ("Dependencies Check", test_dependencies),
        ("News Service Imports", test_news_service_imports),
        ("Command Imports", test_command_imports),
        ("News Functions Execution", test_news_functions_execution),
        ("Command Routing", test_command_routing),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    all_passed = all(result for _, result in results)
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED - News functions are working correctly!")
    else:
        print("❌ SOME TESTS FAILED - Please check the errors above")
    print("=" * 60)
    
    return all_passed


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
