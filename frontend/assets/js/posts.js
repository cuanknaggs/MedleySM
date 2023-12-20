removeAllChildNodes = (parent) => {
    while (parent.firstChild) {
        parent.removeChild(parent.firstChild);
    }
}

getPosts = async () => {
    const response = await fetch('http://127.0.0.1:8000/api/posts?start=0&limit=0');
    return await response.json();
}
getUserPosts = async (userName) => {
    const response = await fetch(`http://127.0.0.1:8000/api/posts/${userName}`);
    return await response.json();
}


likePost = async (postId) => {
    try {
        console.log('ping');
        const response = await fetch(`http://127.0.0.1:8000/api/post/like/${postId}`, {
            method: "PUT",
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${jwt}`
            }
        });
        const data = await response.json();
        console.log(data)
        switch(response.status) {
            case 201:
                break;
            default:
        }
    } catch (e) {
        console.error(e);
    }
}

makePost = (post) => {
    const postContent = document.createElement('li');
    const postContentWrapper = document.createElement('div');
    const title = document.createElement('h3');
    const userName = document.createElement('button');
    const content = document.createElement('p');
    const likeCount = document.createElement('span');
    const like = document.createElement('button');
    const fackCheck = document.createElement('p');

    userName.innerHTML = post.user_name;
    userName.setAttribute('data-user', post.user_name);
    userName.addEventListener('click', (event) => {
        makeUserPostsList(event.target.getAttribute('data-user'));
    })
    title.appendChild(userName);
    content.innerHTML = post.content;
    like.innerHTML = 'Like';
    like.setAttribute('data-id', post.id);
    like.addEventListener('click', (event) => {
        likePost(event.target.getAttribute('data-id'));
    })
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
}

makeUserPostsList = (userName) => {
    const postsList = document.querySelector('#postsList');

    removeAllChildNodes(postsList);

    getUserPosts(event.target.getAttribute('data-user')).then((data) => {
        console.log(data)
        data.map((post) => {
            makePost(post);
        })
    })
}
getPosts().then((data) => {
    const postsList = document.querySelector('#postsList');
    removeAllChildNodes(postsList);

    data.map((post) => {
        makePost(post);
    })
})
