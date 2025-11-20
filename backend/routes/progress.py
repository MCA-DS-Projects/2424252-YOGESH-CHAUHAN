from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from datetime import datetime
from utils.api_response import error_response, success_response, prepare_api_response
from utils.case_converter import convert_dict_keys_to_camel

progress_bp = Blueprint('progress', __name__)

@progress_bp.route('/course/<course_id>', methods=['GET'])
@jwt_required()
def get_course_progress(course_id):
    """Get student's progress for a specific course"""
    try:
        user_id = get_jwt_identity()
        db = current_app.db
        
        # Check if user is student
        user = db.users.find_one({'_id': ObjectId(user_id)})
        if not user or user['role'] != 'student':
            return error_response('Only students can view progress', 403)
        
        # Get or create progress record
        progress = db.progress.find_one({
            'course_id': course_id,
            'student_id': user_id
        })
        
        # If no progress record exists, return default state
        if not progress:
            default_progress = {
                'course_id': course_id,
                'student_id': user_id,
                'started': False,
                'last_accessed': None,
                'overall_progress': 0,
                'completed_materials': []
            }
            return prepare_api_response({'progress': default_progress}, status_code=200)
        
        # Convert ObjectId to string
        progress['_id'] = str(progress['_id'])
        
        # Format datetime fields
        if progress.get('last_accessed'):
            progress['last_accessed'] = progress['last_accessed'].isoformat()
        if progress.get('created_at'):
            progress['created_at'] = progress['created_at'].isoformat()
        if progress.get('updated_at'):
            progress['updated_at'] = progress['updated_at'].isoformat()
        
        return prepare_api_response({'progress': progress}, status_code=200)
        
    except Exception as e:
        return error_response(str(e), 500)

@progress_bp.route('/course/<course_id>/start', methods=['POST'])
@jwt_required()
def start_course(course_id):
    """Initialize progress tracking when student first accesses a course"""
    try:
        user_id = get_jwt_identity()
        db = current_app.db
        
        # Check if user is student
        user = db.users.find_one({'_id': ObjectId(user_id)})
        if not user or user['role'] != 'student':
            return error_response('Only students can start courses', 403)
        
        # Check if course exists
        course = db.courses.find_one({'_id': ObjectId(course_id)})
        if not course:
            return error_response('Course not found', 404)
        
        # Check if student is enrolled
        enrollment = db.enrollments.find_one({
            'course_id': course_id,
            'student_id': user_id
        })
        
        if not enrollment:
            return error_response('Not enrolled in this course', 403)
        
        # Check if progress record already exists
        existing_progress = db.progress.find_one({
            'course_id': course_id,
            'student_id': user_id
        })
        
        current_time = datetime.utcnow()
        
        if existing_progress:
            # Update existing progress record
            db.progress.update_one(
                {'_id': existing_progress['_id']},
                {
                    '$set': {
                        'started': True,
                        'last_accessed': current_time,
                        'updated_at': current_time
                    }
                }
            )
            
            progress_data = {
                'course_id': course_id,
                'student_id': user_id,
                'started': True,
                'last_accessed': current_time.isoformat()
            }
            return success_response('Progress updated', {'progress': progress_data}, 200)
        else:
            # Create new progress record
            progress_data = {
                'course_id': course_id,
                'student_id': user_id,
                'started': True,
                'last_accessed': current_time,
                'completed_materials': [],
                'overall_progress': 0,
                'created_at': current_time,
                'updated_at': current_time
            }
            
            result = db.progress.insert_one(progress_data)
            progress_data['_id'] = str(result.inserted_id)
            progress_data['last_accessed'] = current_time.isoformat()
            progress_data['created_at'] = current_time.isoformat()
            progress_data['updated_at'] = current_time.isoformat()
            
            # IMPORTANT: Also initialize progress in enrollment record
            db.enrollments.update_one(
                {
                    'student_id': user_id,
                    'course_id': course_id
                },
                {
                    '$set': {
                        'progress': 0,
                        'updated_at': current_time
                    }
                }
            )
            
            return success_response('Progress initialized', {'progress': progress_data}, 201)
        
    except Exception as e:
        return error_response(str(e), 500)
