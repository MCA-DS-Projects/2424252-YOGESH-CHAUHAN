"""
Test script to verify learner analytics categorization
Run this to see how students are being categorized
"""
from pymongo import MongoClient
from datetime import datetime, timedelta
import statistics

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/edunexa_lms')
db = client.edunexa_lms

print("=" * 80)
print("LEARNER ANALYTICS TEST")
print("=" * 80)

# Get all students
students = list(db.users.find({'role': 'student'}))
print(f"\nTotal students in database: {len(students)}")

if len(students) == 0:
    print("\n⚠️  No students found in database!")
    print("Please seed the database with student data first.")
    exit(0)

# Analyze each student
slow_count = 0
fast_count = 0
normal_count = 0

print("\n" + "-" * 80)
print("STUDENT ANALYSIS")
print("-" * 80)

for student in students[:10]:  # Show first 10 students
    student_id = str(student['_id'])
    student_name = student.get('name', 'Unknown')
    
    # Get enrollments
    enrollments = list(db.enrollments.find({'student_id': student_id}))
    
    # Get submissions
    all_submissions = list(db.submissions.find({'student_id': student_id}))
    recent_submissions = list(db.submissions.find({
        'student_id': student_id,
        'submitted_at': {'$gte': datetime.utcnow() - timedelta(days=30)}
    }))
    
    # Calculate metrics
    if enrollments:
        progress_rates = []
        total_progress = 0
        for enrollment in enrollments:
            enrollment_date = enrollment.get('enrolled_at', datetime.utcnow())
            current_progress = enrollment.get('progress', 0)
            total_progress += current_progress
            days_enrolled = max(1, (datetime.utcnow() - enrollment_date).days)
            progress_rate = current_progress / days_enrolled
            progress_rates.append(progress_rate)
        
        avg_progress_rate = statistics.mean(progress_rates)
        avg_progress = total_progress / len(enrollments)
    else:
        avg_progress_rate = 0
        avg_progress = 0
    
    submission_frequency = len(recent_submissions) / 30
    
    graded_submissions = [sub for sub in all_submissions if sub.get('grade') is not None]
    avg_grade = statistics.mean([sub['grade'] for sub in graded_submissions]) if graded_submissions else 0
    
    # Determine pace (using same logic as backend)
    if (avg_progress_rate > 1.5 or 
        (avg_grade > 75 and submission_frequency > 0.1) or 
        submission_frequency > 0.2 or
        (avg_progress > 60 and len(recent_submissions) > 2)):
        pace = 'fast'
        fast_count += 1
    elif (avg_progress_rate < 0.8 and submission_frequency < 0.1) or avg_grade < 50:
        pace = 'slow'
        slow_count += 1
    else:
        pace = 'normal'
        normal_count += 1
    
    print(f"\n{student_name} (ID: {student_id[:8]}...)")
    print(f"  Enrollments: {len(enrollments)}")
    print(f"  Avg Progress: {avg_progress:.1f}%")
    print(f"  Progress Rate: {avg_progress_rate:.2f}% per day")
    print(f"  Recent Submissions (30d): {len(recent_submissions)}")
    print(f"  Submission Frequency: {submission_frequency:.3f} per day")
    print(f"  Total Submissions: {len(all_submissions)}")
    print(f"  Avg Grade: {avg_grade:.1f}%")
    print(f"  ➜ PACE: {pace.upper()}")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Total Students Analyzed: {min(len(students), 10)}")
print(f"Fast Learners: {fast_count}")
print(f"Slow Learners: {slow_count}")
print(f"Normal Learners: {normal_count}")
print("\n✅ Test complete!")
