const itemBlock =
    '<div id="item-message-block" class="d-flex p-3 border-top color-bg-accent">' +
    '<div id="item-message" class="overflow-hidden flex-self-center">' + '</div>' +
    '</div>'

var socket = io.connect('http://127.0.0.1:5000');
socket.on('connect', function () {
    console.log('Connected to server');
});

socket.on('response', function (data) {
    console.log('Received response:', data);
    const netItem = $(itemBlock).clone(true);
    netItem.attr("id", 'item');
    netItem.find('#item-message').text(data);
    $('#chat-list').append(netItem);
});

function sendMessage() {
    var message = document.getElementById('message').value;
    socket.emit('message', message);
}