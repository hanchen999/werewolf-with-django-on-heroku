$(function() {
    // When we're using HTTPS, use WSS too.
    var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
    var chatsock = new ReconnectingWebSocket(ws_scheme + '://' + window.location.host + "/chat" + window.location.pathname);

    (function my_func() {
    // your code
    var message = {
            handle: 'keepalive',
            message: 'vote',
            typo: 'keepalive'
        }
        chatsock.send(JSON.stringify(message));
        $("#message").val('').focus();
        return false;
        setTimeout( my_func, 30);
     })();

    
    chatsock.onmessage = function(message) {
        var data = JSON.parse(message.data);
        var chat = $("#chat")
        var ele = $('<tr></tr>')

        ele.append(
            $("<td></td>").text(data.timestamp)
        )
        ele.append(
            $("<td></td>").text(data.handle)
        )
        ele.append(
            $("<td></td>").text(data.message)
        ) 
        chat.append(ele)
    };

    $("#chatform").on("submit", function(event) {
        var message = {
            handle: $('#handle').val(),
            message: $('#message').val(),
            typo: 'Vote'
        }
        chatsock.send(JSON.stringify(message));
        $("#message").val('').focus();
        return false;
    });

    $("#startGame").on("submit", function(event) {
        var message = {
            handle: $('#handle').val(),
            message: 'vote',
            typo: 'startGame'
        }
        chatsock.send(JSON.stringify(message));
        $("#message").val('').focus();
        return false;
    });

    $("#identification").on("submit", function(event) {
        var message = {
            handle: $('#handle').val(),
            message: 'vote',
            typo: 'identification'
        }
        chatsock.send(JSON.stringify(message));
        $("#message").val('').focus();
        return false;
    });

    $("#jugdementView").on("submit", function(event) {
        var message = {
            handle: $('#handle').val(),
            message: 'vote',
            typo: 'judgement'
        }
        chatsock.send(JSON.stringify(message));
        $("#message").val('').focus();
        return false;
    });
    $("#poison").on("submit", function(event) {
        var message = {
            handle: $('#handle').val(),
            message: $('#message').val(),
            typo: 'poison'
        }
        chatsock.send(JSON.stringify(message));
        $("#message").val('').focus();
        return false;
    });

    $("#save").on("submit", function(event) {
        var message = {
            handle: $('#handle').val(),
            message: $('#message').val(),
            typo: 'save'
        }
        chatsock.send(JSON.stringify(message));
        $("#message").val('').focus();
        return false;
    });

    $("#bloom").on("submit", function(event) {
        var message = {
            handle: $('#handle').val(),
            message: 'vote',
            typo: 'save'
        }
        chatsock.send(JSON.stringify(message));
        $("#message").val('').focus();
        return false;
    });

    $("#bloom").on("submit", function(event) {
        var message = {
            handle: $('#handle').val(),
            message: 'vote',
            typo: 'save'
        }
        chatsock.send(JSON.stringify(message));
        $("#message").val('').focus();
        return false;
    });
});