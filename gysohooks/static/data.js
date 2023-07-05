const baseItem = $('#base-item').clone().removeAttr('id').removeClass('d-none');

const socket = io.connect('http://127.0.0.1:5000');

$(document).ready(function () {
    //baseItem.appendTo('#capture-list').show();
});

socket.on('connect', function () {
    console.log('Connected to server');
});

socket.on('response', function (data) {
    console.log('Received response:', data);
    let netItem = baseItem.clone(true);
    netItem.find('#base-item-url').text(data);
    netItem.appendTo('#capture-list').show();
});

$('#clear-data').click(() => {
    $('#capture-list').empty();
})

$('#export-data').click(() => {

})

$('#import-data').click(() => {

})

$('#stop-start-capture').click(() => {

})

function sendMessage() {
    let message = document.getElementById('message').value;
    socket.emit('message', message);
}