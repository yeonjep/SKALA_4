const postList = document.querySelector('#postList');
const pagination = document.querySelector('#pagination');
const currentUser = document.querySelector('#currentUser');

let currentPage = 0;
let currentUsername = '';

async function checkAuthentication() {
    const response = await fetch('/api/auth/check', {
        credentials: 'include'
    });

    if (!response.ok) {
        location.href = '/login.html';
        return false;
    }

    const body = await response.json();
    currentUsername = body.username;
    currentUser.textContent = `${body.username}님으로 로그인했습니다.`;
    return true;
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

async function loadPosts(page = 0) {
    currentPage = page;

    const params = new URLSearchParams({
        page: String(page),
        size: '10',
        searchType: document.querySelector('#searchType').value,
        sort: document.querySelector('#sort').value
    });

    const keyword = document.querySelector('#keyword').value.trim();
    if (keyword) {
        params.set('keyword', keyword);
    }

    const response = await fetch(`/api/posts?${params}`, {
        credentials: 'include'
    });

    if (!response.ok) {
        postList.innerHTML =
            '<tr><td colspan="7" class="empty-row">목록을 불러오지 못했습니다.</td></tr>';
        return;
    }

    const pageData = await response.json();
    renderPosts(pageData.content);
    renderPagination(pageData);
}

function renderPosts(posts) {
    if (posts.length === 0) {
        postList.innerHTML =
            '<tr><td colspan="7" class="empty-row">등록된 게시글이 없습니다.</td></tr>';
        return;
    }

    postList.innerHTML = posts.map(post => `
        <tr>
            <td>${post.id}</td>
            <td>
                <a class="title-link"
                   href="/post-detail.html?id=${post.id}">
                    ${escapeHtml(post.title)}
                </a>
            </td>
            <td>${escapeHtml(post.writer)}</td>
            <td>${post.viewCount}</td>
            <td>${post.likeCount}</td>
            <td>${post.commentCount}</td>
            <td>${formatDate(post.createdAt)}</td>
        </tr>
    `).join('');
}

function renderPagination(pageData) {
    pagination.innerHTML = '';

    for (let index = 0; index < pageData.totalPages; index++) {
        const button = document.createElement('button');
        button.type = 'button';
        button.textContent = String(index + 1);
        button.classList.toggle('active', index === pageData.page);
        button.addEventListener('click', () => loadPosts(index));
        pagination.appendChild(button);
    }
}

function escapeHtml(value) {
    const div = document.createElement('div');
    div.textContent = value ?? '';
    return div.innerHTML;
}

document.querySelector('#searchButton')
    .addEventListener('click', () => loadPosts(0));

document.querySelector('#keyword')
    .addEventListener('keydown', event => {
        if (event.key === 'Enter') {
            loadPosts(0);
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
    if (await checkAuthentication()) {
        await loadPosts();
    }
})();
