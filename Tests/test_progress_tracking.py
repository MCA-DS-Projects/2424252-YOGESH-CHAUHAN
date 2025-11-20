"""
Test progress tracking endpoints
"""
import requests
import json

BASE_URL = "http://localhost:5000/api"

def test_progress_tracking():
    """Test the progress tracking system"""
    
    print("\n=== Testing Progress Tracking System ===\n")
    
    # Step 1: Login as a student
    print("1. Logging in as student...")
    login_data = {
        "email": "student@test.com",
        "password": "password123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"❌ Login failed: {response.json()}")
        return
    
    token = response.json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Student logged in successfully")
    
    # Step 2: Get list of enrolled courses
    print("\n2. Getting enrolled courses...")
    response = requests.get(f"{BASE_URL}/courses", headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to get courses: {response.json()}")
        return
    
    courses = response.json()['courses']
    enrolled_courses = [c for c in courses if c.get('is_enrolled')]
    
    if not enrolled_courses:
        print("❌ No enrolled courses found")
        return
    
    course_id = enrolled_courses[0]['_id']
    print(f"✅ Found enrolled course: {enrolled_courses[0]['title']} (ID: {course_id})")
    
    # Step 3: Get progress for the course (should not exist yet)
    print("\n3. Getting progress for course (should be default state)...")
    response = requests.get(f"{BASE_URL}/progress/course/{course_id}", headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to get progress: {response.json()}")
        return
    
    progress = response.json()['progress']
    print(f"✅ Progress retrieved:")
    print(f"   - Started: {progress['started']}")
    print(f"   - Last Accessed: {progress['last_accessed']}")
    print(f"   - Overall Progress: {progress['overall_progress']}%")
    
    # Step 4: Start the course (initialize progress)
    print("\n4. Starting the course (initializing progress)...")
    response = requests.post(f"{BASE_URL}/progress/course/{course_id}/start", headers=headers)
    if response.status_code not in [200, 201]:
        print(f"❌ Failed to start course: {response.json()}")
        return
    
    progress = response.json()['progress']
    print(f"✅ Course started successfully:")
    print(f"   - Started: {progress['started']}")
    print(f"   - Last Accessed: {progress['last_accessed']}")
    
    # Step 5: Get progress again (should now show started=True)
    print("\n5. Getting progress again (should show started=True)...")
    response = requests.get(f"{BASE_URL}/progress/course/{course_id}", headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to get progress: {response.json()}")
        return
    
    progress = response.json()['progress']
    print(f"✅ Progress retrieved:")
    print(f"   - Started: {progress['started']}")
    print(f"   - Last Accessed: {progress['last_accessed']}")
    print(f"   - Overall Progress: {progress['overall_progress']}%")
    
    if progress['started']:
        print("\n✅ All progress tracking tests passed!")
    else:
        print("\n❌ Progress tracking test failed: started should be True")

if __name__ == "__main__":
    test_progress_tracking()
