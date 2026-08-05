const params = new URLSearchParams(location.search);
const postId = params.get('id');

const postTitle = document.querySelector('#postTitle');
const postMeta = document.querySelector('#postMeta');
const postContent = document.querySelector('#postContent');
const likeButton = document.querySelector('#likeButton');
const likeCount = document.querySelector('#likeCount');
const deletePostButton = document.querySelector('#deletePostButton');
const commentList = document.querySelector('#commentList');
const commentCount = document.querySelector('#commentCount');
const currentUser = document.querySelector('#currentUser');

let username = '';
let liked = false;
let post = null;

function escapeHtml(value) {
    const div = document.createElement('div');
    div.textContent = value ?? '';
    return div.innerHTML;
}

function formatDate(value) {
    return new Intl.DateTimeFormat('ko-KR', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    }).format(new Date(value));
}

async function checkAuthentication() {
    const response = await fetch('/api/auth/check', {
        credentials: 'include'
    });

    if (!response.ok) {
        location.href = '/login.html';
        return false;
    }

    const body = await response.json();
    username = body.username;
    currentUser.textContent = `${username}님으로 로그인했습니다.`;
    return true;
}

async function loadPost() {
    const response = await fetch(`/api/posts/${postId}`, {
        credentials: 'include'
    });

    if (!response.ok) {
        postTitle.textContent = '게시글을 찾을 수 없습니다.';
        return;
    }

    post = await response.json();

    postTitle.textContent = post.title;
    postMeta.textContent =
        `${post.writer} · ${formatDate(post.createdAt)} · 조회 ${post.viewCount}`;
    postContent.textContent = post.content;
    likeCount.textContent = post.likeCount;

    deletePostButton.classList.toggle(
        'hidden',
        post.writer !== username
    );
}

async function loadLikeStatus() {
    const response = await fetch(`/api/posts/${postId}/likes`, {
        credentials: 'include'
    });

    if (!response.ok) {
        return;
    }

    const body = await response.json();
    liked = body.liked;
    likeCount.textContent = body.likeCount;
    likeButton.classList.toggle('liked', liked);
}

async function loadComments() {
    const response = await fetch(`/api/posts/${postId}/comments`, {
        credentials: 'include'
    });

    if (!response.ok) {
        return;
    }

    const comments = await response.json();
    commentCount.textContent = comments.length;

    if (comments.length === 0) {
        commentList.innerHTML =
            '<div class="comment-item">등록된 댓글이 없습니다.</div>';
        return;
    }

    commentList.innerHTML = comments.map(comment => `
        <article class="comment-item">
            <div class="comment-head">
                <span class="comment-writer">${escapeHtml(comment.writer)}</span>
                <span class="comment-date">${formatDate(comment.createdAt)}</span>
            </div>
            <p class="comment-content">${escapeHtml(comment.content)}</p>
            ${comment.writer === username ? `
                <div class="comment-actions">
                    <button type="button"
                            data-comment-id="${comment.id}">
                        삭제
                    </button>
                </div>
            ` : ''}
        </article>
    `).join('');

    commentList
        .querySelectorAll('[data-comment-id]')
        .forEach(button => {
            button.addEventListener('click', async () => {
                await deleteComment(button.dataset.commentId);
            });
        });
}

async function deleteComment(commentId) {
    const response = await fetch(
        `/api/posts/${postId}/comments/${commentId}`,
        {
            method: 'DELETE',
            credentials: 'include'
        }
    );

    if (response.ok) {
        await loadComments();
    }
}

likeButton.addEventListener('click', async () => {
    const response = await fetch(
        `/api/posts/${postId}/likes`,
        {
            method: liked ? 'DELETE' : 'POST',
            credentials: 'include'
        }
    );

    if (!response.ok) {
        return;
    }

    const body = await response.json();
    liked = body.liked;
    likeCount.textContent = body.likeCount;
    likeButton.classList.toggle('liked', liked);
});

document.querySelector('#commentForm')
    .addEventListener('submit', async event => {
        event.preventDefault();

        const content = document.querySelector('#commentContent');

        const response = await fetch(
            `/api/posts/${postId}/comments`,
            {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                credentials: 'include',
                body: JSON.stringify({content: content.value})
            }
        );

        if (response.ok) {
            content.value = '';
            await loadComments();
        }
    });

deletePostButton.addEventListener('click', async () => {
    if (!confirm('게시글을 삭제하시겠습니까?')) {
        return;
    }

    const response = await fetch(`/api/posts/${postId}`, {
        method: 'DELETE',
        credentials: 'include'
    });

    if (response.ok) {
        location.href = '/board.html';
    }
});

document.querySelector('#logout')
    .addEventListener('click', async () => {
        await fetch('/api/auth/logout', {
            method: 'POST',
            credentials: 'include'
        });

        location.href = '/login.html';
    });

(async () => {
    if (!postId) {
        location.href = '/board.html';
        return;
    }

    if (await checkAuthentication()) {
        await Promise.all([
            loadPost(),
            loadLikeStatus(),
            loadComments()
        ]);
    }
})();
