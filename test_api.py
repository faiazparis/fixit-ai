#!/usr/bin/env python3
"""
🧪 iFixit Repair Guide API - Test Suite
Comprehensive testing for all API endpoints and functionality.
"""

import requests
import json
import sys
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
TIMEOUT = 15  # Increased timeout for better reliability

def print_header(title):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")

def print_section(title):
    """Print a formatted section."""
    print(f"\n📋 {title}")
    print(f"{'-'*40}")

def test_endpoint(endpoint, method="GET", data=None, description="", expected_status=200):
    """Test an API endpoint and return the result."""
    url = f"{BASE_URL}{endpoint}"
    
    print(f"  🔗 {method} {endpoint}")
    if description:
        print(f"     📝 {description}")
    
    try:
        start_time = time.time()
        
        if method == "GET":
            response = requests.get(url, timeout=TIMEOUT)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=TIMEOUT)
        else:
            print(f"     ❌ Unsupported method: {method}")
            return False
        
        elapsed = time.time() - start_time
        
        if response.status_code == expected_status:
            print(f"     ✅ Success ({response.status_code}) - {elapsed:.2f}s")
            
            # Show response preview for successful requests
            if response.status_code == 200 and response.content:
                try:
                    json_data = response.json()
                    if isinstance(json_data, dict):
                        if 'total_results' in json_data:
                            print(f"     📊 Found {json_data['total_results']} results")
                        elif 'status' in json_data:
                            print(f"     💚 Status: {json_data['status']}")
                        elif 'categories' in json_data:
                            categories = list(json_data['categories'].keys())
                            print(f"     📱 Categories: {', '.join(categories)}")
                except:
                    pass
            
            return True
        else:
            print(f"     ❌ Failed ({response.status_code}) - {elapsed:.2f}s")
            if response.text:
                print(f"     📄 Response: {response.text[:200]}...")
            return False
            
    except requests.exceptions.Timeout:
        print(f"     ⏰ Timeout after {TIMEOUT}s")
        return False
    except requests.exceptions.ConnectionError:
        print(f"     🔌 Connection error - server not running?")
        return False
    except Exception as e:
        print(f"     ❌ Error: {str(e)}")
        return False

def check_server_status():
    """Check if the server is running and healthy."""
    print_header("SERVER STATUS CHECK")
    
    try:
        print("  🔍 Checking server availability...")
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Server is running!")
            print(f"     💚 Status: {data.get('status', 'unknown')}")
            print(f"     📅 Version: {data.get('version', 'unknown')}")
            print(f"     🕐 Timestamp: {data.get('timestamp', 'unknown')}")
            return True
        else:
            print(f"  ❌ Server responded but health check failed ({response.status_code})")
            return False
            
    except requests.exceptions.ConnectionError:
        print("  ❌ Server is not running!")
        print("     💡 Start the server with: python app.py")
        return False
    except Exception as e:
        print(f"  ❌ Error checking server: {e}")
        return False

def run_basic_tests():
    """Run basic API functionality tests."""
    print_header("BASIC FUNCTIONALITY TESTS")
    
    tests = [
        # Info endpoints
        ("/", "GET", None, "API information", 200),
        ("/health", "GET", None, "Health check", 200),
        ("/popular", "GET", None, "Popular devices", 200),
        
        # Search endpoints
        ("/search?q=iPhone%2014&max_results=3", "GET", None, "Search iPhone 14", 200),
        ("/search?q=Samsung%20Galaxy&max_results=2", "GET", None, "Search Samsung Galaxy", 200),
        ("/search?q=MacBook&max_results=1", "GET", None, "Search MacBook", 200),
    ]
    
    passed = 0
    total = len(tests)
    
    for endpoint, method, data, description, expected_status in tests:
        if test_endpoint(endpoint, method, data, description, expected_status):
            passed += 1
    
    return passed, total

def run_advanced_tests():
    """Run advanced API functionality tests."""
    print_header("ADVANCED FUNCTIONALITY TESTS")
    
    tests = [
        # POST search tests
        ("/search", "POST", {"query": "iPhone 13", "max_results": 5}, "POST search iPhone 13", 200),
        ("/search", "POST", {"query": "Samsung Galaxy S23", "max_results": 3}, "POST search Samsung S23", 200),
        
        # Edge cases
        ("/search?q=NonExistentDevice123", "GET", None, "Search non-existent device", 200),
        ("/search", "POST", {"query": "", "max_results": 1}, "Empty query search", 200),
    ]
    
    passed = 0
    total = len(tests)
    
    for endpoint, method, data, description, expected_status in tests:
        if test_endpoint(endpoint, method, data, description, expected_status):
            passed += 1
    
    return passed, total

def run_ai_summary_tests():
    """Run AI summary functionality tests."""
    print_header("AI SUMMARY TESTS")
    
    # Test AI summary endpoint
    summary_data = {
        "device_url": "https://www.ifixit.com/Guide/iPhone+14+Screen+Replacement/173000",
        "summary_type": "beginner"
    }
    
    print("  🤖 Testing AI summary functionality...")
    print("     📝 Note: This requires DeepSeek API key to work fully")
    
    passed = test_endpoint("/summarize", "POST", summary_data, "Generate AI summary", 200)
    
    if passed:
        print("     ✅ AI summary endpoint is working!")
    else:
        print("     ⚠️  AI summary may not be configured (DeepSeek API key missing)")
    
    return 1 if passed else 0, 1

def run_error_handling_tests():
    """Run error handling tests."""
    print_header("ERROR HANDLING TESTS")
    
    tests = [
        ("/nonexistent", "GET", None, "404 Not Found", 404),
        ("/search", "POST", {"invalid": "data"}, "Invalid POST data", 422),
    ]
    
    passed = 0
    total = len(tests)
    
    for endpoint, method, data, description, expected_status in tests:
        if test_endpoint(endpoint, method, data, description, expected_status):
            passed += 1
    
    return passed, total

def print_summary(basic_passed, basic_total, advanced_passed, advanced_total, 
                 ai_passed, ai_total, error_passed, error_total):
    """Print test summary."""
    print_header("TEST SUMMARY")
    
    total_tests = basic_total + advanced_total + ai_total + error_total
    total_passed = basic_passed + advanced_passed + ai_passed + error_passed
    
    print(f"📊 Test Results:")
    print(f"   🔧 Basic Tests:     {basic_passed}/{basic_total}")
    print(f"   🚀 Advanced Tests:  {advanced_passed}/{advanced_total}")
    print(f"   🤖 AI Summary:      {ai_passed}/{ai_total}")
    print(f"   🛡️  Error Handling: {error_passed}/{error_total}")
    print(f"   {'='*30}")
    print(f"   🎯 Total:           {total_passed}/{total_tests}")
    
    success_rate = (total_passed / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"\n📈 Success Rate: {success_rate:.1f}%")
    
    if total_passed == total_tests:
        print("🎉 All tests passed! Your API is working perfectly!")
    elif success_rate >= 80:
        print("✅ Most tests passed! Your API is working well!")
    elif success_rate >= 60:
        print("⚠️  Some tests failed. Check the output above for details.")
    else:
        print("❌ Many tests failed. Please check your setup and try again.")
    
    print(f"\n🔗 Useful Links:")
    print(f"   📚 API Documentation: {BASE_URL}/docs")
    print(f"   💚 Health Check:      {BASE_URL}/health")
    print(f"   🏠 API Home:          {BASE_URL}/")

def main():
    """Run the complete test suite."""
    print_header("iFixit Repair Guide API - Test Suite")
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Testing: {BASE_URL}")
    
    # Check server status first
    if not check_server_status():
        print("\n❌ Cannot run tests - server is not available!")
        print("💡 Please start the server with: python app.py")
        sys.exit(1)
    
    # Run all test suites
    basic_passed, basic_total = run_basic_tests()
    advanced_passed, advanced_total = run_advanced_tests()
    ai_passed, ai_total = run_ai_summary_tests()
    error_passed, error_total = run_error_handling_tests()
    
    # Print summary
    print_summary(basic_passed, basic_total, advanced_passed, advanced_total,
                 ai_passed, ai_total, error_passed, error_total)
    
    print(f"\n🕐 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main() 