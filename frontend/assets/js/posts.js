const postTemplate = document.querySelector('#postTemplate');

cleanPostDialog = (createPostDialog) => {
    createPostDialog.querySelector('#parentPost').innerHTML = '-';
    createPostDialog.querySelector('#createPostMessage').innerHTML = '';
    createPostDialog.querySelector('#parentPostId').value = -1;
    createPostDialog.querySelector('#newPost').value = '';
}

removeAllChildNodes = (parent) => {
    while (parent.firstChild) {
        parent.removeChild(parent.firstChild);
    }
}

createPost = async (event) => {
    event.preventDefault();
    const body = {
        "content": createPostForm.newPost.value,
        "parent_post": parseInt(createPostForm.parentPostId.value)
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
                const postsList = document.querySelector('#postsList');
                removeAllChildNodes(postsList);

                getPosts().then((data) => {
                    data.map((post) => {
                        makePost(post, postsList, postTemplate);
                    })
                })
                cleanPostDialog(createPostDialog);
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

getPosts = async () => {
    const response = await fetch('http://127.0.0.1:8000/api/posts');
    return await response.json();
}

getComments = async (postId) => {
    const response = await fetch(`http://127.0.0.1:8000/api/post/${postId}/comments`);
    return await response.json();
}

getUserPosts = async (userName) => {
    const response = await fetch(`http://127.0.0.1:8000/api/posts/${userName}`);
    return await response.json();
}

likePost = async (postId) => {
    try {
        const response = await fetch(`http://127.0.0.1:8000/api/post/${postId}/like`, {
            method: "PUT",
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${jwt}`
            }
        });
        const data = await response.json();
        switch(response.status) {
            case 201:
                break;
            default:
        }
    } catch (e) {
        console.error(e);
    }
}

moderatePost = async (postId) => {
    try {
        const response = await fetch(`http://127.0.0.1:8000/api/post/${postId}/isFake`, {
            method: "PUT",
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${jwt}`
            }
        });
        const data = await response.json();
        switch(response.status) {
            case 201:
                break;
            default:
        }
    } catch (e) {
        console.error(e);
    }
}

postComment = (postId) => {
    const post = document.querySelector(`#post_${postId} p`);
    createPostForm.querySelector('#parentPostId').value = postId;
    createPostDialog.querySelector('#parentPost').innerHTML = post.innerHTML;
    createPostDialog.showModal();
}

makeUserPostsList = (userName) => {
    const postsList = document.querySelector('#postsList');

    removeAllChildNodes(postsList);

    getUserPosts(event.target.getAttribute('data-user')).then((data) => {
        data.map((post) => {
            makePost(post, postsList, postTemplate);
        })
    })
    allPosts.classList.remove('hidden');
}

showComments = (event, postId, postElement) => {
    const postsList = postElement.querySelector('.comments');
    if (event.target.classList.contains('open')) {
        removeAllChildNodes(postsList);
        event.target.classList.remove('open')
    } else {
        getComments(postId).then((data) => {
            event.target.classList.add('open')
            removeAllChildNodes(postsList);
            data.map((post) => {
                makePost(post, postsList, postTemplate);
            })
        })
    }
}

makePost = (post, postsList, postTemplate) => {
    const allPosts = document.querySelector('#allPosts');
    const postContent = postTemplate.content.cloneNode(true);
    const postLi = postContent.querySelector('li');
    const title = postContent.querySelector('h3');
    const seeAll = postContent.querySelector('.see_all');
    const seeAllComments = postContent.querySelector('.see_all_comments');
    const comment = postContent.querySelector('.comment');
    const content = postContent.querySelector('.post_content');
    const likeCount = postContent.querySelector('.post_likes');
    const like = postContent.querySelector('.like');
    const moderate = postContent.querySelector('.moderate');
    const fackCheck = postContent.querySelector('.fact_check');

    postLi.setAttribute('id', `post_${post.id}`);
    postLi.setAttribute('data-id', post.id);

    title.textContent = post.user_name;
    if (post.has_comments) {
        seeAllComments.classList.remove('hidden');
        seeAllComments.addEventListener('click', () => {
            showComments(event, post.id, postLi);
        })
    }
    seeAll.setAttribute('data-user', post.user_name);
    seeAll.addEventListener('click', () => {
        allPosts.classList.remove('hidden');
        makeUserPostsList(post.user_name);
    })
    content.innerHTML = post.content;
    if (post.likes !== null) {
        likeCount.innerHTML = post.likes;
    }
    if (loggedIn) {
        like.setAttribute('data-id', post.id);
        like.addEventListener('click', () => {
            likePost(post.id);
        })
        comment.addEventListener('click', () => {
            postComment(post.id);
        })
        if (currentUser.userName == post.user_name) {
            like.setAttribute('disabled', true);
        }
        if (currentUser.moderator) {
            moderate.classList.remove('hidden');
            moderate.addEventListener('click', () => {
                moderatePost(post.id);
            })
        }
    } else {
        comment.setAttribute('disabled', true);
        like.setAttribute('disabled', true);
    }
    if (post.fact_check) {
        postLi.classList.add('false_claim');
        like.setAttribute('disabled', true);
        fackCheck.classList.remove('hidden');
    }
    postsList.appendChild(postContent);
}

getPosts().then((data) => {
    const postsList = document.querySelector('#postsList');
    removeAllChildNodes(postsList);

    data.map((post) => {
        if (post.parent_post == -1) {
            makePost(post, postsList, postTemplate);
        }
    })
})
