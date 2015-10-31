var theGame = null;

function init() {
    var canvas = document.getElementById("gameCanvas");
    theGame = new GameController(canvas);

    function handleCanvasClick(c) {
        this.onclick = null;
        theGame.startGame();
    }
    canvas.onclick = handleCanvasClick;

    theGame.prepareGame();

}

