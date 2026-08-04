const form = document.querySelector('#postForm');
const titleInput = document.querySelector('#title');
const contentInput = document.querySelector('#content');
const message = document.querySelector('#message');
const formTitle = document.querySelector('#formTitle');
const postId = new URLSearchParams(location.search).get('id');

async function request(url, options = {}) {
    const response = await fetch(url, {
        credentials: 'include',
        ...options
    });

    if (response.status === 401 || response.status === 403) {
        const body = await response.json().catch(() => null);
        if (response.status === 401) location.href = '/login';
        else message.textContent = body?.message ?? '권한이 없습니다.';
    }

    return response;
}

async function loadPost() {
    if (!postId) return;

    formTitle.textContent = '게시글 수정';
    const response = await request(`/api/posts/${postId}`);
    if (!response.ok) return;

    const post = await response.json();
    titleInput.value = post.title;
    contentInput.value = post.content;
}

form.addEventListener('submit', async event => {
    event.preventDefault();

    const payload = JSON.stringify({
        title: titleInput.value.trim(),
        content: contentInput.value.trim()
    });

    const response = await request(
        postId ? `/api/posts/${postId}` : '/api/posts',
        {
            method: postId ? 'PUT' : 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: payload
        }
    );

    if (response.ok) {
        location.href = '/board.html';
        return;
    }

    const body = await response.json().catch(() => ({ message: '저장에 실패했습니다.' }));
    message.textContent = body.message;
});

loadPost();
