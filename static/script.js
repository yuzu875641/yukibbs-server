const API_URL = window.location.origin;

document.addEventListener('DOMContentLoaded', () => {
    fetchPosts();
    loadAuthorAndAccountIdFromCookie(); // 👈 Cookieから名前とaccountIDを読み込む

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
                <span class="account-id">ID: ${escapeHtml(post.account_id)}</span>
                <span>投稿日時: ${new Date(post.timestamp).toLocaleString()}</span>
            </div>
            <div class="post-content">${escapeHtml(post.message)}</div>
        `;
        container.appendChild(postElement);
    });
}

async function postMessage() {
    const authorInput = document.getElementById('author-input');
    const messageInput = document.getElementById('message-input');
    const author = authorInput.value;
    const message = messageInput.value;
    const accountId = getCookie('accountId'); // 👈 CookieからaccountIDを取得

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
            body: JSON.stringify({ author, message, account_id: accountId }) // 👈 accountIDを送信
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || '投稿に失敗しました');
        }

        const newPost = await response.json();
        saveAuthorAndAccountIdToCookie(newPost.author, newPost.account_id); // 👈 新しいIDを保存

        messageInput.value = '';
        fetchPosts();

    } catch (error) {
        console.error('エラー:', error);
        alert('投稿中にエラーが発生しました。\n' + error.message);
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

/**
 * 新しい関数: 名前とaccountIDをCookieに保存する
 */
function saveAuthorAndAccountIdToCookie(author, accountId) {
    document.cookie = `author=${encodeURIComponent(author)}; max-age=${60 * 60 * 24 * 365}; path=/`;
    document.cookie = `accountId=${encodeURIComponent(accountId)}; max-age=${60 * 60 * 24 * 365}; path=/`;
}

/**
 * 新しい関数: Cookieから名前とaccountIDを読み込む
 */
function loadAuthorAndAccountIdFromCookie() {
    const authorInput = document.getElementById('author-input');
    const author = getCookie('author');
    const accountId = getCookie('accountId');

    if (author && accountId) {
        authorInput.value = author;
        authorInput.disabled = true; // 👈 なりすまし防止のため、名前の変更を無効化
    }
}

/**
 * ヘルパー関数: Cookieから特定のキーの値を取得する
 */
function getCookie(name) {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
        let cookie = cookies[i].trim();
        if (cookie.startsWith(name + '=')) {
            return decodeURIComponent(cookie.substring(name.length + 1));
        }
    }
    return null;
}
