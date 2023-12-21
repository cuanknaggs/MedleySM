// auth
let jwt;
let loggedIn = false;
let currentUser;
const createPostButton = document.querySelector("#createPostButton");

setCookie = (cname, cvalue, exdays, unset = false) => {
    const d = new Date();
    if (unset) {
        d.setTime(d.getTime() + (-exdays * 24 * 60 * 60 * 1000));
    } else {
        d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000));
    }
    let expires = "expires="+d.toUTCString();
    document.cookie = `${cname}=${cvalue};${expires};path=${document.baseURI};secure=httpOnly;sameSite=strict`;
}

isLoggedIn = () => {
    const cookieValue = document.cookie
        .split("; ")
        .find((row) => row.startsWith("medleysm="))
        ?.split("=")[1];
    jwt = cookieValue;

    const options = {
        method: 'GET',
        headers: {
            Authorization: `Bearer ${cookieValue}`
        }
    };
    fetch('http://127.0.0.1:8000/api/users/me/', options)
        .then(response => response.json())
        .then((response) => {
            if (response.status == 'ok') {
                loggedIn = true;
                currentUser = response;
                document.querySelector('#loginButton').innerHTML = 'logout';
                createPostButton.removeAttribute('disabled');
                getPosts().then((data) => {
                    const postsList = document.querySelector('#postsList');
                    removeAllChildNodes(postsList);

                    data.map((post) => {
                        makePost(post, postsList, postTemplate);
                    })
                })
            }
        })
        .catch(err => console.error(err));
}
isLoggedIn();

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

const loginDialog = document.querySelector("#loginDialog");
document.querySelector("#loginButton").addEventListener("click", () => {
    if (loggedIn) {
        jwt = null;
        loggedIn = false;
        setCookie('medleysm', '', 0, true);
        document.querySelector('#loginButton').innerHTML = 'login';
    } else {
        loginDialog.showModal();
    }
});
document.querySelector("#cancelLogin").addEventListener("click", (event) => {
    event.preventDefault();
    loginDialog.close();
});

loginDialog.addEventListener("close", (e) => {
    console.log(loginDialog);
});

// createPostDialog
const createPostDialog = document.querySelector("#createPostDialog");
createPostButton.addEventListener("click", () => {
    createPostDialog.showModal();
});
document.querySelector("#cancelCreatePost").addEventListener("click", (event) => {
    event.preventDefault();
    cleanPostDialog(createPostDialog);
    createPostDialog.close();
});
