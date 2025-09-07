import string
import random
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime
import threading

app = Flask(__name__, static_folder='static')
CORS(app)

posts_by_id = {}
post_order = []
authors_to_ids = {} # 👈 ユーザー名とaccountIDの紐付けを保存
data_lock = threading.Lock()

def generate_unique_id(length=8):
    """一意のランダムな英数字IDを生成する"""
    characters = string.ascii_letters + string.digits
    while True:
        # ランダムなIDを生成
        new_id = ''.join(random.choice(characters) for _ in range(length))
        # 既存のIDと重複しないかチェック
        if new_id not in authors_to_ids.values():
            return new_id

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

    author = data['author']
    client_account_id = data.get('account_id') # クライアントから送信されたIDを取得

    with data_lock:
        # クライアントからaccountIDが送信されなかった場合、新しいIDを生成
        if not client_account_id:
            new_account_id = authors_to_ids.get(author)
            if not new_account_id:
                new_account_id = generate_unique_id()
                authors_to_ids[author] = new_account_id
        # クライアントからIDが送信された場合、既存のIDと一致するか確認
        else:
            if authors_to_ids.get(author) != client_account_id:
                return jsonify({'error': 'Unauthorized: account ID does not match author'}), 401
            new_account_id = client_account_id
        
        new_post_id = len(posts_by_id) + 1
        new_post = {
            'id': new_post_id,
            'author': author,
            'account_id': new_account_id, # 👈 accountIDを追加
            'message': data['message'],
            'timestamp': datetime.now().isoformat()
        }
        posts_by_id[new_post_id] = new_post
        post_order.append(new_post_id)

    return jsonify(new_post), 201

if __name__ == '__main__':
    app.run(debug=True)
