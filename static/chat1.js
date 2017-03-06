// var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
// var chatsock = new ReconnectingWebSocket(ws_scheme + '://' + window.location.host + "/chat" + window.location.pathname);

$(function() {
    // When we're using HTTPS, use WSS too.
    var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
    var chatsock = new ReconnectingWebSocket(ws_scheme + '://' + window.location.host + "/chat" + window.location.pathname);    
    chatsock.onmessage = function(message) {
        var messageKeeplive = {
            handle: 0,
            message: 'vote',
            typo: 'keepalive'
        }
        //var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
        //var chatsock = new ReconnectingWebSocket(ws_scheme + '://' + window.location.host + "/chat" + window.location.pathname);   
        chatsock.send(JSON.stringify(messageKeeplive));
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
        if (data.handle != 'keepalive')
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

    console.log(1);

    var audio = new Audio('https://s3-us-west-1.amazonaws.com/langrensha-assets/%E6%9F%AF%E5%8D%97%E4%B8%BB%E9%A1%8Csong+-+%E6%9F%AF%E5%8D%97%E4%B8%BB%E9%A1%8Csong.mp3');
    audio.play();
    console.log(2);
});
