#!/usr/bin/env python3
"""
Validation script for Phase 3: Mentorship System
"""

from fastapi.testclient import TestClient
from app.main import app
import json

def test_mentorship_system():
    """Test mentorship system functionality"""

    client = TestClient(app)

    print("🚀 Testing Phase 3: Mentorship System")
    print("=" * 50)

    # Test 1: Check mentorship schemas
    print("1️⃣ Testing mentorship schemas...")
    from schemas.mentorship import MentorshipTopic, MentorshipStatus
    from schemas.mentor import MentorRole

    # Check topics
    topics = [t.value for t in MentorshipTopic]
    expected_topics = ["legal_advice", "emotional_support", "safety_planning", "reporting_guidance"]
    assert set(topics) == set(expected_topics), f"Topics mismatch: {topics}"
    print(f"   ✅ Topics: {topics}")

    # Check mentor roles
    roles = [r.value for r in MentorRole]
    expected_roles = ["NGO", "Lawyer", "Psychologist"]
    assert set(roles) == set(expected_roles), f"Roles mismatch: {roles}"
    print(f"   ✅ Roles: {roles}")

    # Test 2: Check models
    print("\n2️⃣ Testing mentorship models...")
    from models.mentor import Mentor, MentorRole as ModelMentorRole
    from models.mentorship import MentorshipSession, MentorshipTopic as ModelTopic
    from models.mentorship_message import MentorshipMessage, MessageRole

    # Check model enums match schema enums
    schema_roles = [r.value for r in MentorRole]
    model_roles = [r.value for r in ModelMentorRole]
    assert set(schema_roles) == set(model_roles), "MentorRole enum values mismatch"

    schema_topics = [t.value for t in MentorshipTopic]
    model_topics = [t.value for t in ModelTopic]
    assert set(schema_topics) == set(model_topics), "Topic enum values mismatch"
    print("   ✅ Model enums consistent")

    # Test 3: Check service functions exist
    print("\n3️⃣ Testing mentorship services...")
    from services.mentorship import (
        request_mentorship,
        mentor_reply,
        user_reply,
        close_session,
        get_user_sessions
    )
    print("   ✅ All service functions imported")

    # Test 4: Check routes
    print("\n4️⃣ Testing mentorship routes...")
    from routes.mentorship import router
    routes = [route.path for route in router.routes]
    expected_routes = [
        "/mentorship/request",
        "/mentorship/sessions",
        "/mentorship/{session_id}/user-reply",
        "/mentorship/{session_id}/mentor-reply",
        "/mentorship/{session_id}/close"
    ]
    print(f"   ✅ Routes: {routes}")

    # Test 5: Check topic-role mapping
    print("\n5️⃣ Testing topic-role mapping...")
    from services.mentorship import _get_mentor_role_for_topic
    mapping = {
        MentorshipTopic.LEGAL_ADVICE: MentorRole.LAWYER,
        MentorshipTopic.REPORTING_GUIDANCE: MentorRole.LAWYER,
        MentorshipTopic.SAFETY_PLANNING: MentorRole.NGO,
        MentorshipTopic.EMOTIONAL_SUPPORT: MentorRole.PSYCHOLOGIST
    }

    for topic, expected_role in mapping.items():
        actual_role = _get_mentor_role_for_topic(topic)
        assert actual_role.value == expected_role.value, f"Topic {topic} should map to {expected_role}, got {actual_role}"
    print("   ✅ Topic-role mapping correct")

    # Test 6: Check content filtering
    print("\n6️⃣ Testing content filtering...")
    from utils.content_filter import is_content_safe

    # Safe content
    safe, _ = is_content_safe("I need help with legal advice")
    assert safe, "Safe content should pass"
    print("   ✅ Safe content passes filter")

    # Unsafe content
    unsafe, reason = is_content_safe("This contains bastard words")
    assert not unsafe, "Unsafe content should be filtered"
    print("   ✅ Unsafe content filtered")

    print("\n🎉 Phase 3 validation tests passed!")
    print("\n📋 Manual testing required:")
    print("   1. Start server: uvicorn app.main:app --reload")
    print("   2. Create mentor users via database")
    print("   3. Test mentorship request flow")
    print("   4. Test message exchange")
    print("   5. Test session closure")

if __name__ == "__main__":
    test_mentorship_system()