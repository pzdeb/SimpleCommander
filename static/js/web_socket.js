function sockets(){
    var socket = new WebSocket("ws://localhost:8765");
    var frequency = 1;
    var hero = {};
    var heroId = '';
    var units = [];

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
        console.log(answer);
        if (answer.hasOwnProperty('frequency')) {
            frequency = answer.frequency;
            heroId = answer.id;
        }
        else if (units.length == 0) {
            units = answer;
            hero = units[heroId];
            restart(hero, units);
        }
        else {
            units = answer;
            hero = units[heroId];
            unitsUpdate(hero, units);
        }
    };

    socket.onerror = function(error) {
        console.log("Error " + error.message);
    };

    return socket
}



