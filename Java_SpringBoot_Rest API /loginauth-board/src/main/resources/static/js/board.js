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
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    }).format(new Date(value));
}

function renderPosts(posts) {
    if (posts.length === 0) {
        postList.innerHTML = `
            <tr>
                <td colspan="4" class="empty-row">
                    등록된 게시글이 없습니다.
                </td>
            </tr>
        `;
        return;
    }

    postList.innerHTML = posts.map(post => `
        <tr>
            <td>${post.id}</td>
            <td>
                <button
                    class="title-button"
                    data-id="${post.id}">
                    ${escapeHtml(post.title)}
                </button>

                <div
                    class="post-detail"
                    id="detail-${post.id}"
                    hidden>
                </div>
            </td>
            <td>${escapeHtml(post.writer)}</td>
            <td>${formatDate(post.createdAt)}</td>
        </tr>
    `).join('');

    document.querySelectorAll('.title-button').forEach(button => {
        button.addEventListener('click', () => {
            showDetail(Number(button.dataset.id));
        });
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
        ? `
            <div class="detail-actions">
                <a href="/post-form.html?id=${post.id}">
                    수정
                </a>

                <button
                    type="button"
                    data-delete-id="${post.id}">
                    삭제
                </button>
            </div>
        `
        : '';

    detail.innerHTML = `
        <p>
            ${escapeHtml(post.content).replaceAll('\n', '<br>')}
        </p>
        ${actions}
    `;

    detail.hidden = false;

    const deleteButton = detail.querySelector('[data-delete-id]');

    if (deleteButton) {
        deleteButton.addEventListener('click', () => {
            deletePost(post.id);
        });
    }
}

async function deletePost(postId) {
    if (!confirm('게시글을 삭제하시겠습니까?')) {
        return;
    }

    const response = await request(
        `/api/posts/${postId}`,
        {
            method: 'DELETE'
        }
    );

    if (response.ok) {
        message.textContent = '';
        await loadPosts();
        return;
    }

    const body = await response
        .json()
        .catch(() => ({
            message: '삭제에 실패했습니다.'
        }));

    message.textContent =
        body.message ?? '삭제에 실패했습니다.';
}

async function loadPosts() {
    const response = await request('/api/posts');

    if (!response.ok) {
        message.textContent =
            '게시글 목록을 불러오지 못했습니다.';
        return;
    }

    const posts = await response.json();

    message.textContent = '';
    renderPosts(posts);
}

async function initialize() {
    const authResponse =
        await request('/api/auth/check');

    if (!authResponse.ok) {
        throw new Error('인증 정보를 확인하지 못했습니다.');
    }

    const auth = await authResponse.json();

    username = auth.username;

    currentUser.textContent =
        `${username}님으로 로그인했습니다.`;

    await loadPosts();
}

if (logoutButton) {
    logoutButton.addEventListener('click', async () => {
        try {
            const response = await fetch(
                '/api/auth/logout',
                {
                    method: 'POST',
                    credentials: 'include'
                }
            );

            if (!response.ok) {
                const body = await response
                    .json()
                    .catch(() => null);

                throw new Error(
                    body?.message
                    ?? '로그아웃에 실패했습니다.'
                );
            }

            /*
             * fetch 요청은 리다이렉트 응답을 따라가더라도
             * 현재 브라우저 페이지를 자동으로 이동시키지는 않습니다.
             * 따라서 로그아웃 성공 후 직접 로그인 화면으로 이동합니다.
             */
            location.href = '/login';

        } catch (error) {
            message.textContent =
                error.message ?? '로그아웃에 실패했습니다.';
        }
    });
}

function escapeHtml(value) {
    const element = document.createElement('div');

    element.textContent =
        value == null ? '' : String(value);

    return element.innerHTML;
}

initialize().catch(error => {
    message.textContent =
        error.message ?? '초기화에 실패했습니다.';
});