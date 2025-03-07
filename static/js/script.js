setInterval(() => {
    fetch('/status')
        .then(response => response.json())
        .then(data => document.getElementById('status').innerText = data.status);
}, 1000);