var FPS = 60;

var KEYCODE_UP = 38;
var KEYCODE_DOWN = 40;
var KEYCODE_LEFT = 37;
var KEYCODE_RIGHT = 39;
var KEYCODE_SPACE = 32;

var tableScorecards = {name:'', speed:0, life_count:0};
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
    this.socket = null;

    var controller = this;
    document.onkeydown = function (e) {
        controller.handleKeyDown(e);
    };
    document.onkeyup = function (e) {
        controller.handleKeyUp(e);
    };

    this.createConnection = function () {
        this.socket = createSocket(this);
    };

    this.sendToServer = function (heroAction, value) {
        var data = {};
        data[heroAction] = value;
        var data = JSON.stringify(data);
        this.socket.send(data);
    };

    this.onData = function (event) {
        var answer = JSON.parse(event.data);
        console.log(answer);

        for (var key in answer){
            switch (key) {
                case 'init':
                    this.start(answer.init);
                    break;
                case 'error':
                    this.error(answer.error);
                    break;
                case 'new':
                    this.newUnit(answer.new);
                    break;
                case 'update':
                    this.updateUnit(answer.update);
                    break;
                case 'delete':
                    this.killUnit(answer.delete);
                    break;
                case 'update_life':
                    this.updateLife(answer.update_life);
                    break;
            }
        }

    };

    this.error = function(error) {
        console.log(error)
    };

    this.start = function (init) {
        var unitsObj = init['units'];
        var hero_id = init['hero_id'];
        var game_field = init['game'];
        this.frequency = init['frequency'];
        this.canvas.width = game_field.width;
        this.canvas.height = game_field.height;
        this.stage = new createjs.Stage(this.canvas);

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
            unit.regX = unit.width / 2;
            unit.regY = unit.height / 2;
            this.units[unit.id] = unit;
            this.stage.addChild(unit);
        }
        this.hero = this.units[hero_id];

        //Show hero property
        for (var property in tableScorecards){
            if (property in this.hero){
                tableScorecards[property] = new createjs.Text("", "bold 18px Arial", "#FFFFFF");
                tableScorecards[property].x = this.canvas.width - 20;
                tableScorecards[property].y = height_property;
                tableScorecards[property].textAlign = "right";
                var value = property + ": " + (this.hero[property]).toString();
                tableScorecards[property].text = value;
                this.stage.addChild(tableScorecards[property]);
                height_property += 20;
            }
            else{
                console.log('Hero does not have property ' + property)
            }
        }

        //reset key presses
        this.leftPress = this.rightPress = this.upPress = this.downPress = this.spascePress = false;

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

    this.updateTableScorecards = function(){
        for(var property in tableScorecards){
            if (property in this.hero){
                var value = property + ": " + (this.hero[property]).toString();
                tableScorecards[property].text = value;
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
        this.units[id].regX = this.units[id].width / 2;
        this.units[id].regY = this.units[id].height / 2;
        this.units[id].speedTick = this.units[id].speed / this.frequency / FPS;
        if (id == this.hero['id']){
            this.updateTableScorecards()
        }

    };

    this.killUnit = function (unitData) {
        var id = unitData['id'];
        this.stage.removeChild(this.units[id]);
        this.stage.update();
        delete this.units[id];
    };

    this.updateLife = function (unitData) {
        var id = unitData['id'];
        this.units[id].life_count = unitData.life_count;
        this.updateTableScorecards();
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
                    this.sendToServer('rotate_left', null)
                }
                return false;
            case KEYCODE_RIGHT:
                if (!this.leftPress) {
                    this.leftPress = true;
                    this.sendToServer('rotate_right', null)
                }
                return false;
            case KEYCODE_UP:
                //TODO: What is the meaning of `speed` as boolean. Non sense to me
                if (!this.speed) {
                    this.speed = true;
                    this.sendToServer('change_speed_up', null);
                }
                return false;
            case KEYCODE_DOWN:
                if (!this.speed) {
                    this.speed = true;
                    this.sendToServer('change_speed_down', null);
                }
                return false;
            case KEYCODE_SPACE:
                if (!this.spascePress){
                    this.spascePress = true;
                    this.sendToServer('start_fire', null);
                }
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
                    this.sendToServer('stop_rotate', null)
                }
                break;
            case KEYCODE_RIGHT:
                if (this.leftPress) {
                    this.leftPress = false;
                    this.sendToServer('stop_rotate', null)
                }
                break;
            case KEYCODE_UP:
                if (this.speed) {
                    this.speed = false;
                    this.sendToServer('stop_change_speed', null)
                }
                break;
            case KEYCODE_DOWN:
                if (this.speed) {
                    this.speed = false;
                    this.sendToServer('stop_change_speed', null)
                }
                break;
            case KEYCODE_SPACE:
                if (this.spascePress){
                    this.spascePress = false;
                    this.sendToServer('stop_fire', null)
                }
                break;
        }
    };

    this.sendAction = function (action) {
        var http = new XMLHttpRequest();
        var url = "api/hero/" + this.hero.id + "/action/" + action;
        http.open("POST", url, true);
        http.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
        http.send();
    }

}