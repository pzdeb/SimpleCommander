function SocketHandler(controller, name) {
    "use strict";

    /*global window */
    /*global WebSocket */
    var host = window.location.hostname,
        port = window.location.port,
        unit_name = name,
        socket;
    if (port) {
        socket = new WebSocket('ws://' + host + ':' + port + '/ws_stream');
    } else {
        socket = new WebSocket('ws://' + host + '/ws_stream');
    }

    socket.onopen = function () {
        console.log("Connected.");
        controller.sendToServer('start', unit_name);
    };

    socket.onclose = function (event) {
        if (event.wasClean) {
            console.log('Connection closed');
        } else {
            console.log('disconnection');
        }
        console.log('code: ' + event.code + ' reason: ' + event.reason);
    };

    socket.onmessage = function (ans) {
        controller.onData(ans);
    };

    socket.onerror = function (error) {
        console.log("Error " + error.message);
    };

    return socket;
}



