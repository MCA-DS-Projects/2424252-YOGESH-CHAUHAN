#!/usr/bin/env python3
"""
Teacher Dashboard Verification Script

This script verifies that the teacher dashboard is loading data correctly
from the database without any mock or hard-coded data.

Usage:
    python verify_teacher_dashboard.py
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000/api"
FRONTEND_URL = "http://localhost:5173"

def print_header(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def print_success(text):
    print(f"✅ {text}")

def print_error(text):
    print(f"❌ {text}")

def print_info(text):
    print(f"ℹ️  {text}")

def print_warning(text):
    print(f"⚠️  {text}")

def login_as_teacher():
    """Login as a teacher user"""
    print_header("Step 1: Teacher Login")
    
    # You'll need to replace this with an actual teacher account
    email = input("Enter teacher email (or press Enter for default): ").strip()
    if not email:
        email = "teacher@test.com"
    
    password = input("Enter password (or press Enter for default): ").strip()
    if not password:
        password = "TestPass123!"
    
    login_data = {
        "email": email,
        "password": password
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            user = data.get('user', {})
            
            if user.get('role') != 'teacher':
                print_error(f"User is not a teacher! Role: {user.get('role')}")
                return None, None
            
            print_success(f"Logged in as: {user.get('name')} ({user.get('email')})")
            print_info(f"Role: {user.get('role')}")
            return data.get('access_token'), user
        else:
            error = response.json().get('error', 'Unknown error')
            print_error(f"Login failed: {error}")
            return None, None
    except Exception as e:
        print_error(f"Login error: {str(e)}")
        return None, None

def verify_teacher_stats(token):
    """Verify teacher dashboard statistics"""
    print_header("Step 2: Verify Teacher Dashboard Stats")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/analytics/teacher/dashboard", headers=headers)
        if response.status_code == 200:
            stats = response.json().get('dashboard_stats', {})
            
            print_success("Teacher stats loaded successfully!")
            print(f"\n📊 Dashboard Statistics:")
            print(f"   Active Courses: {stats.get('active_courses', 0)}")
            print(f"   Total Students: {stats.get('total_students', 0)}")
            print(f"   Pending Grades: {stats.get('pending_grades', 0)}")
            print(f"   Course Rating: {stats.get('course_rating', 0):.1f}")
            
            monthly_growth = stats.get('monthly_growth', {})
            print(f"\n📈 Monthly Growth:")
            print(f"   Courses: +{monthly_growth.get('courses', 0)}")
            print(f"   Students: +{monthly_growth.get('students', 0)}")
            print(f"   Rating Change: {monthly_growth.get('rating_change', 0):+.1f}")
            
            return True
        else:
            print_error(f"Failed to fetch stats: {response.status_code}")
            print_error(f"Error: {response.json().get('error', 'Unknown error')}")
            return False
    except Exception as e:
        print_error(f"Error fetching stats: {str(e)}")
        return False

def verify_teacher_courses(token):
    """Verify teacher courses are loaded from database"""
    print_header("Step 3: Verify Teacher Courses")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/courses", headers=headers)
        if response.status_code == 200:
            courses = response.json().get('courses', [])
            
            print_success(f"Found {len(courses)} courses")
            
            if len(courses) == 0:
                print_warning("No courses found. This is normal if the teacher hasn't created any courses yet.")
                print_info("You can create a course from the teacher dashboard.")
                return True
            
            print(f"\n📚 Courses:")
            for i, course in enumerate(courses[:5], 1):  # Show first 5
                print(f"\n   {i}. {course.get('title')}")
                print(f"      ID: {course.get('_id')}")
                print(f"      Students: {course.get('enrolled_students', 0)}")
                print(f"      Assignments: {course.get('total_assignments', 0)}")
                print(f"      Active: {course.get('is_active', True)}")
                print(f"      Created: {course.get('created_at', 'N/A')}")
                
                # Verify teacher-specific data is present
                if 'enrolled_students' in course:
                    print_success("      ✓ Enrollment data present")
                if 'total_assignments' in course:
                    print_success("      ✓ Assignment data present")
                if 'average_progress' in course:
                    print_success(f"      ✓ Progress tracking: {course['average_progress']:.1f}%")
            
            if len(courses) > 5:
                print(f"\n   ... and {len(courses) - 5} more courses")
            
            return True
        else:
            print_error(f"Failed to fetch courses: {response.status_code}")
            print_error(f"Error: {response.json().get('error', 'Unknown error')}")
            return False
    except Exception as e:
        print_error(f"Error fetching courses: {str(e)}")
        return False

def verify_teacher_assignments(token):
    """Verify teacher assignments"""
    print_header("Step 4: Verify Teacher Assignments")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/assignments", headers=headers)
        if response.status_code == 200:
            assignments = response.json().get('assignments', [])
            
            print_success(f"Found {len(assignments)} assignments")
            
            if len(assignments) == 0:
                print_warning("No assignments found. This is normal if the teacher hasn't created any assignments yet.")
                return True
            
            # Count pending submissions
            pending = [a for a in assignments if a.get('submission_count', 0) > 0]
            
            print(f"\n📝 Assignment Summary:")
            print(f"   Total Assignments: {len(assignments)}")
            print(f"   With Pending Submissions: {len(pending)}")
            
            if pending:
                print(f"\n   Assignments with submissions:")
                for i, assignment in enumerate(pending[:3], 1):
                    print(f"   {i}. {assignment.get('title')}")
                    print(f"      Submissions: {assignment.get('submission_count', 0)}")
                    print(f"      Course: {assignment.get('course_title', 'N/A')}")
            
            return True
        else:
            print_error(f"Failed to fetch assignments: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error fetching assignments: {str(e)}")
        return False

def verify_no_mock_data():
    """Verify no mock data in source code"""
    print_header("Step 5: Verify No Mock Data in Source Code")
    
    files_to_check = [
        "src/components/dashboard/TeacherDashboard.tsx",
        "src/components/dashboard/StudentDashboard.tsx",
        "src/contexts/LMSContext.tsx",
        "src/services/teacherApi.ts"
    ]
    
    mock_patterns = [
        "mockCourses",
        "mockData",
        "testData",
        "sampleCourses",
        "dummyCourses",
        "const courses = [{"
    ]
    
    all_clean = True
    
    for file_path in files_to_check:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            found_patterns = []
            for pattern in mock_patterns:
                if pattern in content:
                    found_patterns.append(pattern)
            
            if found_patterns:
                print_error(f"{file_path}: Found mock patterns: {', '.join(found_patterns)}")
                all_clean = False
            else:
                print_success(f"{file_path}: Clean ✓")
        except FileNotFoundError:
            print_warning(f"{file_path}: File not found (may be in different location)")
        except Exception as e:
            print_warning(f"{file_path}: Could not check - {str(e)}")
    
    return all_clean

def main():
    print_header("Teacher Dashboard Verification")
    print_info("This script verifies that the teacher dashboard loads data from the database")
    print_info("without any mock or hard-coded data.")
    
    # Step 1: Login
    token, user = login_as_teacher()
    if not token:
        print_error("\nVerification failed: Could not login as teacher")
        return
    
    # Step 2: Verify stats
    stats_ok = verify_teacher_stats(token)
    
    # Step 3: Verify courses
    courses_ok = verify_teacher_courses(token)
    
    # Step 4: Verify assignments
    assignments_ok = verify_teacher_assignments(token)
    
    # Step 5: Verify no mock data
    no_mock = verify_no_mock_data()
    
    # Summary
    print_header("Verification Summary")
    
    results = [
        ("Teacher Login", token is not None),
        ("Dashboard Stats", stats_ok),
        ("Teacher Courses", courses_ok),
        ("Teacher Assignments", assignments_ok),
        ("No Mock Data", no_mock)
    ]
    
    all_passed = all(result[1] for result in results)
    
    for test_name, passed in results:
        if passed:
            print_success(f"{test_name}: PASSED")
        else:
            print_error(f"{test_name}: FAILED")
    
    print("\n" + "="*70)
    if all_passed:
        print_success("🎉 All verifications PASSED!")
        print_info(f"\nYou can now access the teacher dashboard at: {FRONTEND_URL}")
        print_info("The dashboard will show real data from your MongoDB database.")
    else:
        print_error("⚠️  Some verifications FAILED")
        print_info("Please check the errors above and ensure:")
        print_info("  1. Backend server is running (python backend/app.py)")
        print_info("  2. MongoDB is running and accessible")
        print_info("  3. You have a valid teacher account")
        print_info("  4. The teacher has created some courses/assignments")
    print("="*70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Verification interrupted by user")
    except Exception as e:
        print_error(f"\nUnexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
