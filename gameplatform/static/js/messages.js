
function getCookie(name) { // from https://docs.djangoproject.com/en/3.0/ref/csrf/
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

$(document).ready(function () {
    'use strict';
    $(window).on('message', function (evt) {
        //Note that messages from all origins are accepted

        //Get data from sent message
        var data = evt.originalEvent.data;
        var csrftoken = getCookie('csrftoken');
        if (data.messageType === "SCORE") {
            $.post(window.location.href + "/score",
                {
                    player: user,
                    score: data.score,
                    csrfmiddlewaretoken: csrftoken
                }, function (data) {
                    console.log(data)
                    $("#scores").html(data.map(
                        x => "<tr><th class='scoreText'>" + x.player + ": </th><th class='scoreText'>" + x.score + "</th></tr>"
                    ))
                }
            );

        }
        else if (data.messageType === "SETTING") {
            var width = data.options.width
            var height = data.options.height
            document.getElementById("iframe").style.width = width;
            document.getElementById("iframe").style.height = height;
        }
        else if (data.messageType === "SAVE") {
            $.post(window.location.href + "/save",
                {
                    player: user,
                    gameState: JSON.stringify(data.gameState),
                    csrfmiddlewaretoken: csrftoken
                });
        }   // Asks for the saved gameState, if any
        else if (data.messageType === "LOAD_REQUEST") {
            $.get(window.location.href + "/save?player=" + user,
                function (data) {
                    var iFrame = document.getElementById("iframe")
                    var message = {
                        messageType: "LOAD",
                        gameState: JSON.parse(data.data)
                    };
                    iFrame.contentWindow.postMessage(message, '*')
                });
        }
    })
});