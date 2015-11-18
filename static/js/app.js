function init_game(gamer) {
    var canvas = document.getElementById("gameCanvas");
    var theGame = new GameController(canvas);
    theGame.createConnection(gamer);
};