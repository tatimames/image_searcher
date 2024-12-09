import os
from flask import Flask, json, jsonify, render_template, request

import DAL
import utils

app = Flask(__name__)

#Enpoint for Frontend app
@app.route('/', methods=['GET', 'POST'])
def home():
    search_query = None  
    image_urls = []
    
    # Query the database with user's entry and return related images
    if request.method == 'POST':
        search_query = request.form['search']
        image_urls = DAL.query_db_text(search_query) 
        
    return render_template('index.html', search_query=search_query, image_urls=image_urls)

# Upload pictures to DB 
# body: url = array of urls
@app.route('/upload', methods=['POST'])
def upload():
    try:
        urls = request.get_json()['urls']
        image_path = "image.tmp"
        for url in urls:
            if not DAL.does_url_exist(url):
                utils.download_image(url, image_path)
                embeded_image = utils.generate_embedding(image_path)
                DAL.insert_data(embeded_image, url)
        return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
    except Exception as e:
        return jsonify({'success': False, 'error': 'Internal server error.'}), 500



# Endpoint to directly query for images based on input text
@app.route('/query', methods = ['POST'])
def query():
    text = request.get_json()['text']
    return json.dumps({'success':True, 'urls': DAL.query_db_text(text) }), 200, {'ContentType':'application/json'} 

if __name__ == '__main__':
    app.run(debug=True)


