from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models.document import Document
from app.models.transaction import Transaction
from app.services.ocr import process_document
from app.services.nlp import categorize_transactions
import os
from werkzeug.utils import secure_filename
from datetime import datetime

upload_bp = Blueprint('upload', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_bp.route('/document', methods=['POST'])
def upload_document():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
    
    # Get user_id from JWT token
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Authorization token required'}), 401
    
    try:
        from jwt import decode
        payload = decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = payload['user_id']
    except:
        return jsonify({'error': 'Invalid token'}), 401
    
    # Save file
    filename = secure_filename(file.filename)
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    
    # Create document record
    document = Document(
        user_id=user_id,
        filename=filename,
        file_path=file_path,
        document_type=request.form.get('document_type', 'unknown')
    )
    db.session.add(document)
    db.session.commit()
    
    # Process document asynchronously
    process_document.delay(document.id)
    
    return jsonify({
        'message': 'Document uploaded successfully',
        'document': document.to_dict()
    }), 201

@upload_bp.route('/documents', methods=['GET'])
def get_documents():
    # Get user_id from JWT token
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Authorization token required'}), 401
    
    try:
        from jwt import decode
        payload = decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = payload['user_id']
    except:
        return jsonify({'error': 'Invalid token'}), 401
    
    # Get all documents for user
    documents = Document.query.filter_by(user_id=user_id).all()
    return jsonify({
        'documents': [doc.to_dict() for doc in documents]
    }), 200 