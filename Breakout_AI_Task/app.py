from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import io
import pandas as pd
from typing import Dict, Any
import logging
from main import AllInOne
import nltk

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Download required NLTK data
try:
    nltk.download("punkt")
    nltk.download("averaged_perceptron_tagger")
    nltk.download("stopwords")
except Exception as e:
    logging.error(f"Error downloading NLTK data: {str(e)}")

app = Flask(__name__)

# Configure CORS
CORS(app, resources={
    r"/health": {
        "origins": ["*"],  # Allow all origins for health check
        "methods": ["GET"]  # Only allow GET method
    },
    r"/process": {
        "origins": ["http://localhost:5173"],  # Replace with your frontend domains
        "methods": ["POST"],
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Content-Disposition"],
        "supports_credentials": True  # Enable if you need to send cookies
    }
})

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}

# Ensure required directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename: str) -> bool:
    """Check if the uploaded file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/health', methods=['GET'])
def health_check() -> Dict[str, str]:
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})

@app.route('/sheets-headers', methods=['POST'])
def get_sheets_headers() -> Any:
    """Get sheet headers"""
    sheet_url = request.form.get('sheet_url')
    sheet_id = sheet_url.split('/')[5]
    
    # Convert the Google Sheet URL to CSV export URL
    csv_url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv'
    try:
        df = pd.read_csv(csv_url)
        
        headers = df.columns.tolist()
        print(df)
        print(headers)
        response = jsonify({'headers': headers})
        response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response
    except Exception as e:
        logging.error(f"Error reading CSV headers: {str(e)}")
        return jsonify({'error': f'Failed to read CSV file: {str(e)}'}), 400

@app.route('/process', methods=['POST'])
def process_data() -> Any:
    """
    Process CSV data and return results as a file response
    
    Expected form data:
    - file: CSV file
    - column: Column name containing company names
    - question: Question to be answered
    - max_workers (optional): Maximum number of parallel workers
    """
    try:
        # Handle preflight requests
        if request.method == 'OPTIONS':
            response = app.make_default_options_response()
            return response

        # Get the data either from file upload or Google Sheets
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
                
            if not allowed_file(file.filename):
                return jsonify({'error': 'Invalid file type. Only CSV files are allowed'}), 400
                
            # Save uploaded file
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            
        elif 'sheetsUrl' in request.form:
            # Handle Google Sheets URL
            sheet_url = request.form.get('sheetsUrl')
            sheet_id = sheet_url.split('/')[5]
            csv_url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv'
            
            # Download and save the CSV
            df = pd.read_csv(csv_url)
            filename = 'sheet_data.csv'
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            df.to_csv(filepath, index=False)
            
        else:
            return jsonify({'error': 'No file or sheet URL provided'}), 400
            
        column = request.form.get('column')
        if not column:
            return jsonify({'error': 'Column name not provided'}), 400
            
        question = request.form.get('question')
        if not question:
            return jsonify({'error': 'Question not provided'}), 400
            
        max_workers = int(request.form.get('max_workers', 3))
        
        logging.info(f"Processing file: {filename}")
        
        # Process the data
        processor = AllInOne(
            csv_path=filepath,
            column=column,
            question=question,
            max_workers=max_workers
        )
        
        # Execute processing
        processor()
        
        # Convert results to CSV in-memory
        output_df = processor.get_results_as_dataframe()  # Assumes processor has a method to return a DataFrame
        # output_df = pd.DataFrame({'Company Name': ['Company A', 'Company B'], 'Result': ['Result A', 'Result B']})
        # output_buffer = io.StringIO()
        csv_string = output_df.to_csv(index=False) 
        print(csv_string)
        # output_df.to_csv(output_buffer, index=False)
        # output_buffer.seek(0)
        
        # Clean up uploaded file
        os.remove(filepath)
        
        response = jsonify({'success':True,"data" : csv_string})
        
        # Add CORS headers to the response
        response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response
        
    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        # Clean up uploaded file if it exists
        if 'filepath' in locals() and os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5001)