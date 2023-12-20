const getPosts = async () => {
    const response = await fetch('http://127.0.0.1:8000/api/posts?start=0&limit=10');
    return await response.json();
}

const postsList = document.querySelector('#postsList');

likePost = (postId) => {
//     push like to api 
}

getPosts().then((data) => {
    data.map((post) => {
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
        title.appendChild(userName);
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
