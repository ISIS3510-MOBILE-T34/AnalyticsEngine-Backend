# app.py

from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)

# Initialize Firebase
cred_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 'serviceAccountKey.json')
cred = credentials.Certificate(cred_path)

firebase_admin.initialize_app(cred)

db = firestore.client()

# Collection name - OFFERS
COLLECTION_NAME = 'offers'

@app.route('/documents', methods=['POST'])
def create_document():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Add a new document with auto-generated ID
        doc_ref = db.collection(COLLECTION_NAME).add(data)
        return jsonify({'id': doc_ref[1].id, 'data': data}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    
@app.route('/documents/<doc_id>', methods=['GET'])
def get_document(doc_id):
    try:
        doc_ref = db.collection(COLLECTION_NAME).document(doc_id)
        doc = doc_ref.get()
        if doc.exists:
            return jsonify({'id': doc.id, 'data': doc.to_dict()}), 200
        else:
            return jsonify({'error': 'Document not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/documents/<doc_id>', methods=['PUT'])
def update_document(doc_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        doc_ref = db.collection(COLLECTION_NAME).document(doc_id)
        doc = doc_ref.get()
        if doc.exists:
            doc_ref.update(data)
            return jsonify({'id': doc.id, 'data': data}), 200
        else:
            return jsonify({'error': 'Document not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/documents/<doc_id>', methods=['DELETE'])
def delete_document(doc_id):
    try:
        doc_ref = db.collection(COLLECTION_NAME).document(doc_id)
        doc = doc_ref.get()
        if doc.exists:
            doc_ref.delete()
            return jsonify({'message': 'Document deleted successfully'}), 200
        else:
            return jsonify({'error': 'Document not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)

