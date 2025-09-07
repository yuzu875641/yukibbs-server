from flask import Flask, request, jsonify
from datetime import datetime
import threading

app = Flask(__name__)

# インメモリデータベースとして使用する辞書とリスト
# posts_by_id: 投稿IDをキーとした辞書 (検索用)
# post_order: 投稿IDを格納するリスト (順序維持用)
posts_by_id = {}
post_order = []

# スレッドロック
# 複数のリクエストが同時にデータにアクセスするのを防ぎます
data_lock = threading.Lock()


# いらないと思う
@app.route('/', methods=['GET'])
def index():
    return "掲示板サーバーが起動中です！投稿一覧は /posts にアクセスしてください。"
    
@app.route('/posts', methods=['GET'])
def get_posts():
    """
    全投稿を取得するAPI
    投稿順序を維持しつつ、辞書からデータを取得
    """
    with data_lock:
        # post_orderリストの順序で投稿を取得し、辞書に変換して返す
        posts_list = [posts_by_id[post_id] for post_id in post_order]
    return jsonify(posts_list)

@app.route('/posts', methods=['POST'])
def create_post():
    """
    新しい投稿を作成するAPI
    """
    data = request.json
    if not data or 'author' not in data or 'message' not in data:
        return jsonify({'error': 'Invalid data'}), 400

    with data_lock:
        # スレッドロックで保護されたセクション
        new_post_id = len(posts_by_id) + 1
        new_post = {
            'id': new_post_id,
            'author': data['author'],
            'message': data['message'],
            'timestamp': datetime.now().isoformat()
        }
        
        # 投稿データを辞書とリストの両方に追加
        posts_by_id[new_post_id] = new_post
        post_order.append(new_post_id)

    return jsonify(new_post), 201

if __name__ == '__main__':
    app.run(debug=True)
