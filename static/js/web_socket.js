function sockets(){
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
        var data = JSON.parse(event.data);
        if (data.id){
            document.cookie = "hero_id=" + data.id;
        }
        console.log(data)
    };

    socket.onerror = function(error) {
        console.log("Error " + error.message);
    };

}



