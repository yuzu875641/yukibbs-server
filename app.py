from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime
import threading

app = Flask(__name__, static_folder='static')
CORS(app)

# インメモリデータベースとして使用する辞書とリスト
posts_by_id = {}
post_order = []
data_lock = threading.Lock()

@app.route('/')
def serve_index():
    return send_from_directory('static', 'index.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/posts', methods=['GET'])
def get_posts():
    with data_lock:
        posts_list = [posts_by_id[post_id] for post_id in post_order]
    return jsonify(posts_list)

@app.route('/posts', methods=['POST'])
def create_post():
    data = request.json
    if not data or 'author' not in data or 'message' not in data:
        return jsonify({'error': 'Invalid data'}), 400

    with data_lock:
        new_post_id = len(posts_by_id) + 1
        new_post = {
            'id': new_post_id,
            'author': data['author'],
            'message': data['message'],
            'timestamp': datetime.now().isoformat()
        }
        posts_by_id[new_post_id] = new_post
        post_order.append(new_post_id)

    return jsonify(new_post), 201

if __name__ == '__main__':
    app.run(debug=True)
