const API_URL = window.location.origin;

document.addEventListener('DOMContentLoaded', () => {
    fetchPosts();

    document.getElementById('post-button').addEventListener('click', postMessage);
});

async function fetchPosts() {
    try {
        const response = await fetch(`${API_URL}/posts`);
        if (!response.ok) {
            throw new Error('投稿の取得に失敗しました');
        }
        const posts = await response.json();
        renderPosts(posts);
    } catch (error) {
        console.error('エラー:', error);
        alert('投稿の読み込み中にエラーが発生しました。');
    }
}

function renderPosts(posts) {
    const container = document.getElementById('posts-container');
    container.innerHTML = '';
    
    if (posts.length === 0) {
        container.innerHTML += '<p>まだ投稿はありません。</p>';
        return;
    }

    posts.slice().reverse().forEach(post => {
        const postElement = document.createElement('div');
        postElement.classList.add('post');
        postElement.innerHTML = `
            <div class="post-meta">
                <span>名前: ${escapeHtml(post.author)}</span>
                <span>投稿日時: ${new Date(post.timestamp).toLocaleString()}</span>
            </div>
            <div class="post-content">${escapeHtml(post.message)}</div>
        `;
        container.appendChild(postElement);
    });
}

async function postMessage() {
    const author = document.getElementById('author-input').value;
    const message = document.getElementById('message-input').value;

    if (!author || !message) {
        alert('名前とメッセージ内容を入力してください。');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/posts`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ author, message })
        });

        if (!response.ok) {
            throw new Error('投稿に失敗しました');
        }

        document.getElementById('author-input').value = '';
        document.getElementById('message-input').value = '';
        fetchPosts();

    } catch (error) {
        console.error('エラー:', error);
        alert('投稿中にエラーが発生しました。');
    }
}

function escapeHtml(text) {
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
