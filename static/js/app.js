function init() {
    var stage = new createjs.Stage("demoCanvas");
    var circle = new createjs.Shape();
    circle.graphics.beginFill("DeepSkyBlue").drawCircle(0, 0, 50);
    circle.x = 100;
    circle.y = 100;
    stage.addChild(circle);
    stage.update();
    createjs.Tween.get(circle, {loop: true})
        .to({x: 1100}, 1000, createjs.Ease.getPowInOut(4))
        .to({alpha: 0, y: 475}, 500, createjs.Ease.getPowInOut(2))
        .to({alpha: 0, y: 425}, 100)
        .to({alpha: 1, y: 200}, 500, createjs.Ease.getPowInOut(2))
        .to({x: 100}, 800, createjs.Ease.getPowInOut(2));
    createjs.Ticker.setFPS(60);
    createjs.Ticker.addEventListener("tick", stage);
}


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
    console.log("received data " + event.data);
};

socket.onerror = function(error) {
    console.log("Error " + error.message);
};
