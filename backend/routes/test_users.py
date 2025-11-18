"""
Test Users API Routes
Provides endpoints to retrieve generated test users for demonstration purposes.
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from datetime import datetime

test_users_bp = Blueprint('test_users', __name__)


@test_users_bp.route('/test-users/students', methods=['GET'])
@jwt_required()
def get_test_students():
    """Get all test students"""
    try:
        db = current_app.db
        
        # Query parameters
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        department = request.args.get('department')
        year = request.args.get('year')
        
        # Build query
        query = {
            "role": "student",
            "email": {"$regex": "@student\\.edu$"}
        }
        
        if department:
            query['department'] = department
        if year:
            query['year'] = year
        
        # Get total count
        total = db.users.count_documents(query)
        
        # Get paginated results
        students = list(db.users.find(query, {'password': 0})
                       .skip((page - 1) * limit)
                       .limit(limit)
                       .sort('name', 1))
        
        # Convert ObjectId to string
        for student in students:
            student['_id'] = str(student['_id'])
            if 'date_of_birth' in student and student['date_of_birth']:
                student['date_of_birth'] = student['date_of_birth'].isoformat()
            if 'created_at' in student:
                student['created_at'] = student['created_at'].isoformat()
            if 'updated_at' in student:
                student['updated_at'] = student['updated_at'].isoformat()
        
        return jsonify({
            'students': students,
            'total': total,
            'page': page,
            'limit': limit,
            'total_pages': (total + limit - 1) // limit
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@test_users_bp.route('/test-users/teachers', methods=['GET'])
@jwt_required()
def get_test_teachers():
    """Get all test teachers"""
    try:
        db = current_app.db
        
        # Query parameters
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        department = request.args.get('department')
        
        # Build query
        query = {
            "role": "teacher",
            "email": {"$regex": "@faculty\\.edu$"}
        }
        
        if department:
            query['department'] = department
        
        # Get total count
        total = db.users.count_documents(query)
        
        # Get paginated results
        teachers = list(db.users.find(query, {'password': 0})
                       .skip((page - 1) * limit)
                       .limit(limit)
                       .sort('name', 1))
        
        # Convert ObjectId to string
        for teacher in teachers:
            teacher['_id'] = str(teacher['_id'])
            if 'date_of_birth' in teacher and teacher['date_of_birth']:
                teacher['date_of_birth'] = teacher['date_of_birth'].isoformat()
            if 'created_at' in teacher:
                teacher['created_at'] = teacher['created_at'].isoformat()
            if 'updated_at' in teacher:
                teacher['updated_at'] = teacher['updated_at'].isoformat()
        
        return jsonify({
            'teachers': teachers,
            'total': total,
            'page': page,
            'limit': limit,
            'total_pages': (total + limit - 1) // limit
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@test_users_bp.route('/test-users/student/<student_id>', methods=['GET'])
@jwt_required()
def get_test_student_by_id(student_id):
    """Get a specific test student by ID"""
    try:
        db = current_app.db
        
        student = db.users.find_one({
            '_id': ObjectId(student_id),
            'role': 'student',
            'email': {"$regex": "@student\\.edu$"}
        }, {'password': 0})
        
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        # Convert ObjectId to string
        student['_id'] = str(student['_id'])
        if 'date_of_birth' in student and student['date_of_birth']:
            student['date_of_birth'] = student['date_of_birth'].isoformat()
        if 'created_at' in student:
            student['created_at'] = student['created_at'].isoformat()
        if 'updated_at' in student:
            student['updated_at'] = student['updated_at'].isoformat()
        
        return jsonify({'student': student}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@test_users_bp.route('/test-users/teacher/<teacher_id>', methods=['GET'])
@jwt_required()
def get_test_teacher_by_id(teacher_id):
    """Get a specific test teacher by ID"""
    try:
        db = current_app.db
        
        teacher = db.users.find_one({
            '_id': ObjectId(teacher_id),
            'role': 'teacher',
            'email': {"$regex": "@faculty\\.edu$"}
        }, {'password': 0})
        
        if not teacher:
            return jsonify({'error': 'Teacher not found'}), 404
        
        # Convert ObjectId to string
        teacher['_id'] = str(teacher['_id'])
        if 'date_of_birth' in teacher and teacher['date_of_birth']:
            teacher['date_of_birth'] = teacher['date_of_birth'].isoformat()
        if 'created_at' in teacher:
            teacher['created_at'] = teacher['created_at'].isoformat()
        if 'updated_at' in teacher:
            teacher['updated_at'] = teacher['updated_at'].isoformat()
        
        return jsonify({'teacher': teacher}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@test_users_bp.route('/test-users/stats', methods=['GET'])
@jwt_required()
def get_test_users_stats():
    """Get statistics about test users"""
    try:
        db = current_app.db
        
        # Count users
        total_students = db.users.count_documents({
            "role": "student",
            "email": {"$regex": "@student\\.edu$"}
        })
        
        total_teachers = db.users.count_documents({
            "role": "teacher",
            "email": {"$regex": "@faculty\\.edu$"}
        })
        
        # Student distribution by department
        student_dept_pipeline = [
            {"$match": {"role": "student", "email": {"$regex": "@student\\.edu$"}}},
            {"$group": {"_id": "$department", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        student_dept_stats = list(db.users.aggregate(student_dept_pipeline))
        
        # Student distribution by year
        student_year_pipeline = [
            {"$match": {"role": "student", "email": {"$regex": "@student\\.edu$"}}},
            {"$group": {"_id": "$year", "count": {"$sum": 1}}},
            {"$sort": {"_id": 1}}
        ]
        student_year_stats = list(db.users.aggregate(student_year_pipeline))
        
        # Teacher distribution by department
        teacher_dept_pipeline = [
            {"$match": {"role": "teacher", "email": {"$regex": "@faculty\\.edu$"}}},
            {"$group": {"_id": "$department", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        teacher_dept_stats = list(db.users.aggregate(teacher_dept_pipeline))
        
        # Teacher distribution by designation
        teacher_desig_pipeline = [
            {"$match": {"role": "teacher", "email": {"$regex": "@faculty\\.edu$"}}},
            {"$group": {"_id": "$designation", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        teacher_desig_stats = list(db.users.aggregate(teacher_desig_pipeline))
        
        return jsonify({
            'total_students': total_students,
            'total_teachers': total_teachers,
            'student_by_department': student_dept_stats,
            'student_by_year': student_year_stats,
            'teacher_by_department': teacher_dept_stats,
            'teacher_by_designation': teacher_desig_stats
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@test_users_bp.route('/test-users/search', methods=['GET'])
@jwt_required()
def search_test_users():
    """Search test users by name or email"""
    try:
        db = current_app.db
        
        query_text = request.args.get('q', '').strip()
        role = request.args.get('role')  # student or teacher
        limit = int(request.args.get('limit', 20))
        
        if not query_text:
            return jsonify({'error': 'Search query is required'}), 400
        
        # Build query
        search_query = {
            "$or": [
                {"name": {"$regex": query_text, "$options": "i"}},
                {"email": {"$regex": query_text, "$options": "i"}}
            ]
        }
        
        if role == 'student':
            search_query["role"] = "student"
            search_query["email"] = {"$regex": "@student\\.edu$"}
        elif role == 'teacher':
            search_query["role"] = "teacher"
            search_query["email"] = {"$regex": "@faculty\\.edu$"}
        else:
            # Search both
            search_query["$and"] = [
                {"$or": [
                    {"email": {"$regex": "@student\\.edu$"}},
                    {"email": {"$regex": "@faculty\\.edu$"}}
                ]}
            ]
        
        # Get results
        users = list(db.users.find(search_query, {'password': 0})
                    .limit(limit)
                    .sort('name', 1))
        
        # Convert ObjectId to string
        for user in users:
            user['_id'] = str(user['_id'])
            if 'date_of_birth' in user and user['date_of_birth']:
                user['date_of_birth'] = user['date_of_birth'].isoformat()
            if 'created_at' in user:
                user['created_at'] = user['created_at'].isoformat()
            if 'updated_at' in user:
                user['updated_at'] = user['updated_at'].isoformat()
        
        return jsonify({
            'results': users,
            'count': len(users),
            'query': query_text
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@test_users_bp.route('/test-users/departments', methods=['GET'])
@jwt_required()
def get_departments():
    """Get list of all departments"""
    try:
        db = current_app.db
        
        # Get unique departments
        departments = db.users.distinct('department', {
            "email": {"$regex": "@(student|faculty)\\.edu$"}
        })
        
        return jsonify({
            'departments': sorted(departments)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@test_users_bp.route('/test-users/sample', methods=['GET'])
@jwt_required()
def get_sample_users():
    """Get sample users for quick demonstration"""
    try:
        db = current_app.db
        
        # Get 5 sample students
        sample_students = list(db.users.find({
            "role": "student",
            "email": {"$regex": "@student\\.edu$"}
        }, {'password': 0}).limit(5))
        
        # Get 3 sample teachers
        sample_teachers = list(db.users.find({
            "role": "teacher",
            "email": {"$regex": "@faculty\\.edu$"}
        }, {'password': 0}).limit(3))
        
        # Convert ObjectId to string
        for user in sample_students + sample_teachers:
            user['_id'] = str(user['_id'])
            if 'date_of_birth' in user and user['date_of_birth']:
                user['date_of_birth'] = user['date_of_birth'].isoformat()
            if 'created_at' in user:
                user['created_at'] = user['created_at'].isoformat()
            if 'updated_at' in user:
                user['updated_at'] = user['updated_at'].isoformat()
        
        return jsonify({
            'sample_students': sample_students,
            'sample_teachers': sample_teachers
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
