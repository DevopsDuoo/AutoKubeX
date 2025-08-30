#!/usr/bin/env python3
"""
Test script to verify session management functionality
"""

import sys
import os

# Add the project root to the path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)

from interface.session_manager import SessionManager
import tempfile

def test_session_manager():
    """Test basic session manager functionality"""
    print("🧪 Testing Session Manager...")
    
    # Initialize session manager
    sm = SessionManager()
    print(f"✅ Session manager initialized")
    print(f"📁 Session directory: {sm.session_dir}")
    
    # Test session data save/load
    test_data = {
        'test_key': 'test_value',
        'cluster_name': 'test-cluster',
        'connection_time': '2025-08-30T10:00:00'
    }
    
    print(f"💾 Saving test data: {test_data}")
    if sm.save_session_data(test_data):
        print("✅ Session data saved successfully")
        
        # Load the data back
        loaded_data = sm.load_session_data()
        if loaded_data:
            print(f"📥 Loaded data: {loaded_data}")
            print("✅ Session data loaded successfully")
        else:
            print("❌ Failed to load session data")
    else:
        print("❌ Failed to save session data")
    
    # Test session listing
    active_sessions = sm.list_active_sessions()
    print(f"📋 Active sessions: {len(active_sessions)}")
    for session_id, info in active_sessions.items():
        print(f"  📱 {session_id[:8]}... | {info}")
    
    # Test cleanup
    session_id = sm.get_session_id()
    print(f"🧹 Cleaning up session: {session_id[:8]}...")
    if sm.cleanup_session(session_id):
        print("✅ Session cleaned up successfully")
    else:
        print("❌ Failed to cleanup session")
    
    print("\n🎉 Session Manager test completed!")

if __name__ == "__main__":
    test_session_manager()
