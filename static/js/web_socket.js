

function createSocket(onMessage){
    var host = window.location.hostname;
    var socket = new WebSocket('ws://' + host + ':8765');

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

    socket.onmessage = onMessage;

    socket.onerror = function(error) {
        console.log("Error " + error.message);
    };
}



