var theGame = null;

function init() {
    var canvas = document.getElementById("gameCanvas");
    var name = document.getElementById("heroName");
    var send = document.getElementById("send");
    theGame = new GameController(canvas);

    send.onclick = function(){
        theGame.sendName(name.value)
    };

}