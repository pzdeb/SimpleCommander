function sendAction(data){
    var http = new XMLHttpRequest();
    http.open("POST", "action", true);
    http.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
    http.onload = function () {
        console.log(this.responseText);
    };
    http.send(JSON.stringify(data));
}