(function () {
    var Message;
    Message = function (arg) {
        this.text = arg.text, this.message_side = arg.message_side;
        this.draw = function (_this) {
            return function () {
                var $message;
                $message = $($('.message_template').clone().html());
                $message.addClass(_this.message_side).find('.text').html(_this.text);
                $('.messages').append($message);
                return setTimeout(function () {
                    return $message.addClass('appeared');
                }, 0);
            };
        }(this);
        return this;
    };
    $(function () {
        var getMessageText, message_side, putMessage, sendMessage;
        message_side = 'right';
        getMessageText = function () {
            var $message_input;
            $message_input = $('.message_input');
            return $message_input.val();
        };
        putMessage = function (text) {
            var $messages, message;
            if (text.trim() === '') {
                return;
            }
            $('.message_input').val('');
            $messages = $('.messages');
            message_side = 'left';
            message = new Message({
                text: text,
                message_side: message_side
            });
            message.draw();
            return $messages.animate({ scrollTop: $messages.prop('scrollHeight') }, 300);
        };
        // Track all of the chats we've seen -- Don't strictly need
        // this / use it right now
        var messages = [];
        // Keeps track of the last element we've seen
        var getChatsFrom = 0;
        
        update = function() {
            $.getJSON("/chats/from/" + getChatsFrom,function(chats) {
                if (Array.isArray(chats)) {
                    messages.push(chats);
                    if (chats.length > 0) {
                        getChatsFrom = chats[chats.length-1].id+1;
                        chats.forEach(function(chat) {
                            putMessage("> " + chat.username + ": " + chat.content + "\n");
                        });
                    }
                }
            });
        };

        // Update the chats every 200 milliseconds
        setInterval(update, 200);
        
        var sendMessage = function (text) {
            $.ajax
            ({
                type: "POST",
                //the url where you want to sent the userName and password to
                url: '/chat',
                dataType: 'json',
                contentType: 'application/json',
                data: '{"uid": "' + $('#uid').val() + '", "content" : "' + text + '"}',
            });
        };

        $('.send_message').click(function (e) {
            return sendMessage(getMessageText());
        });
        $('.message_input').keyup(function (e) {
            if (e.which === 13) {
                return sendMessage(getMessageText());
            }
        });
    });
}.call(this));

