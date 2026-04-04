from flask import Flask, render_template, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
import os
import werkzeug.utils
from lsb import encode, decode, encode_file, decode_file

app = Flask(__name__)

# Configurations
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ENCODED_FOLDER'] = 'encoded_files'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024 # 50 MB max
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stegano.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

IMG_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.bmp'}

db = SQLAlchemy(app)

class ImageRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_filename = db.Column(db.String(255), nullable=False)
    encoded_filename = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

# Setup upload folder safely
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['ENCODED_FOLDER'], exist_ok=True)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/encode', methods=['POST'])
def handle_encode():
    """Handles the encoding request"""
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided. Please upload an image.'}), 400
        
    file = request.files['image']
    message = request.form.get('message', '')
    password = request.form.get('password', '')
    
    if file.filename == '':
        return jsonify({'error': 'No selected file.'}), 400
        
    if not message:
        return jsonify({'error': 'Message cannot be empty.'}), 400
        
    try:
        filename = werkzeug.utils.secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath) # Save the initial upload to disk
        
        # Routing logic: LSB for images, EOF for others
        _, ext = os.path.splitext(filename)
        if ext.lower() in IMG_EXTENSIONS:
            output_path = encode(filepath, message, password if password else None, output_dir=app.config['ENCODED_FOLDER'])
        else:
            output_path = encode_file(filepath, message, password if password else None, output_dir=app.config['ENCODED_FOLDER'])
        
        # Cleanup original upload to save space
        if os.path.exists(filepath):
            os.remove(filepath)
            
        # Log to Database
        try:
            output_basename = os.path.basename(output_path)
            new_record = ImageRecord(
                original_filename=filename, 
                encoded_filename=output_basename
            )
            db.session.add(new_record)
            db.session.commit()
        except Exception as db_err:
            print(f"DB Error: {db_err}")
            
        # Send the encoded file back to user
        return send_file(output_path, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/decode', methods=['POST'])
def handle_decode():
    """Handles the decoding request"""
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided. Please upload an encoded image.'}), 400
        
    file = request.files['image']
    password = request.form.get('password', '')
    
    if file.filename == '':
        return jsonify({'error': 'No selected file.'}), 400
        
    try:
        filename = werkzeug.utils.secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Routing logic: LSB for images, EOF for others
        _, ext = os.path.splitext(filename)
        if ext.lower() in IMG_EXTENSIONS:
            message = decode(filepath, password if password else None)
        else:
            message = decode_file(filepath, password if password else None)
        
        # Cleanup upload
        if os.path.exists(filepath):
            os.remove(filepath)
            
        return jsonify({'message': message})
    except Exception as e:
        # Prevent old files from piling up if there's an error
        if 'filepath' in locals() and os.path.exists(filepath):
             os.remove(filepath)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=8080) # Started on 8080
