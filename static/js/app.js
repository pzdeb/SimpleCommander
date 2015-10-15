var TURN_FACTOR = 7;
var SPEED_FACTOR = 1;

var KEYCODE_UP = 38;
var KEYCODE_DOWN = 40;
var KEYCODE_LEFT = 37;
var KEYCODE_RIGHT = 39;

var leftPress;
var rightPress;
var upPress;
var downPress;

var canvas;                //Main canvas
var stage;                 //Main display stage

var hero;                  //the actual hero
var alive;                 //whether the player is alive

var messageField;          //Message display field
var scoreField;            //score Field

//register key functions
document.onkeydown = handleKeyDown;

function init() {
    canvas = document.getElementById("gameCanvas");
    stage = new createjs.Stage(canvas);
    messageField = new createjs.Text("Welcome: Click to play", "bold 24px Arial", "#000");
    messageField.maxWidth = 1000;
    messageField.textAlign = "center";
    messageField.textBaseline = "middle";
    messageField.x = canvas.width / 2;
    messageField.y = canvas.height / 2;
    stage.addChild(messageField);
    stage.update();     //update the stage to show text
    canvas.onclick = handleClick;
}

function handleClick() {
    //prevent extra clicks and hide text
    canvas.onclick = null;
    stage.removeChild(messageField);
    restart();
}

//reset all game logic
function restart() {
    //hide anything on stage and show the score
    stage.removeAllChildren();
    scoreField = new createjs.Text("0", "bold 18px Arial", "#FFFFFF");
    scoreField.textAlign = "right";
    scoreField.x = canvas.width - 20;
    scoreField.y = 20;
    scoreField.maxWidth = 1000;
    scoreField.text = (0).toString();
    stage.addChild(scoreField);

    //create the player
    alive = true;
    hero = new createjs.Shape();
    hero.graphics.beginFill("DeepSkyBlue").drawRect(0, 0, 10, 15);
    hero.x = canvas.width / 2;
    hero.y = canvas.height / 2;
    hero.speed = 0;
    hero.rotation = 0;

    //reset key presses
    leftPress = rightPress = upPress = downPress = false;

    //ensure stage is blank and add the hero
    stage.clear();
    stage.addChild(hero);
    stage.update();

    //start game timer
    if (!createjs.Ticker.hasEventListener("tick")) {
        createjs.Ticker.addEventListener("tick", tick);
    }
}

function ShowSpeed(value) {
    scoreField.text = Number(value).toString();
}

function tick(event) {
    //handle turning
    if (alive && leftPress) {
        hero.rotation -= TURN_FACTOR;
        leftPress = false;
    } else if (alive && rightPress) {
        hero.rotation += TURN_FACTOR;
        rightPress = false;
    }

    //handle speed
    if (alive && upPress) {
        hero.speed += SPEED_FACTOR;
        ShowSpeed(hero.speed);
        upPress = false;
    } else if (alive && downPress) {
        hero.speed -= SPEED_FACTOR;
        ShowSpeed(hero.speed);
        downPress = false;
    }

    hero.x += Math.sin(hero.rotation * (Math.PI / -180)) * hero.speed;
    hero.y += Math.cos(hero.rotation * (Math.PI / -180)) * hero.speed;

    stage.update();

}

//allow for arrow control scheme
function handleKeyDown(e) {
    //cross browser issues exist
    if (!e) {
        var e = window.event;
    }
    switch (e.keyCode) {
        case KEYCODE_LEFT:
            leftPress = true;
            return false;
        case KEYCODE_RIGHT:
            rightPress = true;
            return false;
        case KEYCODE_UP:
            upPress = true;
            return false;
        case KEYCODE_DOWN:
            downPress = true;
            return false;
    }
}
