var FPS = 60;
var TURN_ADDING = 2;
var SPEED_ADDING = 0.2;
var MAX_SPEED = 70;

var KEYCODE_UP = 38;
var KEYCODE_DOWN = 40;
var KEYCODE_LEFT = 37;
var KEYCODE_RIGHT = 39;
var KEYCODE_SPACE = 32;


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
var units;                 //Array with units
var newSpeed;

//register key functions
document.onkeydown = handleKeyDown;
document.onkeyup = handleKeyUp;


function send(){
    sendAction('fire');
}

function gameStart() {
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
    var socket = sockets();
    stage.removeChild(messageField);
}

//reset all game logic
function restart(heroObj, unitsObj) {
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
    hero = new createjs.Bitmap("static/images/hero.png");
    hero.scaleX = 0.2;
    hero.scaleY = 0.2;
    hero.id = heroObj.id;
    hero.x = heroObj.x0;
    hero.y = heroObj.y0;
    hero.speed = heroObj.speed;
    hero.rotation = heroObj.rotation;

    //create Units
    units = {};
    units[hero.id] = hero;

    //ensure stage is blank and add the hero
    stage.clear();
    stage.addChild(hero);

    for (var i in unitsObj) {
        if (unitsObj[i].id != hero.id) {
            var unit = new createjs.Shape();
            unit.graphics.beginFill("Black").drawRect(0, 0, 10, 15);
            unit.id = unitsObj[i].id;
            unit.x = unitsObj[i].x0;
            unit.y = unitsObj[i].y0;
            unit.speed = unitsObj[i].speed;
            unit.rotation = unitsObj[i].angle;
            units[unit.id] = unit;
            stage.addChild(unit);
        }
    }

    //reset key presses
    leftPress = rightPress = upPress = downPress = false;

    stage.update();

    //start game timer
    if (!createjs.Ticker.hasEventListener("tick")) {
        createjs.Ticker.setFPS(FPS);
        createjs.Ticker.addEventListener("tick", tick);
    }
    console.log(createjs.Ticker.getInterval())
}

function ShowSpeed(value) {
    scoreField.text = Number(value).toString();
}

function unitsUpdate(heroObj, unitsObj) {
    ShowSpeed(heroObj.speed);
    for (var key in units) {
        if (unitsObj.hasOwnProperty(key)){
            units[key].rotation = unitsObj[key].angle;
            units[key].x0 = unitsObj[key].x0;
            units[key].y0 = unitsObj[key].y0;
            units[key].x1 = unitsObj[key].x1;
            units[key].y1 = unitsObj[key].y1;
            units[key].x = unitsObj[key].x0;
            units[key].y = unitsObj[key].y0;
            units[key].speedTick = units[key].speed / window.frequency / FPS
        }
    }
}
//
//function unitUpdate(unitObj){
//
//}

function tick(event) {
    //handle turning
    if (alive && leftPress) {
        sendAction('rotate', -TURN_ADDING);
        //hero.rotation -= TURN_ADDING;
    } else if (alive && rightPress) {
        sendAction('rotate', TURN_ADDING);
        //hero.rotation += TURN_ADDING;
    }

    //handle speed
    if (alive && upPress) {
        newSpeed = hero.speed + SPEED_ADDING;
        if (newSpeed >= -MAX_SPEED && newSpeed <= MAX_SPEED) {
            hero.speed = newSpeed;
            ShowSpeed(hero.speed);
            sendAction('change_speed', SPEED_ADDING);
        }
    } else if (alive && downPress) {
        newSpeed = hero.speed - SPEED_ADDING;
        if (newSpeed >= -MAX_SPEED && newSpeed <= MAX_SPEED) {
            hero.speed = newSpeed;
            ShowSpeed(hero.speed);
            sendAction('change_speed', -SPEED_ADDING);
        }
    }

    for (var i in units){
        if (units[i].speed != 0 && units[i].speedTick) {
            if (units[i].x != units[i].x1 || units[i].y != units[i].y1) {
                units[i].x = window.width - units[i].x;
                units[i].y = window.height - units[i].y;
                units[i].x += Math.sin(units[i].rotation * (Math.PI / -180)) * units[i].speedTick;
                units[i].y += Math.cos(units[i].rotation * (Math.PI / -180)) * units[i].speedTick;
                units[i].x = window.width - units[i].x;
                units[i].y = window.height - units[i].y;
            }
        }
    }

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
        case KEYCODE_SPACE:
            console.log('space');
            return false;
    }
}

function handleKeyUp(e) {
    //cross browser issues exist
    if (!e) {
        var e = window.event;
    }
    switch (e.keyCode) {
        case KEYCODE_LEFT:
            leftPress = false;
            break;
        case KEYCODE_RIGHT:
            rightPress = false;
            break;
        case KEYCODE_UP:
            upPress = false;
            break;
        case KEYCODE_DOWN:
            downPress = false;
            break;
    }
}