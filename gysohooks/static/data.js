const baseItem = $('#base-item').clone().removeAttr('id').removeClass('d-none');
const cache = {};
const socket = io.connect('http://127.0.0.1:5000');
let current_uid = ''

class Capture{
    constructor(uid, snap, request, response) {
        this.uid = uid;
        this.snap = snap;
        this.request = request;
        this.response = response;
    }
}
$(document).ready(function () {
    //baseItem.appendTo('#capture-list').show();
    $('#capture-detail').hide();
});

socket.on('connect', function () {
    console.log('Connected to server');
});

socket.on('response', function (data) {
    let capture = JSON.parse(data);
    switch (capture.type) {
        case 'snap':
            snapInfo(capture);
            break;
        case 'request':
            requestInfo(capture);
            break;
        case 'response':
            responseInfo(capture);
            break;
        default:
            console.log("none type");
    }
});


function snapInfo(snap) {
    console.log('Received response:', snap);
    $('#capture-list-blank-tip').hide();
    let netItem = baseItem.clone(true);
    netItem.find('#base-item-url').text(snap.pretty_url);
    netItem.find('#base-item-type').text(snap.method);
    netItem.attr('id', snap.uid);
    netItem.appendTo('#capture-list').show();
    netItem.click(() => {
        current_uid = $(netItem).attr("id");
        $('#capture-list').children().removeClass('selected');
        $(netItem).addClass('selected');
        console.log($(netItem).attr("id"))
        getCaptureDetail(snap.uid);
    });
    cache[snap.uid] = new Capture(snap.uid,snap,null,null);
    if(current_uid === ''){
        current_uid = snap.uid;
        setTimeout(function (){
            getCaptureDetail(current_uid);
        }, 4000);
    }
}

function getCaptureDetail(uid) {
    let capture = cache[uid];
    if (capture.request != null){
        console.log(capture);
        parseDetail(capture);
        return;
    }
    $('#capture-detail').show();
    $("#capture-detail-blank").hide();
    $.ajax({
        url: "/captureDetail/"+uid,
        method: "GET",
        dataType: "json",
        success: function (captureDetail) {
            console.log(captureDetail);
            parseDetail(captureDetail);
        },
        error: function (error) {
            console.error("Error fetching conversations:", error);
        },
    });
}

function formatJSONToHTML(obj, indent = 0) {
  let output = '';
  const indentString = '&nbsp;&nbsp;'.repeat(indent); // 使用两个空格作为缩进
  for (let key in obj) {
    if (typeof obj[key] === 'object' && obj[key] !== null) {
      output += `${indentString}${key}:<br>${formatJSONToHTML(obj[key], indent + 1)}`;
    } else {
      output += `${indentString}${key}: ${obj[key]}<br>`;
    }
  }
  return output;
}

function parseDetail(captureDetail) {
    const format = formatJSONToHTML(captureDetail);
    $("#capture-detail").html(format);
}


function requestInfo(request) {
    let captureCache = cache[request.uid];
    captureCache.request = request;
    console.log("requestInfo:", captureCache)
}

function responseInfo(response) {
    let captureCache = cache[response.uid];
    captureCache.response = response;
    console.log("responseInfo:", captureCache)
}

$('#clear-data').click(() => {
    $('#capture-list').find('li').remove();
    $('#capture-list-blank-tip').show();
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