#!/usr/bin/env python3
"""
View Test Users Script
Display generated test users from the database.

Usage:
    python backend/scripts/view_test_users.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()


def print_header(title):
    """Print formatted header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_table_row(columns, widths):
    """Print a table row"""
    row = " | ".join(str(col).ljust(width) for col, width in zip(columns, widths))
    print(f"| {row} |")


def print_table_separator(widths):
    """Print table separator"""
    separator = "-+-".join("-" * width for width in widths)
    print(f"+-{separator}-+")


def display_students(db, limit=None):
    """Display student records"""
    print_header("Student Records")
    
    query = {"role": "student", "email": {"$regex": "@student\\.edu$"}}
    total = db.users.count_documents(query)
    
    print(f"\nTotal Students: {total}")
    
    if limit:
        print(f"Showing first {limit} students:\n")
        students = list(db.users.find(query).limit(limit))
    else:
        students = list(db.users.find(query))
    
    if not students:
        print("No students found.")
        return
    
    # Table headers
    widths = [25, 35, 15, 25, 12]
    headers = ["Name", "Email", "Roll Number", "Department", "Year"]
    
    print_table_separator(widths)
    print_table_row(headers, widths)
    print_table_separator(widths)
    
    for student in students:
        row = [
            student.get('name', 'N/A')[:25],
            student.get('email', 'N/A')[:35],
            student.get('roll_number', 'N/A'),
            student.get('department', 'N/A')[:25],
            student.get('year', 'N/A')
        ]
        print_table_row(row, widths)
    
    print_table_separator(widths)


def display_teachers(db, limit=None):
    """Display teacher records"""
    print_header("Teacher Records")
    
    query = {"role": "teacher", "email": {"$regex": "@faculty\\.edu$"}}
    total = db.users.count_documents(query)
    
    print(f"\nTotal Teachers: {total}")
    
    if limit:
        print(f"Showing first {limit} teachers:\n")
        teachers = list(db.users.find(query).limit(limit))
    else:
        teachers = list(db.users.find(query))
    
    if not teachers:
        print("No teachers found.")
        return
    
    # Table headers
    widths = [25, 35, 15, 25, 20]
    headers = ["Name", "Email", "Employee ID", "Department", "Designation"]
    
    print_table_separator(widths)
    print_table_row(headers, widths)
    print_table_separator(widths)
    
    for teacher in teachers:
        row = [
            teacher.get('name', 'N/A')[:25],
            teacher.get('email', 'N/A')[:35],
            teacher.get('employee_id', 'N/A'),
            teacher.get('department', 'N/A')[:25],
            teacher.get('designation', 'N/A')[:20]
        ]
        print_table_row(row, widths)
    
    print_table_separator(widths)


def display_detailed_student(db, email):
    """Display detailed student information"""
    student = db.users.find_one({"email": email, "role": "student"})
    
    if not student:
        print(f"❌ Student not found: {email}")
        return
    
    print_header(f"Student Details: {student['name']}")
    
    print(f"\n📋 Basic Information:")
    print(f"   Name: {student.get('name')}")
    print(f"   Email: {student.get('email')}")
    print(f"   Roll Number: {student.get('roll_number')}")
    print(f"   Phone: {student.get('phone')}")
    print(f"   Date of Birth: {student.get('date_of_birth', 'N/A')}")
    
    print(f"\n🎓 Academic Information:")
    print(f"   Department: {student.get('department')}")
    print(f"   Year: {student.get('year')}")
    print(f"   Semester: {student.get('semester')}")
    print(f"   Total Points: {student.get('total_points', 0)}")
    
    if student.get('address'):
        addr = student['address']
        print(f"\n🏠 Address:")
        print(f"   {addr.get('street')}")
        print(f"   {addr.get('city')}, {addr.get('state')} {addr.get('zip_code')}")
    
    if student.get('emergency_contact'):
        contact = student['emergency_contact']
        print(f"\n🚨 Emergency Contact:")
        print(f"   Name: {contact.get('name')}")
        print(f"   Relationship: {contact.get('relationship')}")
        print(f"   Phone: {contact.get('phone')}")
    
    print(f"\n📅 Account Information:")
    print(f"   Created: {student.get('created_at', 'N/A')}")
    print(f"   Status: {'Active' if student.get('is_active') else 'Inactive'}")
    print(f"   Profile Picture: {student.get('profile_pic', 'N/A')}")


def display_detailed_teacher(db, email):
    """Display detailed teacher information"""
    teacher = db.users.find_one({"email": email, "role": "teacher"})
    
    if not teacher:
        print(f"❌ Teacher not found: {email}")
        return
    
    print_header(f"Teacher Details: {teacher['name']}")
    
    print(f"\n📋 Basic Information:")
    print(f"   Name: {teacher.get('name')}")
    print(f"   Email: {teacher.get('email')}")
    print(f"   Employee ID: {teacher.get('employee_id')}")
    print(f"   Phone: {teacher.get('phone')}")
    print(f"   Date of Birth: {teacher.get('date_of_birth', 'N/A')}")
    
    print(f"\n👨‍🏫 Professional Information:")
    print(f"   Department: {teacher.get('department')}")
    print(f"   Designation: {teacher.get('designation')}")
    print(f"   Years of Experience: {teacher.get('years_of_experience', 0)}")
    print(f"   Specializations: {', '.join(teacher.get('specializations', []))}")
    
    if teacher.get('office'):
        office = teacher['office']
        print(f"\n🏢 Office Information:")
        print(f"   Building: {office.get('building')}")
        print(f"   Room: {office.get('room')}")
        print(f"   Hours: {office.get('hours')}")
    
    if teacher.get('education'):
        edu = teacher['education']
        print(f"\n🎓 Education:")
        print(f"   Highest Degree: {edu.get('highest_degree')}")
        print(f"   University: {edu.get('university')}")
        print(f"   Year: {edu.get('year')}")
    
    print(f"\n📅 Account Information:")
    print(f"   Created: {teacher.get('created_at', 'N/A')}")
    print(f"   Status: {'Active' if teacher.get('is_active') else 'Inactive'}")
    print(f"   Profile Picture: {teacher.get('profile_pic', 'N/A')}")


def display_statistics(db):
    """Display database statistics"""
    print_header("Database Statistics")
    
    total_students = db.users.count_documents({"role": "student"})
    total_teachers = db.users.count_documents({"role": "teacher"})
    total_admins = db.users.count_documents({"role": {"$in": ["admin", "super_admin"]}})
    total_users = db.users.count_documents({})
    
    print(f"\n👥 User Counts:")
    print(f"   Total Users: {total_users}")
    print(f"   Students: {total_students}")
    print(f"   Teachers: {total_teachers}")
    print(f"   Admins: {total_admins}")
    
    # Department distribution for students
    print(f"\n📊 Student Distribution by Department:")
    pipeline = [
        {"$match": {"role": "student"}},
        {"$group": {"_id": "$department", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    dept_stats = list(db.users.aggregate(pipeline))
    
    for stat in dept_stats:
        print(f"   {stat['_id']}: {stat['count']} students")
    
    # Year distribution for students
    print(f"\n📅 Student Distribution by Year:")
    pipeline = [
        {"$match": {"role": "student"}},
        {"$group": {"_id": "$year", "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}}
    ]
    year_stats = list(db.users.aggregate(pipeline))
    
    for stat in year_stats:
        print(f"   {stat['_id']}: {stat['count']} students")
    
    # Department distribution for teachers
    print(f"\n👨‍🏫 Teacher Distribution by Department:")
    pipeline = [
        {"$match": {"role": "teacher"}},
        {"$group": {"_id": "$department", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    dept_stats = list(db.users.aggregate(pipeline))
    
    for stat in dept_stats:
        print(f"   {stat['_id']}: {stat['count']} teachers")


def interactive_menu(db):
    """Interactive menu for viewing users"""
    while True:
        print_header("Test User Viewer - Interactive Menu")
        print("\n1. View all students (summary)")
        print("2. View all teachers (summary)")
        print("3. View first 10 students")
        print("4. View first 10 teachers")
        print("5. View detailed student by email")
        print("6. View detailed teacher by email")
        print("7. View database statistics")
        print("8. Export students to CSV")
        print("9. Export teachers to CSV")
        print("10. Exit")
        
        choice = input("\nEnter choice (1-10): ").strip()
        
        try:
            if choice == '1':
                display_students(db)
            elif choice == '2':
                display_teachers(db)
            elif choice == '3':
                display_students(db, limit=10)
            elif choice == '4':
                display_teachers(db, limit=10)
            elif choice == '5':
                email = input("Enter student email: ").strip()
                display_detailed_student(db, email)
            elif choice == '6':
                email = input("Enter teacher email: ").strip()
                display_detailed_teacher(db, email)
            elif choice == '7':
                display_statistics(db)
            elif choice == '8':
                export_to_csv(db, "student")
            elif choice == '9':
                export_to_csv(db, "teacher")
            elif choice == '10':
                print("\n👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter 1-10.")
        
        except Exception as e:
            print(f"\n❌ Error: {e}")
        
        input("\nPress Enter to continue...")


def export_to_csv(db, role):
    """Export users to CSV file"""
    import csv
    
    query = {"role": role, "email": {"$regex": f"@{'student' if role == 'student' else 'faculty'}\\.edu$"}}
    users = list(db.users.find(query))
    
    if not users:
        print(f"❌ No {role}s found to export")
        return
    
    filename = f"test_{role}s_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    if role == "student":
        fieldnames = ['name', 'email', 'roll_number', 'department', 'year', 'semester', 'phone', 'date_of_birth']
    else:
        fieldnames = ['name', 'email', 'employee_id', 'department', 'designation', 'phone', 'date_of_birth', 'years_of_experience']
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            
            for user in users:
                # Convert datetime to string
                if 'date_of_birth' in user and user['date_of_birth']:
                    user['date_of_birth'] = user['date_of_birth'].strftime('%Y-%m-%d')
                writer.writerow({k: user.get(k, '') for k in fieldnames})
        
        print(f"✅ Exported {len(users)} {role}s to {filename}")
    
    except Exception as e:
        print(f"❌ Failed to export: {e}")


def main():
    """Main execution function"""
    # Connect to MongoDB
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/edunexa_lms')
    
    try:
        client = MongoClient(MONGO_URI)
        db = client.edunexa_lms
        client.admin.command('ping')
        print(f"✅ Connected to MongoDB: {MONGO_URI}")
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        sys.exit(1)
    
    # Check if test users exist
    student_count = db.users.count_documents({"role": "student", "email": {"$regex": "@student\\.edu$"}})
    teacher_count = db.users.count_documents({"role": "teacher", "email": {"$regex": "@faculty\\.edu$"}})
    
    if student_count == 0 and teacher_count == 0:
        print("\n⚠️  No test users found in database.")
        print("Please run: python backend/scripts/generate_test_users.py")
        sys.exit(1)
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'students':
            display_students(db, limit=10 if len(sys.argv) == 2 else None)
        elif command == 'teachers':
            display_teachers(db, limit=10 if len(sys.argv) == 2 else None)
        elif command == 'stats':
            display_statistics(db)
        elif command == 'student' and len(sys.argv) > 2:
            display_detailed_student(db, sys.argv[2])
        elif command == 'teacher' and len(sys.argv) > 2:
            display_detailed_teacher(db, sys.argv[2])
        else:
            print("Usage:")
            print("  python backend/scripts/view_test_users.py                    # Interactive menu")
            print("  python backend/scripts/view_test_users.py students           # View first 10 students")
            print("  python backend/scripts/view_test_users.py teachers           # View first 10 teachers")
            print("  python backend/scripts/view_test_users.py stats              # View statistics")
            print("  python backend/scripts/view_test_users.py student <email>    # View student details")
            print("  python backend/scripts/view_test_users.py teacher <email>    # View teacher details")
    else:
        # Interactive menu
        interactive_menu(db)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
