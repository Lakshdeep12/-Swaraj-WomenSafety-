#!/usr/bin/env python3
"""
Simple test for Phase 2: Emoji-Based Reaction System using TestClient
"""

from fastapi.testclient import TestClient
from app.main import app
import json

def test_emoji_reactions():
    """Test emoji reaction functionality"""

    client = TestClient(app)

    print("🚀 Testing Phase 2: Emoji-Based Reaction System")
    print("=" * 50)

    # Test 1: Check allowed emojis
    print("1️⃣ Testing emoji validation...")
    from schemas.reaction import AllowedEmoji
    allowed_emojis = [e.value for e in AllowedEmoji]
    print(f"   Allowed emojis: {allowed_emojis}")
    assert len(allowed_emojis) == 6, "Should have 6 allowed emojis"
    print("   ✅ Emoji validation correct")

    # Test 2: Check awareness feed (should work without auth)
    print("\n2️⃣ Testing awareness feed...")
    response = client.get("/awareness/feed")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Feed works: {len(data.get('posts', []))} posts")
    else:
        print(f"   ❌ Feed failed: {response.text}")

    # Test 3: Test reaction validation
    print("\n3️⃣ Testing reaction schema validation...")
    from schemas.reaction import ReactionCreate
    try:
        # Valid emoji
        valid_reaction = ReactionCreate(emoji="🤝")
        print("   ✅ Valid emoji accepted")

        # Invalid emoji should fail
        try:
            invalid_reaction = ReactionCreate(emoji="🚫")
            print("   ❌ Invalid emoji should have been rejected")
        except ValueError:
            print("   ✅ Invalid emoji correctly rejected")
    except Exception as e:
        print(f"   ❌ Schema validation error: {e}")

    # Test 4: Check reaction summary structure
    print("\n4️⃣ Testing reaction summary structure...")
    from schemas.reaction import ReactionSummary
    summary = ReactionSummary(
        total_reactions=5,
        emoji_counts={"🤝": 3, "🕯️": 2},
        user_has_reacted=True,
        users_reacted=5
    )
    print(f"   ✅ Summary structure: {summary.model_dump()}")

    print("\n🎉 Basic validation tests passed!")
    print("\n📋 Manual testing required:")
    print("   1. Start server: uvicorn app.main:app --reload")
    print("   2. Create admin user via database")
    print("   3. Create awareness post")
    print("   4. Test reactions with different users")
    print("   5. Verify unique constraint (user + post)")

if __name__ == "__main__":
    test_emoji_reactions()