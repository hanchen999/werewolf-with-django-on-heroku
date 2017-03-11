// var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
// var chatsock = new ReconnectingWebSocket(ws_scheme + '://' + window.location.host + "/chat" + window.location.pathname);

$(function() {
    // When we're using HTTPS, use WSS too.
    var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
    var temp = window.location.pathname;
    var str = temp.split("/");
    var position = str[1];
    var chatsock = new ReconnectingWebSocket(ws_scheme + '://' + window.location.host + "/chat/" + position);  
    chatsock.onopen = function() {
        var messageKeeplive = {
            handle: $('#handle').val(),
            message: 'vote',
            typo: 'keepalive'
        }
        chatsock.send(JSON.stringify(messageKeeplive));
    }
    chatsock.onmessage = function(message) {
        var messageKeeplive = {
            handle: $('#handle').val(),
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
        if (data.handle !== 'keepalive') {
            chat.append(ele)
        }
        if (data.typo === 'message1') {
            var audio = new Audio('https://s3-us-west-1.amazonaws.com/langrensha-assets/%E5%A4%A9%E9%BB%91%E8%AF%B7%E9%97%AD%E7%9C%BC.mp3')
            audio.play()
        }
        if (data.typo ==='message2') {
            var audio = new Audio('https://s3-us-west-1.amazonaws.com/langrensha-assets/%E5%A4%A9%E4%BA%AE%E8%AF%B7%E7%9D%81%E7%9C%BC.mp3')
            audio.play()
        }
        if (data.typo === 'message3') {
            var audio = new Audio('https://s3-us-west-1.amazonaws.com/langrensha-assets/%E7%8B%BC%E4%BA%BA%E8%AF%B7%E7%9D%81%E7%9C%BC.mp3');
            audio.play();
        }
        if (data.typo === 'message4') {
            var audio = new Audio('https://s3-us-west-1.amazonaws.com/langrensha-assets/%E7%8B%BC%E4%BA%BA%E8%AF%B7%E9%97%AD%E7%9C%BC.mp3');
            audio.play();
        }
        if (data.typo === 'message7') {
            var audio = new Audio('https://s3-us-west-1.amazonaws.com/langrensha-assets/%E5%A5%B3%E5%B7%AB%E8%AF%B7%E7%9D%81%E7%9C%BC.mp3');
            audio.play();
        }
        if (data.typo === 'message8') {
            var audio = new Audio('https://s3-us-west-1.amazonaws.com/langrensha-assets/%E5%A5%B3%E5%B7%AB%E8%AF%B7%E9%97%AD%E7%9C%BC.mp3');
            audio.play();
        }
        if (data.typo === 'message5') {
            var audio = new Audio('https://s3-us-west-1.amazonaws.com/langrensha-assets/%E9%A2%84%E8%A8%80%E5%AE%B6%E8%AF%B7%E7%9D%81%E7%9C%BC.mp3');
            audio.play();
        }
        if (data.typo === 'message6') {
            var audio = new Audio('https://s3-us-west-1.amazonaws.com/langrensha-assets/%E9%A2%84%E8%A8%80%E5%AE%B6%E8%AF%B7%E9%97%AD%E7%9C%BC.mp3');
            audio.play();
        }
        if (data.typo === 'message9') {
            var audio = new Audio('https://s3-us-west-1.amazonaws.com/langrensha-assets/%E5%AE%88%E5%8D%AB%E8%AF%B7%E7%9D%81%E7%9C%BC.mp3');
            audio.play();
        }
        if (data.typo === 'message10') {
            var audio = new Audio('https://s3-us-west-1.amazonaws.com/langrensha-assets/%E5%A5%B3%E5%B7%AB%E8%AF%B7%E9%97%AD%E7%9C%BC.mp3');
            audio.play();
        }
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

    $("#bloom").on("submit", function(event) {
        var message = {
            handle: $('#handle').val(),
            message: 'vote',
            typo: 'bloom'
        }
        chatsock.send(JSON.stringify(message));
        $("#message").val('').focus();
        return false;
    });

    var message = {
            handle: $('#handle').val(),
            message: 'verify the socket address',
            typo: 'Vote'
        }
});
