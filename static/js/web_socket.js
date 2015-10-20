var socket = new WebSocket("ws://localhost:8765");



socket.onopen = function(event) {
    console.log("Connected.");
};


socket.onclose = function(event) {
    if (event.wasClean) {
        console.log('Connection closed');
    } else {
        console.log('disconnection');
    }
        console.log('code: ' + event.code + ' reason: ' + event.reason);
};

socket.onmessage = function(event) {
    var answer = JSON.parse(event.data) || event.data;
    console.log(answer)
};

socket.onerror = function(error) {
    console.log("Error " + error.message);
};

function send(){
    socket.send('hi')
};


