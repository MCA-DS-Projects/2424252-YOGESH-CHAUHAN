"""
Manual test script for video progress tracking.

This script tests the video progress tracking endpoints:
1. POST /api/videos/<video_id>/progress - Update video watch progress
2. GET /api/videos/<video_id>/progress - Get video watch progress

Usage:
    python backend/test_video_progress_manual.py
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000/api"

# Test credentials (update these with actual test user credentials)
STUDENT_EMAIL = "student@test.com"
STUDENT_PASSWORD = "password123"

def login(email, password):
    """Login and get access token"""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": email, "password": password}
    )
    
    if response.status_code == 200:
        data = response.json()
        token = data.get('access_token') or data.get('token')
        print(f"✅ Login successful")
        return token
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return None

def update_video_progress(token, video_id, watch_time, duration):
    """Update video watch progress"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "watchTime": watch_time,
        "duration": duration
    }
    
    response = requests.post(
        f"{BASE_URL}/videos/{video_id}/progress",
        headers=headers,
        json=data
    )
    
    print(f"\n📊 Update Video Progress (watch_time={watch_time}s, duration={duration}s)")
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Progress updated")
        print(f"   Watch Time: {result.get('watchTime')}s")
        print(f"   Completed: {result.get('completed')}")
        return result
    else:
        print(f"   ❌ Failed: {response.text}")
        return None

def get_video_progress(token, video_id):
    """Get video watch progress"""
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(
        f"{BASE_URL}/videos/{video_id}/progress",
        headers=headers
    )
    
    print(f"\n📈 Get Video Progress")
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        progress = result.get('progress', {})
        print(f"   ✅ Progress retrieved")
        print(f"   Watch Time: {progress.get('watchTime')}s")
        print(f"   Completed: {progress.get('completed')}")
        print(f"   Last Watched: {progress.get('lastWatched')}")
        return progress
    else:
        print(f"   ❌ Failed: {response.text}")
        return None

def main():
    """Run manual tests"""
    print("=" * 60)
    print("Video Progress Tracking Manual Test")
    print("=" * 60)
    
    # Step 1: Login
    print("\n1️⃣  Logging in as student...")
    token = login(STUDENT_EMAIL, STUDENT_PASSWORD)
    
    if not token:
        print("\n❌ Cannot proceed without authentication")
        print("   Please ensure:")
        print("   - Backend server is running (python backend/run.py)")
        print("   - Test student account exists")
        print("   - Update STUDENT_EMAIL and STUDENT_PASSWORD in this script")
        return
    
    # Step 2: Get a video ID (you'll need to replace this with an actual video ID)
    video_id = input("\n2️⃣  Enter a video ID to test (or press Enter to skip): ").strip()
    
    if not video_id:
        print("\n⚠️  No video ID provided. Creating a mock test...")
        print("   To test with real data:")
        print("   1. Create a course with a video")
        print("   2. Get the video ID from the database or API")
        print("   3. Run this script again with that video ID")
        return
    
    # Step 3: Test getting initial progress (should be 0)
    print("\n3️⃣  Getting initial video progress...")
    initial_progress = get_video_progress(token, video_id)
    
    # Step 4: Update progress to 50% (should not be complete)
    print("\n4️⃣  Updating progress to 50% (should not be complete)...")
    duration = 100  # 100 seconds video
    watch_time_50 = 50  # 50 seconds watched
    update_video_progress(token, video_id, watch_time_50, duration)
    
    # Step 5: Get progress again (should show 50s watched, not complete)
    print("\n5️⃣  Getting updated progress...")
    progress_50 = get_video_progress(token, video_id)
    
    # Step 6: Update progress to 85% (should be complete)
    print("\n6️⃣  Updating progress to 85% (should be complete)...")
    watch_time_85 = 85  # 85 seconds watched
    update_video_progress(token, video_id, watch_time_85, duration)
    
    # Step 7: Get final progress (should show 85s watched, completed)
    print("\n7️⃣  Getting final progress...")
    progress_85 = get_video_progress(token, video_id)
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    if progress_50 and progress_85:
        print("✅ All tests completed successfully!")
        print(f"   - Initial progress: {initial_progress.get('watchTime', 0)}s")
        print(f"   - Progress at 50%: {progress_50.get('watchTime')}s (completed: {progress_50.get('completed')})")
        print(f"   - Progress at 85%: {progress_85.get('watchTime')}s (completed: {progress_85.get('completed')})")
        
        # Verify completion logic
        if not progress_50.get('completed') and progress_85.get('completed'):
            print("\n✅ Completion logic working correctly!")
            print("   - Video not marked complete at 50%")
            print("   - Video marked complete at 85% (>80% threshold)")
        else:
            print("\n⚠️  Completion logic may have issues")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
