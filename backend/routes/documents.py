from flask import Blueprint, request, jsonify, current_app, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from bson import ObjectId
from datetime import datetime
import os
import uuid

documents_bp = Blueprint('documents', __name__)

# Configuration
UPLOAD_FOLDER = 'uploads/documents'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'ppt', 'pptx', 'txt', 'xls', 'xlsx'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def require_teacher(f):
    """Decorator to ensure only teachers can access the endpoint"""
    @jwt_required()
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        db = current_app.db
        
        user = db.users.find_one({'_id': ObjectId(user_id)})
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if user.get('role') != 'teacher':
            return jsonify({'error': 'Only teachers can upload documents'}), 403
        
        return f(*args, **kwargs)
    
    decorated_function.__name__ = f.__name__
    return decorated_function

@documents_bp.route('/upload', methods=['POST'])
@require_teacher
def upload_document():
    """Upload a document file (teachers only)"""
    try:
        user_id = get_jwt_identity()
        db = current_app.db
        
        # Check if file is in request
        if 'document' not in request.files:
            return jsonify({'error': 'No document file provided'}), 400
        
        file = request.files['document']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file type
        if not allowed_file(file.filename):
            return jsonify({'error': f'Invalid file type. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'}), 400
        
        # Get additional metadata from form data
        title = request.form.get('title', '')
        description = request.form.get('description', '')
        course_id = request.form.get('courseId', '')
        
        # Generate unique filename
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        # Save file
        file.save(file_path)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Create document record in database
        document_doc = {
            'filename': unique_filename,
            'originalFilename': secure_filename(file.filename),
            'title': title or secure_filename(file.filename),
            'description': description,
            'filePath': file_path,
            'fileSize': file_size,
            'uploadedBy': ObjectId(user_id),
            'courseId': ObjectId(course_id) if course_id else None,
            'uploadedAt': datetime.utcnow(),
            'downloads': 0,
            'status': 'active'
        }
        
        result = db.documents.insert_one(document_doc)
        document_id = str(result.inserted_id)
        
        # Update course if courseId provided
        if course_id:
            db.courses.update_one(
                {'_id': ObjectId(course_id)},
                {
                    '$push': {
                        'documents': {
                            'documentId': ObjectId(document_id),
                            'title': document_doc['title'],
                            'addedAt': datetime.utcnow()
                        }
                    }
                }
            )
        
        return jsonify({
            'message': 'Document uploaded successfully',
            'documentId': document_id,
            'documentUrl': f'/api/documents/download/{document_id}',
            'filename': unique_filename,
            'title': document_doc['title'],
            'url': f'/api/documents/download/{document_id}'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@documents_bp.route('/download/<document_id>', methods=['GET'])
@jwt_required()
def download_document(document_id):
    """Download a document file"""
    try:
        db = current_app.db
        
        # Get document record
        document = db.documents.find_one({'_id': ObjectId(document_id)})
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        # Increment download count
        db.documents.update_one(
            {'_id': ObjectId(document_id)},
            {'$inc': {'downloads': 1}}
        )
        
        # Get the directory and filename
        directory = os.path.dirname(document['filePath'])
        filename = document['filename']
        
        return send_from_directory(directory, filename, as_attachment=True, download_name=document['originalFilename'])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@documents_bp.route('/view/<document_id>', methods=['GET'])
@jwt_required()
def view_document(document_id):
    """View a document file (inline)"""
    try:
        db = current_app.db
        
        # Get document record
        document = db.documents.find_one({'_id': ObjectId(document_id)})
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        # Get the directory and filename
        directory = os.path.dirname(document['filePath'])
        filename = document['filename']
        
        return send_from_directory(directory, filename, as_attachment=False)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@documents_bp.route('/list', methods=['GET'])
@jwt_required()
def list_documents():
    """List all documents (with optional course filter)"""
    try:
        db = current_app.db
        user_id = get_jwt_identity()
        
        # Get query parameters
        course_id = request.args.get('courseId')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        
        # Build query
        query = {'status': 'active'}
        if course_id:
            query['courseId'] = ObjectId(course_id)
        
        # Get user to check role
        user = db.users.find_one({'_id': ObjectId(user_id)})
        
        # If student, only show documents from enrolled courses
        if user.get('role') == 'student':
            enrolled_courses = user.get('enrolledCourses', [])
            query['courseId'] = {'$in': [ObjectId(c) for c in enrolled_courses]}
        
        # Get total count
        total = db.documents.count_documents(query)
        
        # Get documents with pagination
        documents = list(db.documents.find(query)
                        .sort('uploadedAt', -1)
                        .skip((page - 1) * limit)
                        .limit(limit))
        
        # Format response
        document_list = []
        for doc in documents:
            uploader = db.users.find_one({'_id': doc['uploadedBy']})
            document_list.append({
                'id': str(doc['_id']),
                'title': doc['title'],
                'description': doc.get('description', ''),
                'filename': doc['originalFilename'],
                'fileSize': doc['fileSize'],
                'uploadedBy': {
                    'id': str(doc['uploadedBy']),
                    'name': uploader.get('name', 'Unknown') if uploader else 'Unknown'
                },
                'uploadedAt': doc['uploadedAt'].isoformat(),
                'downloads': doc.get('downloads', 0),
                'documentUrl': f'/api/documents/download/{str(doc["_id"])}'
            })
        
        return jsonify({
            'documents': document_list,
            'total': total,
            'page': page,
            'limit': limit,
            'totalPages': (total + limit - 1) // limit
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@documents_bp.route('/<document_id>', methods=['GET'])
@jwt_required()
def get_document(document_id):
    """Get document details"""
    try:
        db = current_app.db
        
        document = db.documents.find_one({'_id': ObjectId(document_id)})
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        uploader = db.users.find_one({'_id': document['uploadedBy']})
        
        return jsonify({
            'id': str(document['_id']),
            'title': document['title'],
            'description': document.get('description', ''),
            'filename': document['originalFilename'],
            'fileSize': document['fileSize'],
            'uploadedBy': {
                'id': str(document['uploadedBy']),
                'name': uploader.get('name', 'Unknown') if uploader else 'Unknown'
            },
            'uploadedAt': document['uploadedAt'].isoformat(),
            'downloads': document.get('downloads', 0),
            'documentUrl': f'/api/documents/download/{document_id}'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@documents_bp.route('/<document_id>', methods=['DELETE'])
@require_teacher
def delete_document(document_id):
    """Delete a document (teachers only)"""
    try:
        user_id = get_jwt_identity()
        db = current_app.db
        
        document = db.documents.find_one({'_id': ObjectId(document_id)})
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        # Check if user is the uploader
        if str(document['uploadedBy']) != user_id:
            return jsonify({'error': 'You can only delete your own documents'}), 403
        
        # Delete file from filesystem
        if os.path.exists(document['filePath']):
            os.remove(document['filePath'])
        
        # Delete from database
        db.documents.delete_one({'_id': ObjectId(document_id)})
        
        # Remove from courses
        db.courses.update_many(
            {},
            {'$pull': {'documents': {'documentId': ObjectId(document_id)}}}
        )
        
        return jsonify({'message': 'Document deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@documents_bp.route('/<document_id>', methods=['PUT'])
@require_teacher
def update_document(document_id):
    """Update document metadata (teachers only)"""
    try:
        user_id = get_jwt_identity()
        db = current_app.db
        data = request.get_json()
        
        document = db.documents.find_one({'_id': ObjectId(document_id)})
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        # Check if user is the uploader
        if str(document['uploadedBy']) != user_id:
            return jsonify({'error': 'You can only update your own documents'}), 403
        
        # Update fields
        update_data = {}
        if 'title' in data:
            update_data['title'] = data['title']
        if 'description' in data:
            update_data['description'] = data['description']
        
        if update_data:
            db.documents.update_one(
                {'_id': ObjectId(document_id)},
                {'$set': update_data}
            )
        
        return jsonify({'message': 'Document updated successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
