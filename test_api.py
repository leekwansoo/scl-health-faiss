"""
Basic tests for the SCL Health FAISS API
Tests authentication, endpoints, and basic functionality without OpenAI dependency
"""

import requests
import json
from pathlib import Path

API_BASE = "http://localhost:8000"
TEST_TOKEN = "scl-health-api-token-2024"
WRONG_TOKEN = "wrong-token"

def test_health_endpoint():
    """Test health check endpoint - no auth required"""
    response = requests.get(f"{API_BASE}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "scl-health-faiss-api"
    print("✓ Health endpoint test passed")

def test_root_endpoint():
    """Test root information endpoint - no auth required"""
    response = requests.get(f"{API_BASE}/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "endpoints" in data
    print("✓ Root endpoint test passed")

def test_authentication():
    """Test authentication with valid and invalid tokens"""
    
    # Test without token - should fail
    response = requests.get(f"{API_BASE}/api/documents")
    assert response.status_code == 403  # FastAPI returns 403 for missing auth
    print("✓ No token authentication test passed")
    
    # Test with wrong token - should fail  
    headers = {"Authorization": f"Bearer {WRONG_TOKEN}"}
    response = requests.get(f"{API_BASE}/api/documents", headers=headers)
    assert response.status_code == 401  # Our custom error for invalid token
    print("✓ Wrong token authentication test passed")
    
    # Test with correct token - should succeed
    headers = {"Authorization": f"Bearer {TEST_TOKEN}"}
    response = requests.get(f"{API_BASE}/api/documents", headers=headers)
    assert response.status_code == 200
    print("✓ Valid token authentication test passed")

def test_list_documents():
    """Test document listing endpoint"""
    headers = {"Authorization": f"Bearer {TEST_TOKEN}"}
    response = requests.get(f"{API_BASE}/api/documents", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "documents" in data
    assert isinstance(data["documents"], list)
    print(f"✓ List documents test passed - found {len(data['documents'])} documents")

def test_query_endpoint_validation():
    """Test query endpoint parameter validation"""
    headers = {"Authorization": f"Bearer {TEST_TOKEN}"}
    
    # Test empty query - should fail
    response = requests.post(f"{API_BASE}/api/query", 
                           headers=headers,
                           data={"query": ""})
    assert response.status_code == 400
    print("✓ Empty query validation test passed")
    
    # Test missing query parameter - should fail
    response = requests.post(f"{API_BASE}/api/query", headers=headers)
    assert response.status_code != 200  # Should fail validation
    print("✓ Missing query parameter validation test passed")

def run_basic_tests():
    """Run all basic tests that don't require OpenAI"""
    print("Running SCL Health FAISS API Tests")
    print("=" * 40)
    
    try:
        test_health_endpoint()
        test_root_endpoint()
        test_authentication()
        test_list_documents()
        test_query_endpoint_validation()
        
        print("\n" + "=" * 40)
        print("✅ All basic tests passed!")
        print("\nNote: Upload and query functionality tests require a valid OPENAI_API_KEY")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return False
    except requests.ConnectionError:
        print("\n❌ Cannot connect to API server. Make sure it's running on http://localhost:8000")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = run_basic_tests()
    exit(0 if success else 1)