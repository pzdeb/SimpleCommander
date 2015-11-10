var theGame = null;

function init() {
    var canvas = document.getElementById("gameCanvas");
    var form = document.getElementById("formStartGame");
    var name = document.getElementById("heroName");
    theGame = new GameController(canvas);

    form.addEventListener("submit", function (e) {
        e.preventDefault();
        if (!theGame.socket){
            theGame.createConnection(name.value)
        }
        else{
            theGame.sendToServer('set_name', name.value)
        }

    }, false)

}