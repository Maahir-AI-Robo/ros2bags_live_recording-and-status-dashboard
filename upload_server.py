#!/usr/bin/env python3
"""
Simple Upload Server for ROS2 Dashboard
Handles chunked uploads with resume capability
"""

from flask import Flask, request, jsonify  # type: ignore
from flask_cors import CORS  # type: ignore
import os
import uuid
import hashlib
import json
from datetime import datetime
from typing import Dict, Set, Any, Tuple

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_DIR = os.path.expanduser("~/ros2_uploads")
TEMP_DIR = os.path.join(UPLOAD_DIR, "temp")
COMPLETED_DIR = os.path.join(UPLOAD_DIR, "completed")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(COMPLETED_DIR, exist_ok=True)

# In-memory storage for upload sessions
upload_sessions: Dict[str, Dict[str, Any]] = {}


@app.route('/health', methods=['GET'])
def health_check() -> Tuple[Any, int]:
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()}), 200


@app.route('/upload/init', methods=['POST'])
def initialize_upload() -> Tuple[Any, int]:
    """Initialize a new upload session"""
    try:
        data = request.json
        filename = data.get('filename')
        filesize = data.get('filesize')
        chunks = data.get('chunks')
        metadata = data.get('metadata', {})
        checksum = data.get('checksum')
        
        # Generate upload ID
        upload_id = str(uuid.uuid4())
        
        # Create session
        upload_sessions[upload_id] = {
            'filename': filename,
            'filesize': filesize,
            'chunks': chunks,
            'metadata': metadata,
            'checksum': checksum,
            'received_chunks': set(),  # type: ignore
            'created_at': datetime.now().isoformat(),
            'temp_dir': os.path.join(TEMP_DIR, upload_id)
        }
        
        # Create temp directory for chunks
        os.makedirs(upload_sessions[upload_id]['temp_dir'], exist_ok=True)
        
        print(f"📥 Initialized upload: {filename} ({filesize} bytes, {chunks} chunks) - ID: {upload_id}")
        
        return jsonify({
            'success': True,
            'upload_id': upload_id,
            'message': 'Upload session created'
        }), 200
        
    except Exception as e:
        print(f"Error initializing upload: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/upload/chunk', methods=['POST'])
def upload_chunk() -> Tuple[Any, int]:
    """Upload a single chunk"""
    try:
        upload_id = request.form.get('upload_id')
        chunk_index = int(request.form.get('chunk_index'))
        chunk_total = int(request.form.get('chunk_total'))
        
        if upload_id not in upload_sessions:
            return jsonify({'success': False, 'error': 'Invalid upload ID'}), 400
            
        session = upload_sessions[upload_id]
        
        # Get chunk data
        chunk_file = request.files.get('chunk')
        if not chunk_file:
            return jsonify({'success': False, 'error': 'No chunk data'}), 400
            
        # Save chunk
        chunk_path = os.path.join(session['temp_dir'], f'chunk_{chunk_index}')
        chunk_file.save(chunk_path)
        
        # Mark chunk as received
        session['received_chunks'].add(chunk_index)
        
        progress = len(session['received_chunks']) / chunk_total * 100
        print(f"📦 Received chunk {chunk_index + 1}/{chunk_total} for {session['filename']} ({progress:.1f}%)")
        
        return jsonify({
            'success': True,
            'received_chunks': len(session['received_chunks']),
            'total_chunks': chunk_total,
            'progress': progress
        }), 200
        
    except Exception as e:
        print(f"Error uploading chunk: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/upload/finalize', methods=['POST'])
def finalize_upload() -> Tuple[Any, int]:
    """Finalize upload by combining chunks"""
    try:
        data = request.json
        upload_id = data.get('upload_id')
        checksum = data.get('checksum')
        
        if upload_id not in upload_sessions:
            return jsonify({'success': False, 'error': 'Invalid upload ID'}), 400
            
        session = upload_sessions[upload_id]
        
        # Verify all chunks received
        if len(session['received_chunks']) != session['chunks']:
            return jsonify({
                'success': False,
                'error': f"Missing chunks: {len(session['received_chunks'])}/{session['chunks']}"
            }), 400
            
        # Combine chunks
        output_path = os.path.join(COMPLETED_DIR, session['filename'])
        
        with open(output_path, 'wb') as output_file:
            for i in range(session['chunks']):
                chunk_path = os.path.join(session['temp_dir'], f'chunk_{i}')
                with open(chunk_path, 'rb') as chunk_file:
                    output_file.write(chunk_file.read())
                    
        # Verify checksum
        calculated_checksum = calculate_checksum(output_path)
        
        if checksum and calculated_checksum != checksum:
            os.remove(output_path)
            return jsonify({
                'success': False,
                'error': 'Checksum mismatch'
            }), 400
            
        # Clean up temp files
        for i in range(session['chunks']):
            chunk_path = os.path.join(session['temp_dir'], f'chunk_{i}')
            if os.path.exists(chunk_path):
                os.remove(chunk_path)
        os.rmdir(session['temp_dir'])
        
        # Save metadata
        metadata_path = output_path + '.metadata.json'
        with open(metadata_path, 'w') as f:
            json.dump({
                'filename': session['filename'],
                'filesize': session['filesize'],
                'checksum': calculated_checksum,
                'metadata': session['metadata'],
                'uploaded_at': datetime.now().isoformat()
            }, f, indent=2)
            
        print(f"✅ Upload completed: {session['filename']} -> {output_path}")
        
        # Remove session
        del upload_sessions[upload_id]
        
        return jsonify({
            'success': True,
            'message': 'Upload completed',
            'file_path': output_path,
            'checksum': calculated_checksum
        }), 200
        
    except Exception as e:
        print(f"Error finalizing upload: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/upload/status/<upload_id>', methods=['GET'])
def upload_status(upload_id: str) -> Tuple[Any, int]:
    """Get upload status"""
    if upload_id not in upload_sessions:
        return jsonify({'success': False, 'error': 'Invalid upload ID'}), 404
        
    session = upload_sessions[upload_id]
    
    return jsonify({
        'success': True,
        'filename': session['filename'],
        'received_chunks': len(session['received_chunks']),
        'total_chunks': session['chunks'],
        'progress': len(session['received_chunks']) / session['chunks'] * 100
    }), 200


@app.route('/uploads', methods=['GET'])
def list_uploads() -> Tuple[Any, int]:
    """List completed uploads"""
    uploads = []
    
    for filename in os.listdir(COMPLETED_DIR):
        if filename.endswith('.metadata.json'):
            continue
            
        filepath = os.path.join(COMPLETED_DIR, filename)
        metadata_path = filepath + '.metadata.json'
        
        upload_info = {
            'filename': filename,
            'size': os.path.getsize(filepath),
            'uploaded_at': datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat()
        }
        
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
                upload_info.update(metadata)
                
        uploads.append(upload_info)
        
    return jsonify({'success': True, 'uploads': uploads}), 200


def calculate_checksum(file_path: str) -> str:
    """Calculate MD5 checksum"""
    md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            md5.update(chunk)
    return md5.hexdigest()


if __name__ == '__main__':
    print(f"""
╔═══════════════════════════════════════════════════════════╗
║          ROS2 Dashboard Upload Server                      ║
╠═══════════════════════════════════════════════════════════╣
║  Upload Directory: {UPLOAD_DIR:<37} ║
║  Server URL: http://localhost:8080                        ║
║  Health Check: http://localhost:8080/health               ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    app.run(host='0.0.0.0', port=8080, debug=True)
