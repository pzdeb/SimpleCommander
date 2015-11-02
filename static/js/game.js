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
var newSpeed;

//register key functions



function GameController(canvas) {
    this.hero = null;
    this.units = {};
    this.rotate = false;
    this.speed = false;
    this.canvas = canvas;

    var controller = this;
    document.onkeydown = function(e) { controller.handleKeyDown(e); };
    document.onkeyup = function(e) { controller.handleKeyUp(e); };


    this.prepareGame = function() {
        this.stage = new createjs.Stage(this.canvas);
        this.messageField = new createjs.Text("Welcome: Click to play", "bold 24px Arial", "#000");
        this.messageField.maxWidth = 1000;
        this.messageField.textAlign = "center";
        this.messageField.textBaseline = "middle";
        this.messageField.x = this.canvas.width / 2;
        this.messageField.y = this.canvas.height / 2;
        this.stage.addChild(this.messageField);
        this.stage.update();     //update the stage to show text
    };
    //create the player
    alive = true;
    hero = new createjs.Bitmap("static/images/" +heroObj.type+ ".png");
    hero.id = heroObj.id;
    hero.x = heroObj.x;
    hero.y = heroObj.y;
    hero.speed = heroObj.speed;
    hero.rotation = heroObj.angle;

    this.startGame = function() {
        var socket = createSocket(this);
        this.stage.removeChild(this.messageField);
        this.stage.update();
    };

    this.onData = function (event) {
        var answer = JSON.parse(event.data);
        console.log(answer);

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

        //else if (answer.length == 0) {
        //    hero = answer[heroId];
        //    restart(hero, answer);
        //}
    };


    this.restart = function(init) {
        //hide anything on stage and show the score
        var unitsObj = init['units'];
        var hero_id = init['hero_id'];
        var game_field = init['game'];
        this.frequency = init['frequency'];
        this.canvas.width = game_field.width;
        this.canvas.hight = game_field.hight;
        this.stage.removeAllChildren();
        scoreField = new createjs.Text("0", "bold 18px Arial", "#FFFFFF");
        scoreField.textAlign = "right";
        scoreField.x = this.canvas.width - 20;
        scoreField.y = 20;
        scoreField.maxWidth = 1000;
        scoreField.text = (0).toString();
        this.stage.addChild(scoreField);

        //create Units
        this.units = {};

        //ensure stage is blank and add the hero
        this.stage.clear();
        this.stage.addChild(this.hero);

        for (var i in unitsObj) {
            var unit = new createjs.Bitmap("static/images/" + unitsObj[i].type + ".png");
            if (unitsObj[i].id = hero_id){
                unit.graphics.beginFill("DeepSkyBlue").drawRect(0, 0, 10, 15);
            }
            else{
                unit.graphics.beginFill("Black").drawRect(0, 0, 10, 15);
            }
            for (var property in unitsObj[i]){
                if (property != 'angle') {
                    unit[property] = unitsObj[i][property];
                }
                if (property == 'angle'){
                    unit.rotation = unitsObj[i].angle;
                }
            }
            this.units[unit.id] = unit;
            this.stage.addChild(unit);
        }
        this.hero = this.units[hero_id];

        //reset key presses
        this.leftPress = this.rightPress = this.upPress = this.downPress = false;

        this.stage.update();

        //start game timer
        if (!createjs.Ticker.hasEventListener("tick")) {
            createjs.Ticker.setFPS(FPS);
            var controller = this;
            createjs.Ticker.addEventListener("tick", function() {controller.tick()});
        }
        console.log(createjs.Ticker.getInterval())
    };

    this.showSpeed = function(value) {
        scoreField.text = Number(value).toString();
    };

    this.newUnit = function(unitData) {
        if (!this.units[unitData.id]){
            this.units[unitData] = unitData;
        }
    };

    this.updateUnit = function(unitData){
        var id = unitData['id'];

        for (var key in unitData){
            if (this.units[id].hasOwnProperty(key)){
                this.units[id][key] = unitData[key]

            }
            else if(key = 'angle'){
                this.units[id]['rotation'] = unitData[key]
            }
        }
        this.units[id].speedTick = this.units[id].speed / this.frequency / FPS
    };

    this.tick = function(event) {
        this.showSpeed(this.hero.speed);

        var units = this.units;
        for (var i in units){
            if (units[i].speed != 0 && units[i].speedTick) {
                if (units[i].x != units[i].x1 || units[i].y != units[i].y1) {
                    units[i].x = this.canvas.width - units[i].x;
                    units[i].y = this.canvas.height - units[i].y;
                    units[i].x += Math.sin(units[i].rotation * (Math.PI / -180)) * units[i].speedTick;
                    units[i].y += Math.cos(units[i].rotation * (Math.PI / -180)) * units[i].speedTick;
                    units[i].x = this.canvas.width - units[i].x;
                    units[i].y = this.canvas.height - units[i].y;
                }
            }
        }

        this.stage.update();

    };

    this.handleKeyDown = function(e) {
        //cross browser issues exist
        if (!e) {
            var e = window.event;
        }
        switch (e.keyCode) {
            case KEYCODE_LEFT:
                if (!this.leftPress){
                    this.leftPress = true;
                    this.sendAction('rotate', 'left')
                }
                return false;
            case KEYCODE_RIGHT:
                if (!this.leftPress){
                    this.leftPress = true;
                    this.sendAction('rotate', 'right')
                }
                return false;
            case KEYCODE_UP:
                //TODO: What is the meaning of `speed` as boolean. Non sense to me
                if (!this.speed){
                    this.speed = true;
                    this.sendAction('change_speed', 'front');
                }
                return false;
            case KEYCODE_DOWN:
                if (!this.speed){
                    this.speed = true;
                    this.sendAction('change_speed', 'back');
                }
                return false;
            case KEYCODE_SPACE:
                console.log('space');
                return false;
        }
    };

    this.handleKeyUp = function(e) {
        //cross browser issues exist
        if (!e) {
            var e = window.event;
        }
        switch (e.keyCode) {
            case KEYCODE_LEFT:
                if (this.leftPress){
                    this.leftPress = false;
                    this.sendAction('rotate', 'stop')
                }
                break;
            case KEYCODE_RIGHT:
                if (this.leftPress){
                    this.leftPress = false;
                    this.sendAction('rotate', 'stop')
                }
                break;
            case KEYCODE_UP:
               if (this.speed){
                    this.speed = false;
                    this.sendAction('change_speed', 'stop')
               }
                break;
            case KEYCODE_DOWN:
                if (this.speed){
                    this.speed = false;
                    this.sendAction('change_speed', 'stop')
                }
                break;
        }
    };

    this.sendAction = function (action, value) {
        var http = new XMLHttpRequest();
        var url = "api/hero/" + this.hero.id + "/action/" + action + "/" + value;
        http.open("POST", url, true);
        http.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
        http.send(JSON.stringify({'value': value}));
    }

}

