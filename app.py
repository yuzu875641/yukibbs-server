import os
import json
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from redis import Redis
from rq import Queue
from websockets.sync.client import connect as ws_connect

# インメモリデータストア
posts_in_memory = []
next_post_id = 1

# RedisとRQキューの設定
redis_conn = Redis(host=os.environ.get('REDIS_HOST', 'localhost'), port=6379)
q = Queue(connection=redis_conn)

# Flaskアプリケーションの設定
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

def process_post_task(post_data):
    """RQワーカーが実行するタスク：投稿データを永続化（今回は省略）"""
    print(f"非同期で投稿を処理中: {post_data}")
    # 実際にはここにRDBへの書き込み処理が入る
    
    # WebSocketサーバーに通知
    try:
        ws_host = os.environ.get('WEBSOCKET_HOST', 'localhost')
        with ws_connect(f"ws://{ws_host}:8765") as websocket:
            websocket.send(json.dumps({"type": "new_post", "data": post_data}))
    except Exception as e:
        print(f"WebSocketサーバーへの接続失敗: {e}")

@app.route("/api/posts", methods=["GET"])
def get_posts():
    """全投稿を返す"""
    return jsonify(posts_in_memory)

@app.route("/api/posts", methods=["POST"])
def post_message():
    """新しい投稿を受け付け、インメモリに追加し、キューに入れる"""
    global next_post_id
    data = request.json
    author = data.get("author")
    content = data.get("content")
    
    if not author or not content:
        return jsonify({"error": "Author and content are required"}), 400

    # タイムスタンプを正確に取得
    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # インメモリに追加
    new_post = {
        "id": next_post_id,
        "author": author,
        "timestamp": timestamp_str,
        "content": content
    }
    posts_in_memory.append(new_post)
    next_post_id += 1
    
    # 投稿処理をキューに追加
    q.enqueue(process_post_task, new_post)
    
    return jsonify(new_post), 201

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
