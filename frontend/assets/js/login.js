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
                setCookie('medleysm', data.access_token, 1);

                jwt = data.access_token;
                loginDialog.close();
                isLoggedIn();
                break;
            default:
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
