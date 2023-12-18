const path = window.location.href.split('/');

const loginForm = document.querySelector('#login');
const login = async (event) => {
    event.preventDefault();
    const formData = new FormData(loginForm);

    try {
        const response = await fetch(event.target.action, {
            method: "POST",
            body: formData,
        });
        const data = await response.json();
        switch(response.status) {
            case 200:
                const cookie = `value=${data.access_token};secure=httpOnly;sameSite=strict`;
                document.cookie = cookie;
                path.pop();
                path.push('index.html');
                console.log(path.join('/'));
                window.location.href = path.join('/');
                break;
            default:
                console.log(data);
                if (typeof data.detail == 'string') {
                    document.querySelector('#message').innerHTML = data.detail;
                } else {
                    document.querySelector('#message').innerHTML = response.statusText;
                }
        }
    } catch (e) {
        console.error(e);
    }
}
loginForm.addEventListener('submit', login);
