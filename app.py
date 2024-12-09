import os
from flask import Flask, json, jsonify, render_template, request

import DAL
import utils

app = Flask(__name__)

# Endpoint for Frontend app
@app.route('/', methods=['GET', 'POST'])
def home():
    try:
        search_query = None  
        image_urls = []
        
        # Query the database with user's entry and return related images
        if request.method == 'POST':
            search_query = request.form.get('search', '')
            if search_query: 
                image_urls = DAL.query_db_text(search_query)
        
        return render_template('index.html', search_query=search_query, image_urls=image_urls)
    except Exception as e:
        return 'An error occurred while loading the page.', 500

# Upload pictures to DB 
# body: url = array of urls
@app.route('/upload', methods=['POST'])
def upload():
    try:
        urls = request.get_json().get('urls', [])
        if not urls:
            return jsonify({'success': False, 'error': 'No URLs provided.'}), 400

        image_path = "image.tmp"
        for url in urls:
            if not DAL.does_url_exist(url):
                utils.download_image(url, image_path)
                embeded_image = utils.generate_embedding(image_path)
                DAL.insert_data(embeded_image, url)

        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': 'Internal server error.'}), 500
    

# Endpoint to directly query for images based on input text
@app.route('/query', methods=['POST'])
def query():
    try:
        text = request.get_json().get('text', '')
        if not text:
            raise ValueError("The 'text' field is required.")
        
        urls = DAL.query_db_text(text)
        response = {'success': True, 'urls': urls}
        status_code = 200
    except ValueError as ve:
        response = {'success': False, 'error': str(ve)}
        status_code = 400
    except Exception as e:
        response = {'success': False, 'error': 'An unexpected error occurred.'}
        status_code = 500
    
    return json.dumps(response), status_code, {'ContentType': 'application/json'}

if __name__ == '__main__':
    app.run(debug=True)


