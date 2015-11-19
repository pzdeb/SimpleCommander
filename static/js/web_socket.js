

function createSocket(controller, name){
    var host = window.location.hostname;
    var port = window.location.port;
    var unit_name = name;
    if (port) {
        var socket = new WebSocket('ws://' + host + ':'+ port + '/ws_stream');
    } else {
        var socket = new WebSocket('ws://' + host + '/ws_stream');
    }

    socket.onopen = function(event) {
        console.log("Connected.");
        controller.sendToServer('start', unit_name)
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



