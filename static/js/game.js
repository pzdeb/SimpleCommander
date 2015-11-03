var FPS = 60;

var KEYCODE_UP = 38;
var KEYCODE_DOWN = 40;
var KEYCODE_LEFT = 37;
var KEYCODE_RIGHT = 39;
var KEYCODE_SPACE = 32;

var shown_hero_properties = {speed:0, life_count:0};
var height_property = 20;

var leftPress;
var rightPress;
var upPress;
var downPress;

var canvas;                //Main canvas
var stage;                 //Main display stage

var hero;                  //the actual hero
var alive;                 //whether the player is alive

var messageField;          //Message display field

//register key functions



function GameController(canvas) {
    this.hero = null;
    this.units = {};
    this.rotate = false;
    this.speed = false;
    this.canvas = canvas;

    var controller = this;
    document.onkeydown = function (e) {
        controller.handleKeyDown(e);
    };
    document.onkeyup = function (e) {
        controller.handleKeyUp(e);
    };


    this.prepareGame = function () {
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

    this.startGame = function () {
        var socket = createSocket(this);
        this.stage.removeChild(this.messageField);
        this.stage.update();
    };

    this.onData = function (event) {
        var answer = JSON.parse(event.data);
        console.log(answer);

        for (var key in answer){
            switch (key) {
                case 'init':
                    this.restart(answer.init);
                    break;
                case 'new':
                    this.newUnit(answer.new);
                    break;
                case 'update':
                    this.updateUnit(answer.update);
                    break;
            }
        }

    };

    this.restart = function (init) {
        //hide anything on stage and show the score
        var unitsObj = init['units'];
        var hero_id = init['hero_id'];
        var game_field = init['game'];
        this.frequency = init['frequency'];
        this.canvas.width = game_field.width;
        this.canvas.hight = game_field.hight;
        this.stage.removeAllChildren();

        //create Units
        this.units = {};

        //ensure stage is blank and add the hero
        this.stage.clear();
        this.stage.addChild(this.hero);

        for (var i in unitsObj) {
            var unit = new createjs.Bitmap("static/images/" + unitsObj[i].type + ".png");
            for (var property in unitsObj[i]) {
                if (property != 'angle') {
                    unit[property] = unitsObj[i][property];
                }
                if (property == 'angle') {
                    unit.rotation = unitsObj[i].angle;
                }
            }
            this.units[unit.id] = unit;
            this.stage.addChild(unit);
        }
        this.hero = this.units[hero_id];

        //Show hero property
        for (var property in shown_hero_properties){
            if (property in this.hero){
                shown_hero_properties[property] = new createjs.Text("", "bold 18px Arial", "#FFFFFF");
                shown_hero_properties[property].x = this.canvas.width - 20;
                shown_hero_properties[property].y = height_property;
                shown_hero_properties[property].textAlign = "right";
                var value = property + ": " + (this.hero[property]).toString();
                shown_hero_properties[property].text = value;
                this.stage.addChild(shown_hero_properties[property]);
                height_property += 20;
            }
            else{
                console.log('Hero does not have property ' + property)
            }
        }

        //reset key presses
        this.leftPress = this.rightPress = this.upPress = this.downPress = false;

        this.stage.update();

        //start game timer
        if (!createjs.Ticker.hasEventListener("tick")) {
            createjs.Ticker.setFPS(FPS);
            var controller = this;
            createjs.Ticker.addEventListener("tick", function () {
                controller.tick()
            });
        }
        console.log(createjs.Ticker.getInterval())
    };

    this.updateShownProperty = function(){
        for(var property in shown_hero_properties){
            if (property in this.hero){
                var value = property + ": " + (this.hero[property]).toString();
                shown_hero_properties[property].text = value;
            }
            else{
                console.log('Hero does not have property ' + property)
            }
        }
    };

    this.newUnit = function (unitData) {
        if (!this.units[unitData.id]) {
            var unit = new createjs.Bitmap("static/images/" + unitData.type + ".png");
            for (var property in unitData) {
                if (property != 'angle') {
                    unit[property] = unitData[property];
                }
                if (property == 'angle') {
                    unit.rotation = unitData.angle;
                }
            }
            this.units[unitData.id] = unit;
            this.stage.addChild(unit);
            this.stage.update();
        }
    };

    this.updateUnit = function (unitData) {
        var id = unitData['id'];

        for (var key in unitData) {
            if (this.units[id].hasOwnProperty(key)) {
                this.units[id][key] = unitData[key]

            }
            else if (key = 'angle') {
                this.units[id]['rotation'] = unitData[key]
            }
        }
        this.units[id].speedTick = this.units[id].speed / this.frequency / FPS;
        this.updateShownProperty();
    };

    this.tick = function (event) {

        var units = this.units;
        for (var i in units) {
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

    this.handleKeyDown = function (e) {
        //cross browser issues exist
        if (!e) {
            var e = window.event;
        }
        switch (e.keyCode) {
            case KEYCODE_LEFT:
                if (!this.leftPress) {
                    this.leftPress = true;
                    this.sendAction('rotate', 'left')
                }
                return false;
            case KEYCODE_RIGHT:
                if (!this.leftPress) {
                    this.leftPress = true;
                    this.sendAction('rotate', 'right')
                }
                return false;
            case KEYCODE_UP:
                //TODO: What is the meaning of `speed` as boolean. Non sense to me
                if (!this.speed) {
                    this.speed = true;
                    this.sendAction('change_speed', 'front');
                }
                return false;
            case KEYCODE_DOWN:
                if (!this.speed) {
                    this.speed = true;
                    this.sendAction('change_speed', 'back');
                }
                return false;
            case KEYCODE_SPACE:
                console.log('space');
                return false;
        }
    };

    this.handleKeyUp = function (e) {
        //cross browser issues exist
        if (!e) {
            var e = window.event;
        }
        switch (e.keyCode) {
            case KEYCODE_LEFT:
                if (this.leftPress) {
                    this.leftPress = false;
                    this.sendAction('rotate', 'stop')
                }
                break;
            case KEYCODE_RIGHT:
                if (this.leftPress) {
                    this.leftPress = false;
                    this.sendAction('rotate', 'stop')
                }
                break;
            case KEYCODE_UP:
                if (this.speed) {
                    this.speed = false;
                    this.sendAction('change_speed', 'stop')
                }
                break;
            case KEYCODE_DOWN:
                if (this.speed) {
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