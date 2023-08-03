const baseItem = $('#base-item').clone().removeAttr('id').removeClass('d-none');
const cache = {};
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

    $.ajax({
        url: "/get_edit_list",
        method: "GET",
        dataType: "json",
        success: function (jsonList) {
            console.log(jsonList)
            for (let i = 0; i < jsonList.length; i++) {
                let snap = jsonList[i];
                snapInfo(snap);
            }
        },
        error: function (error) {
            console.error("Error fetching conversations:", error);
        },

    });
});


function snapInfo(snap) {
    console.log('Received response:', snap);
    $('#capture-list-blank-tip').hide();
    let netItem = baseItem.clone(true);
    netItem.find('#base-item-url').text(snap.pretty_url);
    netItem.find('#base-item-type').text(snap.method);
    netItem.attr('id', snap.uid);
    netItem.appendTo('#capture-list').show();
    console.log("before uid ", $(netItem).attr("id"), snap.uid)
    console.log("before url ", snap.pretty_url)
    netItem.click(() => {
        current_uid = $(netItem).attr("id");
        $('#capture-list').children().removeClass('selected');
        $(netItem).addClass('selected');
        console.log("after ", $(netItem).attr("id"))
        getCaptureDetail(snap.uid);
    });
    cache[snap.uid] = new Capture(snap.uid, snap, null, null);
    if (current_uid === '') {
        current_uid = snap.uid;
        setTimeout(function () {
            getCaptureDetail(current_uid);
        }, 10);
    }
}

function getCaptureDetail(uid) {
    let capture = cache[uid];
    if (capture.request != null) {
        console.log(capture);
        parseEditDetail(capture);
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
            parseEditDetail(captureDetail);
            parseDetailToEdit(captureDetail)
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

function parseEditDetail(captureDetail) {
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

function resetEditRequestInfo(request_info) {
    if (request_info === '') {
        return ''
    }
    const requestLine = `${request_info.method} ${request_info.path} ${request_info.http_version}`;
    // Format the query parameters
    const queryParams = new URLSearchParams(request_info.url.split('?')[1]);
    // Create the headers section
    let headers = `Host: ${request_info.host}\n`;

    for (const [header, value] of Object.entries(request_info.headers)) {
        if (header.toLowerCase() !== 'host') {
            headers += `${header}: ${value}\n`;
        }
    }

    let formattedRequest = `${requestLine}\n${headers}\n`;

    // Add the request body if present
    if (request_info.content) {
        formattedRequest += JSON.stringify(request_info.content, null, 2);
    }
    $('#edit-request-textarea').text(formattedRequest);
}

function resetEditResponseInfo(response_info) {
    if (response_info === '') {
        return ''
    }
    const responseLine = `${response_info.http_version} ${response_info.status_code} ${response_info.reason}`;
    let headers = ``;

    if (response_info.headers) {
        for (const [header, value] of Object.entries(response_info.headers)) {
            headers += `${header}: ${value}\n`;
        }
    }
    let formattedResponse = `${responseLine}\n${headers}\n`;
    $('#edit-response-textarea-header').text(formattedResponse);

    let formattedContent = "";
    if (response_info.content) {
        try {
            formattedContent = JSON.stringify(response_info.content, null, 2);
        } catch (err) {
            formattedContent = response_info.content;
        }
    }
    $('#edit-response-textarea-body').text(formattedContent);
}

function parseDetailToEdit(captureDetail) {
    const request_info = captureDetail.request;
    const response_info = captureDetail.response;
    resetEditRequestInfo(request_info);
    resetEditResponseInfo(response_info);
    $('#target-url').text(`${request_info.url}`);
}

$('#clear-data').click(() => {
    $('#capture-list').find('li').remove();
    $('#capture-list-blank-tip').show();
    // 发起AJAX请求上传文件
    $.ajax({
        url: "/clear/edit",
        method: "GET",
        dataType: 'text',
        processData: false,
        contentType: false,
        success: function (data) {
            console.log(data)
        },
        error: function (xhr, status, error) {
            console.error("Error clear:", error);
        }
    });
})

$('#import-data').click(() => {
    const fileInput = $("#history-file-input")[0];
    const file = fileInput.files[0];

    if (!file) {
        alert("请选择一个历史数据作为基础修改数据");
        return;
    }

    var formData = new FormData();
    formData.append("file", file);

    // 发起AJAX请求上传文件
    $.ajax({
        url: "/upload_history_file",
        method: "POST",
        data: formData,
        processData: false,
        contentType: false,
        success: function (data) {
            console.log(data)
            $('#capture-list').find('li').remove();
            $.ajax({
                url: "/get_edit_list",
                method: "GET",
                dataType: "json",
                success: function (jsonList) {
                    console.log(jsonList)
                    if (jsonList.length === 0) {
                        $('#capture-list-blank-tip').show();
                    } else {
                        for (let i = 0; i < jsonList.length; i++) {
                            let snap = jsonList[i];
                            snapInfo(snap);
                        }
                    }
                },
                error: function (error) {
                    console.error("Error fetching conversations:", error);
                },

            });
        },
        error: function (xhr, status, error) {
            console.error("Error uploading file:", error);
        }
    });
})

$('#stop-start-capture').click(() => {

})

function sendMessage() {
    let message = document.getElementById('message').value;
    socket.emit('message', message);
}