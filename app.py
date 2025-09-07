from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from datetime import datetime
import threading

app = Flask(__name__)
CORS(app)

posts_by_id = {}
post_order = []
data_lock = threading.Lock()

@app.route('/')
def serve_index():
    with data_lock:
        posts_list = [posts_by_id[post_id] for post_id in post_order]
    
    # 古い投稿を下に表示するため、逆順にする
    sorted_posts = sorted(posts_list, key=lambda p: p['timestamp'])
    
    return render_template('index.html', posts=sorted_posts)

@app.route('/static/<path:filename>')
def serve_static(filename):
    return app.send_static_file(filename)

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

    # SSRの場合、投稿後はリダイレクトで再描画する
    return jsonify({'redirect': '/'}), 201

if __name__ == '__main__':
    app.run(debug=True)
