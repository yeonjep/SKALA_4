const form = document.querySelector('#postForm');
const message = document.querySelector('#message');

form.addEventListener('submit', async event => {
    event.preventDefault();

    const response = await fetch('/api/posts', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        credentials: 'include',
        body: JSON.stringify({
            title: document.querySelector('#title').value,
            content: document.querySelector('#content').value
        })
    });

    if (response.status === 401) {
        location.href = '/login.html';
        return;
    }

    if (response.ok) {
        const post = await response.json();
        location.href = `/post-detail.html?id=${post.id}`;
        return;
    }

    const body = await response.json().catch(() => ({
        message: '게시글 저장에 실패했습니다.'
    }));

    message.textContent = body.message;
});
