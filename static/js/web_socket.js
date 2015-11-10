

function createSocket(controller){
    var host = window.location.hostname;
    var socket = new WebSocket('ws://' + host + ':8765');
    var hero_name = document.getElementById("heroName");

    socket.onopen = function(event) {
        console.log("Connected.");
        controller.sendToServer('start', hero_name.value)
    };

    socket.onclose = function(event) {
        if (event.wasClean) {
            console.log('Connection closed');
        } else {
            console.log('disconnection');
        }
            console.log('code: ' + event.code + ' reason: ' + event.reason);
    };

    socket.onmessage = function(ans) {
        controller.onData(ans);
    };

    socket.onerror = function(error) {
        console.log("Error " + error.message);
    };
    return socket
}



