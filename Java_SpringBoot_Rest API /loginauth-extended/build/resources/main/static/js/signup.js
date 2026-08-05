const form = document.querySelector('#signupForm');
const message = document.querySelector('#message');

form.addEventListener('submit', async event => {
    event.preventDefault();

    const response = await fetch('/api/auth/signup', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            username: document.querySelector('#username').value,
            password: document.querySelector('#password').value
        })
    });

    if (response.ok) {
        location.href = '/login.html';
        return;
    }

    const body = await response.json().catch(() => ({
        message: '회원가입에 실패했습니다.'
    }));

    message.textContent = body.message;
});
