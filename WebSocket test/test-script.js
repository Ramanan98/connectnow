const socket = new WebSocket('ws://localhost:8000/get_matches/');
//id is the one that's in auth_user table, change it accordingly
const id = 6;
// Connection opened
socket.addEventListener('open', function (event) {
    socket.send(JSON.stringify({
        'id': id
    }));
});

// Listen for messages
socket.addEventListener('message', function (event) {
    console.log('Message from server ', event.data);
});