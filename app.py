import os
import logging
from datetime import datetime, timedelta

log_dir = "logging"
os.makedirs(log_dir, exist_ok=True)
log_filename = f"{log_dir}/app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format='%(message)s'
)
logging.info("Test log entry: Logging is working.")

print("Logging to:", os.path.abspath(log_filename))  # Add this for debugging



from flask import Flask, request, jsonify, send_from_directory, make_response
from flask_cors import CORS
from pymongo import MongoClient

from dotenv import load_dotenv
import pytz
import openai
import json
from bson import ObjectId
import httpx
import boto3
from botocore.exceptions import ClientError
import io
import asyncio
import hashlib
#from concurrent.futures import ThreadPoolExecutor
import mylang4  # Import the LangChain module
#from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
#from question_prompt import QuestionPromptGenerator
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from Utility.pdfmaker import CreatePDF

import re
import gc
import psutil

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, static_folder='dist', static_url_path='')

# Configure CORS
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Initialize MongoDB with configurable database and collections
try:
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
    DB_NAME = os.getenv('DB_NAME', 'question_paper_db')
    REQUEST_COLLECTION = os.getenv('REQUEST_COLLECTION', 'question_requests')
    PAPER_COLLECTION = os.getenv('PAPER_COLLECTION', 'question_papers')
    
    client = MongoClient(MONGODB_URI)
    db = client[DB_NAME]
    requests_collection = db[REQUEST_COLLECTION]
    papers_collection = db[PAPER_COLLECTION]
    logging.info("✅ MongoDB Connection Successful!")
except Exception as e:
    logging.info(f"❌ MongoDB Connection Error: {e}")
    db = None

# Initialize OpenAI client
try:
    http_client = httpx.Client(
        base_url="https://api.openai.com/v1",
        timeout=60.0,
        follow_redirects=True
    )
    
    openai_client = openai.OpenAI(
        api_key=os.getenv('OPENAI_API_KEY'),
        http_client=http_client
    )
    logging.info("✅ OpenAI client initialized successfully")
except Exception as e:
    logging.info(f"❌ Error initializing OpenAI client: {e}")
    raise

# Initialize AWS S3 client
try:
    s3_client = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_REGION', 'us-east-1')
    )
    S3_BUCKET = os.getenv('S3_BUCKET_NAME')
    NOTES_BUCKET = os.getenv('NOTES_BUCKET_NAME')  # Separate bucket for notes
    logging.info("✅ AWS S3 Connection Successful!")
except Exception as e:
    logging.info(f"❌ AWS S3 Connection Error: {e}")
    s3_client = None

# Add memory monitoring function
def monitor_memory():
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    return memory_info.rss / 1024 / 1024  # Convert to MB

# Add cleanup function
def cleanup_memory():
    gc.collect()
    if hasattr(psutil.Process(), "memory_maps"):
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == 'python':
                try:
                    proc.kill()
                except:
                    pass

@app.route('/')
def serve():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')


# Initialize the question generator
#question_generator = QuestionPromptGenerator()
@app.route('/api/generate-questions', methods=['POST'])
def generate_questions():
    try:
        logging.info("Received request at /api/generate-questions")
        data = request.get_json()

        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        # Validate required fields
        required_fields = ['subjectName', 'classGrade', 'topics']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f"Missing required field: {field}"}), 400

        # Insert request metadata
        data['created_at'] = datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
        request_id = requests_collection.insert_one(data).inserted_id

        # Load vectorstore if exists
        vectorstore_path = "vectorstores/latest"
        vectorstore = None
        if os.path.exists(vectorstore_path):
            try:
                embeddings = OpenAIEmbeddings()
                vectorstore = FAISS.load_local(vectorstore_path, embeddings, allow_dangerous_deserialization=True)
                logging.info(f"Loaded vectorstore from {vectorstore_path}")
            except Exception as e:
                logging.warning(f"Vectorstore load failed: {e}")

        # Generate questions for each topic in batches
        all_questions = []
        for topic in data['topics']:
            topic_data = {
                **topic,
                'subjectName': data['subjectName'],
                'classGrade': data['classGrade']
            }

            try:
                num_qs = int(topic.get('numQuestions', 1))
            except ValueError:
                num_qs = 1

            batch_size = 5
            topic_questions = []

            for i in range(0, num_qs, batch_size):
                current_batch = min(batch_size, num_qs - i)
                batch_data = {**topic_data, 'numQuestions': current_batch}

                questions = mylang4.question_generator.generate_questions(batch_data, vectorstore)
                topic_questions.extend(questions['questions'])

                # Free memory
                gc.collect()

            all_questions.append({
                'topic': topic.get('sectionName', ''),
                'questions': topic_questions,
                'cached': False
            })

        # Save to MongoDB
        paper_data = {
            'request_id': str(request_id),
            'questions': all_questions,
            'created_at': datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S'),
            'previous_paper_id': data.get('previous_paper_id')
        }
        paper_id = papers_collection.insert_one(paper_data).inserted_id

        # Generate PDFs
        pdf_filename = f"question_paper_{paper_id}.pdf"
        pdf_buffer = CreatePDF.generate(
            all_questions,
            pdf_filename,
            class_grade=data['classGrade'],
            subject_name=data['subjectName']
        )

        s3_client.upload_fileobj(
            pdf_buffer,
            S3_BUCKET,
            pdf_filename,
            ExtraArgs={'ContentType': 'application/pdf'}
        )

        pdf_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET, 'Key': pdf_filename},
            ExpiresIn=3600
        )

        # Final cleanups
        if os.path.exists(vectorstore_path):
            try:
                import shutil
                shutil.rmtree(vectorstore_path)
                logging.info(f"Cleaned up vectorstore directory: {vectorstore_path}")
            except Exception as e:
                logging.warning(f"Failed to delete vectorstore directory: {e}")

        

        return jsonify({
            'success': True,
            'paper_id': str(paper_id),
            'questions': all_questions,
            'pdf_url': pdf_url
        })

    except Exception as e:
        logging.error(f"Exception in /generate-questions: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/download-pdf/<paper_id>', methods=['GET'])
def download_pdf(paper_id):
    try:
        filename = f"question_paper_{paper_id}.pdf"
        # Generate a pre-signed URL for the S3 object
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': S3_BUCKET,
                'Key': filename
            },
            ExpiresIn=3600  # URL expires in 1 hour
        )
        
        return jsonify({
            'success': True,
            'url': url
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/upload-note', methods=['POST'])
def upload_note():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400

        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'success': False, 'error': 'Only PDF files are allowed'}), 400

        # Generate unique filename
        filename = f"notes/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"

        temp_folder = 'temp_uploads'
        os.makedirs(temp_folder, exist_ok=True)
        local_path = os.path.join(temp_folder, 'latest.pdf')
        logging.info(f"Saving file to: {local_path}")
        file.save(local_path)

        # Upload to S3 (no metadata)
        s3_client.upload_fileobj(
            file,
            NOTES_BUCKET,
            filename,
            ExtraArgs={'ContentType': 'application/pdf'}
        )
        logging.info(f"File uploaded to S3: {filename}")
        # Save note metadata to MongoDB
        note_data = {
            'filename': filename,
            'original_name': file.filename,
            'uploaded_at': datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S'),
            's3_url': f"s3://{NOTES_BUCKET}/{filename}"
        }
        notes_collection = db['notes']
        note_id = notes_collection.insert_one(note_data).inserted_id

        return jsonify({
            'success': True,
            'note_id': str(note_id),
            'filename': file.filename
        })

    except Exception as e:
        logging.info(f"Error uploading note: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/analyse-note', methods=['POST'])
def analyse_note():
    try:
        local_pdf_path = 'temp_uploads/latest.pdf'
        if not os.path.exists(local_pdf_path):
            return jsonify({'success': False, 'error': 'No PDF found to analyze'}), 400

        vectorstore_path = f'vectorstores/latest'
        os.makedirs(vectorstore_path, exist_ok=True)
        vectorstore, chunks = mylang4.document_processor.process_uploaded_document(local_pdf_path, persist_directory=vectorstore_path)

        

        return jsonify({'success': True})
    except Exception as e:
        logging.info(f"Error in analyse_note: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logging.info(f"🚀 Server starting on http://localhost:{port}")
    logging.info(f"📁 Serving static files from: {os.path.abspath(app.static_folder)}")
    app.run(
        host='0.0.0.0',
        port=port,
        debug=True
    )


'''
taskl
1.generate pdf with and without answer
2.Working on improvement of question quality
3.To understand the malang4 file
4.good text look of chatgpt see
5.additional info in question paper optional also
'''