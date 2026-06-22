from flask import Flask, request, jsonify, send_from_directory
from pathlib import Path
import os

HERE = Path(__file__).parent
app = Flask(__name__, static_folder=str(HERE / 'static'))

# import parser from same folder
from parser import parse_input

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
    return response

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/parse', methods=['POST'])
def api_parse():
    data = request.get_json(force=True)
    text = data.get('text', '')
    result = parse_input(text)
    return jsonify(result)

@app.route('/api/agent/parse', methods=['POST'])
def api_agent_parse():
    data = request.get_json(force=True)
    text = data.get('text', '')
    result = parse_input(text)
    parsed = {
        'recipient_type': result.get('recipient'),
        'recipient_age_range': result.get('age_range'),
        'genres': result.get('genres', []),
        'avoid': result.get('avoid', []),
        'surprise_level': result.get('surprise_level'),
        'raw_input': result.get('raw', text)
    }
    return jsonify({
        'parsed': parsed,
        'follow_up_question': None,
        'suggestions': []
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='127.0.0.1', port=port, debug=False)
