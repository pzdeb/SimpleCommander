function sendAction(action, value){
    var http = new XMLHttpRequest();
    var url = "api/hero/" + window.heroId + "/action/" + action;
    http.open("POST", url, true);
    http.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
    http.onload = function () {
        console.log(this.responseText);
    };
    http.send(JSON.stringify({'value': value}));
}
function getCookie(cname) {
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for(var i=0; i<ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') c = c.substring(1);
        if (c.indexOf(name) == 0) return c.substring(name.length,c.length);
    }
    return "";
}