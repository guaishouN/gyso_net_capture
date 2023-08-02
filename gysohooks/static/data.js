const baseItem = $('#base-item').clone().removeAttr('id').removeClass('d-none');
const cache = {};
const socketHostname = window.location.hostname;
const socketPort = 5000;
const socket = io.connect(`http://${socketHostname}:${socketPort}`);

let current_uid = ''

class Capture {
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
    $('.navtab li').on('click', function () {
        if ($(this).hasClass('selected')) {
            return;
        }
        const url = $(this).attr('data-href');
        if (url) {
            window.location.href = url;
        }
    });
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
    cache[snap.uid] = new Capture(snap.uid, snap, null, null);
    if (current_uid === '') {
        current_uid = snap.uid;
        setTimeout(function () {
            getCaptureDetail(current_uid);
        }, 4000);
    }
}

function getCaptureDetail(uid) {
    let capture = cache[uid];
    if (capture.request != null) {
        console.log(capture);
        parseDetail(capture);
        return;
    }
    $('#capture-detail').show();
    $("#capture-detail-blank").hide();
    $.ajax({
        url: "/captureDetail/" + uid,
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
    const code = captureDetail.code;
    const request = captureDetail.request;
    const response = captureDetail.response;
    const request_info = {
        'url': request.url,
        'method': request.method,
        'headers': formatJSONToHTML(request.headers),
        'content': request.content,
        'timestamp': new Date(parseInt(request.timestamp)).toLocaleString().replace(/:\d{1,2}$/, ' '),
    }
    const response_info = {
        'status_code': response.status_code,
        'headers': formatJSONToHTML(response.headers),
        'content': response.content,
        'time_diff': response.time_diff,
    }
    const detail = $('#capture-detail');
    detail.find('#capture-request-url').html('<b> ' + request_info.method + '</b> <br>' + request_info.url);
    detail.find('#capture-request-header-detail').html(request_info.headers);
    detail.find('#capture-request-body-detail').text(request_info.content);

    detail.find('#capture-response-state').html('<b>' + response_info.status_code + '</b> <br>Time consume:  ' + response_info.time_diff + ' ms');
    detail.find('#capture-response-header-detail').html(response_info.headers);
    detail.find('#capture-response-body-detail').text(response_info.content);
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
    $.ajax({
        url: "/dumps_file",
        method: "GET",
        xhrFields: {
            responseType: "text"  // 告诉浏览器返回的数据类型为二进制流
        },
        success: function (data, status, xhr) {
            // 创建一个临时的URL来下载文件
            var blob = new Blob([data], {type: xhr.getResponseHeader("Content-Type")});
            var link = document.createElement("a");
            link.href = window.URL.createObjectURL(blob);
            link.download = "dumps.data";  // 下载的文件名
            link.click();
        },
        error: function (xhr, status, error) {
            console.error("Error downloading file:",status ,  error);
        }
    });
})


$('#stop-start-capture').click(() => {

})

function sendMessage() {
    let message = document.getElementById('message').value;
    socket.emit('message', message);
}