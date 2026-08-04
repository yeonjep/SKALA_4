const postList = document.querySelector('#postList');
const message = document.querySelector('#message');
const currentUser = document.querySelector('#currentUser');
const logoutButton = document.querySelector('#logout');

let username = '';

async function request(url, options = {}) {
    const response = await fetch(url, {
        credentials: 'include',
        ...options
    });

    if (response.status === 401 || response.status === 403) {
        location.href = '/login';
        throw new Error('인증이 필요합니다.');
    }

    return response;
}

function formatDate(value) {
    return new Intl.DateTimeFormat('ko-KR', {
        year: 'numeric', month: '2-digit', day: '2-digit',
        hour: '2-digit', minute: '2-digit'
    }).format(new Date(value));
}

function renderPosts(posts) {
    if (posts.length === 0) {
        postList.innerHTML = '<tr><td colspan="4" class="empty-row">등록된 게시글이 없습니다.</td></tr>';
        return;
    }

    postList.innerHTML = posts.map(post => `
        <tr>
            <td>${post.id}</td>
            <td>
                <button class="title-button" data-id="${post.id}">${escapeHtml(post.title)}</button>
                <div class="post-detail" id="detail-${post.id}" hidden></div>
            </td>
            <td>${escapeHtml(post.writer)}</td>
            <td>${formatDate(post.createdAt)}</td>
        </tr>
    `).join('');

    document.querySelectorAll('.title-button').forEach(button => {
        button.addEventListener('click', () => showDetail(Number(button.dataset.id)));
    });
}

async function showDetail(postId) {
    const detail = document.querySelector(`#detail-${postId}`);
    if (!detail.hidden) {
        detail.hidden = true;
        return;
    }

    const response = await request(`/api/posts/${postId}`);
    if (!response.ok) {
        message.textContent = '게시글을 불러오지 못했습니다.';
        return;
    }

    const post = await response.json();
    const actions = post.writer === username
        ? `<div class="detail-actions">
             <a href="/post-form.html?id=${post.id}">수정</a>
             <button type="button" data-delete-id="${post.id}">삭제</button>
           </div>`
        : '';

    detail.innerHTML = `<p>${escapeHtml(post.content).replaceAll('\n', '<br>')}</p>${actions}`;
    detail.hidden = false;

    const deleteButton = detail.querySelector('[data-delete-id]');
    if (deleteButton) {
        deleteButton.addEventListener('click', () => deletePost(post.id));
    }
}

async function deletePost(postId) {
    if (!confirm('게시글을 삭제하시겠습니까?')) return;

    const response = await request(`/api/posts/${postId}`, { method: 'DELETE' });
    if (response.ok) {
        await loadPosts();
        return;
    }

    const body = await response.json().catch(() => ({ message: '삭제에 실패했습니다.' }));
    message.textContent = body.message;
}

async function loadPosts() {
    const response = await request('/api/posts');
    if (!response.ok) {
        message.textContent = '게시글 목록을 불러오지 못했습니다.';
        return;
    }
    renderPosts(await response.json());
}

async function initialize() {
    const authResponse = await request('/api/auth/check');
    const auth = await authResponse.json();
    username = auth.username;
    currentUser.textContent = `${username}님으로 로그인했습니다.`;
    await loadPosts();
}

logoutButton.addEventListener('click', async () => {
    await fetch('/api/auth/logout', { method: 'POST', credentials: 'include' });
    location.href = '/login';
});

function escapeHtml(value) {
    const element = document.createElement('div');
    element.textContent = value;
    return element.innerHTML;
}

initialize().catch(error => {
    message.textContent = error.message;
});
