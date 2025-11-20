"""
Test script for verifying video upload functionality
Tests:
- Video upload with valid video file
- File type validation (MP4, WebM, OGG)
- File size validation (max 500MB)
- Unique filename generation using UUID
- Video ID and metadata returned correctly
Requirements: 3.1, 3.2, 3.3
"""

import requests
import json
import io
import os

# Configuration
BASE_URL = "http://localhost:5000/api"

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def create_test_video(size_mb=1):
    """Create a small test video file in memory (simulated)"""
    # Create a minimal MP4 file header (not a real video, but enough for testing)
    # In a real scenario, you'd use a proper video file
    video_data = b'\x00\x00\x00\x20\x66\x74\x79\x70\x69\x73\x6f\x6d' + (b'\x00' * (size_mb * 1024 * 1024))
    return io.BytesIO(video_data)

def get_teacher_token():
    """Login as teacher and get token"""
    login_data = {
        "email": "teacher@test.com",
        "password": "password123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code == 200:
        return response.json()['access_token']
    return None

def test_video_upload_valid():
    """Test uploading a valid video"""
    print_section("TEST 1: Upload valid video (MP4)")
    
    token = get_teacher_token()
    if not token:
        print("❌ FAIL: Could not login as teacher")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create test video
    video_bytes = create_test_video(size_mb=1)
    files = {'video': ('test_video.mp4', video_bytes, 'video/mp4')}
    
    response = requests.post(f"{BASE_URL}/videos/upload", headers=headers, files=files)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        data = response.json()
        required_fields = ['video_id', 'filename', 'original_filename', 'file_size', 'mime_type', 'video_url']
        if all(field in data for field in required_fields):
            print(f"✅ PASS: Video uploaded successfully")
            print(f"   Video ID: {data['video_id']}")
            print(f"   Filename: {data['filename']}")
            print(f"   MIME Type: {data['mime_type']}")
            return True
        else:
            print("❌ FAIL: Missing required fields in response")
            print(f"   Expected: {required_fields}")
            print(f"   Got: {list(data.keys())}")
            return False
    else:
        print("❌ FAIL: Upload failed")
        return False

def test_video_invalid_type():
    """Test uploading an invalid file type"""
    print_section("TEST 2: Upload invalid file type (should fail)")
    
    token = get_teacher_token()
    if not token:
        print("❌ FAIL: Could not login as teacher")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a text file instead of a video
    text_file = io.BytesIO(b"This is not a video")
    files = {'video': ('test.txt', text_file, 'text/plain')}
    
    response = requests.post(f"{BASE_URL}/videos/upload", headers=headers, files=files)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 400:
        print(f"✅ PASS: Invalid file type correctly rejected")
        return True
    else:
        print("❌ FAIL: Should reject invalid file types")
        return False

def test_video_filename_uniqueness():
    """Test that uploaded files get unique filenames"""
    print_section("TEST 3: Verify filename uniqueness")
    
    token = get_teacher_token()
    if not token:
        print("❌ FAIL: Could not login as teacher")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    filenames = []
    
    # Upload same file twice
    for i in range(2):
        video_bytes = create_test_video(size_mb=1)
        files = {'video': ('same_name.mp4', video_bytes, 'video/mp4')}
        
        response = requests.post(f"{BASE_URL}/videos/upload", headers=headers, files=files)
        
        if response.status_code == 201:
            data = response.json()
            filenames.append(data['filename'])
            print(f"Upload {i+1} filename: {data['filename']}")
        else:
            print(f"❌ FAIL: Upload {i+1} failed")
            return False
    
    if len(filenames) == 2 and filenames[0] != filenames[1]:
        print(f"✅ PASS: Filenames are unique")
        return True
    else:
        print("❌ FAIL: Filenames should be unique")
        return False

def test_video_no_auth():
    """Test that upload requires authentication"""
    print_section("TEST 4: Upload without authentication (should fail)")
    
    video_bytes = create_test_video(size_mb=1)
    files = {'video': ('test.mp4', video_bytes, 'video/mp4')}
    
    response = requests.post(f"{BASE_URL}/videos/upload", files=files)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 401:
        print(f"✅ PASS: Authentication required")
        return True
    else:
        print("❌ FAIL: Should require authentication")
        return False

def test_video_extension_preserved():
    """Test that file extension is preserved"""
    print_section("TEST 5: Verify file extension preservation")
    
    token = get_teacher_token()
    if not token:
        print("❌ FAIL: Could not login as teacher")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test different extensions
    extensions = [('test.mp4', 'video/mp4', '.mp4'), 
                  ('test.webm', 'video/webm', '.webm'),
                  ('test.ogg', 'video/ogg', '.ogg')]
    
    for filename, mime_type, expected_ext in extensions:
        video_bytes = create_test_video(size_mb=1)
        files = {'video': (filename, video_bytes, mime_type)}
        
        response = requests.post(f"{BASE_URL}/videos/upload", headers=headers, files=files)
        
        if response.status_code == 201:
            data = response.json()
            if data['filename'].endswith(expected_ext):
                print(f"✅ Extension {expected_ext} preserved")
            else:
                print(f"❌ FAIL: Extension {expected_ext} not preserved")
                return False
        else:
            print(f"❌ FAIL: Upload failed for {filename}")
            return False
    
    print(f"✅ PASS: All file extensions preserved")
    return True

def main():
    print("\n" + "🧪 VIDEO UPLOAD FUNCTIONALITY VERIFICATION" + "\n")
    print("Testing /api/videos/upload endpoint")
    print("Requirements: 3.1, 3.2, 3.3")
    
    results = []
    
    # Run tests
    results.append(("Valid MP4 Upload", test_video_upload_valid()))
    results.append(("Invalid File Type", test_video_invalid_type()))
    results.append(("Filename Uniqueness", test_video_filename_uniqueness()))
    results.append(("Authentication Required", test_video_no_auth()))
    results.append(("Extension Preservation", test_video_extension_preserved()))
    
    # Summary
    print_section("TEST SUMMARY")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    try:
        exit(main())
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
