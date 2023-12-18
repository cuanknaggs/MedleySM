const isLoggedIn = () => {
    console.log(document.cookie);
    const cookieValue = document.cookie
        .split("; ")
        .find((row) => row.startsWith("value="))
        ?.split("=")[1];
    console.log(cookieValue);
    const options = {
        method: 'GET',
        headers: {
            Authorization: `Bearer ${cookieValue}`
        }
        };

        fetch('http://127.0.0.1:8000/api/users/me/', options)
            .then(response => response.json())
            .then(response => console.log(response))
            .catch(err => console.error(err));
}
isLoggedIn();
