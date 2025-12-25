#!/usr/bin/env python3
"""
Test script for Phase 2: Emoji-Based Reaction System
"""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def test_reaction_system():
    """Test the emoji reaction system"""

    print("🚀 Testing Phase 2: Emoji-Based Reaction System")
    print("=" * 50)

    # Test data
    test_user = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpass123"
    }

    test_awareness = {
        "title": "Test Awareness Post",
        "content": "This is a test awareness post for women safety.",
        "category": "guideline",
        "source": "NGO"
    }

    # 1. Register user
    print("1️⃣ Registering test user...")
    try:
        response = requests.post(f"{BASE_URL}/auth/", json=test_user)
        print(f"   Status: {response.status_code}")
        if response.status_code == 201:
            print("   ✅ User registered successfully")
        else:
            print(f"   ❌ Registration failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # 2. Login
    print("\n2️⃣ Logging in...")
    login_data = {
        "username": test_user["email"],
        "password": test_user["password"]
    }
    try:
        response = requests.post(f"{BASE_URL}/auth/token", data=login_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get("access_token")
            headers = {"Authorization": f"Bearer {token}"}
            print("   ✅ Login successful")
        else:
            print(f"   ❌ Login failed: {response.text}")
            return
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return

    # 3. Create awareness post (this will fail without admin role)
    print("\n3️⃣ Creating awareness post (should fail - not admin)...")
    try:
        response = requests.post(
            f"{BASE_URL}/awareness/create",
            json=test_awareness,
            headers=headers
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 403:
            print("   ✅ Correctly denied - user not admin")
        else:
            print(f"   ❌ Unexpected response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # 4. Get awareness feed
    print("\n4️⃣ Getting awareness feed...")
    try:
        response = requests.get(f"{BASE_URL}/awareness/feed")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            feed_data = response.json()
            print(f"   ✅ Feed retrieved: {len(feed_data.get('posts', []))} posts")
            if feed_data.get('posts'):
                post_id = feed_data['posts'][0]['id']
                print(f"   📝 Using post ID: {post_id}")
            else:
                print("   ⚠️  No posts in feed")
                return
        else:
            print(f"   ❌ Feed retrieval failed: {response.text}")
            return
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return

    # 5. Test emoji reaction
    print("\n5️⃣ Testing emoji reaction...")
    reaction_data = {"emoji": "🤝"}  # Handshake emoji
    try:
        response = requests.post(
            f"{BASE_URL}/awareness/{post_id}/react",
            json=reaction_data,
            headers=headers
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            reaction_result = response.json()
            print(f"   ✅ Reaction added: {reaction_result}")
        else:
            print(f"   ❌ Reaction failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # 6. Get reaction summary
    print("\n6️⃣ Getting reaction summary...")
    try:
        response = requests.get(
            f"{BASE_URL}/awareness/{post_id}/reactions",
            headers=headers
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            summary = response.json()
            print(f"   ✅ Summary: {summary}")
        else:
            print(f"   ❌ Summary failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # 7. Test invalid emoji
    print("\n7️⃣ Testing invalid emoji...")
    invalid_reaction = {"emoji": "🚫"}  # Invalid emoji
    try:
        response = requests.post(
            f"{BASE_URL}/awareness/{post_id}/react",
            json=invalid_reaction,
            headers=headers
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 400:
            print("   ✅ Correctly rejected invalid emoji")
        else:
            print(f"   ❌ Should have rejected invalid emoji: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # 8. Remove reaction
    print("\n8️⃣ Removing reaction...")
    try:
        response = requests.delete(
            f"{BASE_URL}/awareness/{post_id}/react",
            headers=headers
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Reaction removed successfully")
        else:
            print(f"   ❌ Remove failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    print("\n🎉 Phase 2 testing completed!")

if __name__ == "__main__":
    test_reaction_system()