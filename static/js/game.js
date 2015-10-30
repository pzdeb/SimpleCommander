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
    hero = new createjs.Shape();
    hero.graphics.beginFill("DeepSkyBlue").drawRect(0, 0, 10, 15);
    hero.id = heroObj.id;
    hero.x = heroObj.x;
    hero.y = heroObj.y;
    hero.speed = heroObj.speed;
    hero.rotation = heroObj.angle;

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
            unit.x = unitsObj[i].x;
            unit.y = unitsObj[i].y;
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

function unitUpdate(unitObj){
    var id = unitObj['id']
    for (var key in unitObj){
        if (units[id].hasOwnProperty(key)){
            units[id][key] = unitObj[key]

        }
        else if(key = 'angle'){
            units[id]['rotation'] = unitObj[key]
        }
    }
    units[id].speedTick = units[id].speed / window.frequency / FPS
}

function tick(event) {
    ShowSpeed(hero.speed);

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
var rotate = false;
var speed = false;
//allow for arrow control scheme
function handleKeyDown(e) {
    //cross browser issues exist
    if (!e) {
        var e = window.event;
    }
    switch (e.keyCode) {
        case KEYCODE_LEFT:
            if (!leftPress){
                leftPress = true;
                sendAction('rotate', 'left')
            }
            return false;
        case KEYCODE_RIGHT:
            if (!leftPress){
                leftPress = true;
                sendAction('rotate', 'right')
            }
            return false;
        case KEYCODE_UP:
            if (!speed){
                speed = true;
                sendAction('change_speed', 'front');
            }
            return false;
        case KEYCODE_DOWN:
            if (!speed){
                speed = true;
                sendAction('change_speed', 'back');
            }
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
            if (leftPress){
                leftPress = false;
                sendAction('rotate', 'stop')
            }
            break;
        case KEYCODE_RIGHT:
            if (leftPress){
                leftPress = false;
                sendAction('rotate', 'stop')
            }
            break;
        case KEYCODE_UP:
           if (speed){
                speed = false;
                sendAction('change_speed', 'stop')
           }
            break;
        case KEYCODE_DOWN:
            if (speed){
                speed = false;
                sendAction('change_speed', 'stop')
            }
            break;
    }
}