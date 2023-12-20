// auth
let jwt;
let loggedIn = false;

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
        // .then(response => response.json())
        .then((response) => {
            if (response.status == 200) {
                loggedIn = true;
                document.querySelector('#loginButton').innerHTML = 'logout';
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
document.querySelector("#createPostButton").addEventListener("click", () => {
    createPostDialog.showModal();
});
document.querySelector("#cancelCreatePost").addEventListener("click", (event) => {
    event.preventDefault();
    createPostDialog.close();
});

createPost = async (event) => {
    event.preventDefault();
    const body = {
        "content": createPostForm.newPost.value,
        "parent_post": -1
    }
    try {
        const response = await fetch(event.target.action, {
            method: "POST",
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${jwt}`
            },
            body: JSON.stringify(body),
        });
        const data = await response.json();
        switch(response.status) {
            case 201:
                getPosts().then((data) => {
                    data.map((post) => {
                        const postContent = document.createElement('li');
                        const postContentWrapper = document.createElement('div');
                        const title = document.createElement('h3');
                        const content = document.createElement('p');
                        const likeCount = document.createElement('span');
                        const like = document.createElement('button');
                        const fackCheck = document.createElement('p');

                        title.innerHTML = post.user_name;
                        content.innerHTML = post.content;
                        like.innerHTML = 'Like';
                        like.setAttribute('id', `like_${post.id}`)
                        if (post.like !== null) {
                            likeCount.innerHTML = post.likes;
                            like.appendChild(likeCount)
                        }

                        postContentWrapper.appendChild(title);
                        postContentWrapper.appendChild(content);
                        postContentWrapper.appendChild(like);
                        if (post.fack_check) {
                            fackCheck.innerHTML = post.fact_check;
                            postContentWrapper.appendChild(fackCheck);
                        }
                        postContent.appendChild(postContentWrapper);
                        postsList.appendChild(postContent);
                    })
                })
                createPostDialog.close();
                break;
            default:
                if (typeof data.detail == 'string') {
                    document.querySelector('#createPostMessage').innerHTML = data.detail;
                } else {
                    document.querySelector('#createPostMessage').innerHTML = response.statusText;
                }
        }
    } catch (e) {
        console.error(e);
    }
}
const createPostForm = document.querySelector('#createPost');
createPostForm.addEventListener('submit', createPost)

