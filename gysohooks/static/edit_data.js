const baseItem = $('#base-item').clone().removeAttr('id').removeClass('d-none');
const cache = {};
let current_uid = ''
let current_capture_detail = ''

const modify_cache = {
    url: '',
    uid: '',
    requests_data: '',
    response_header: '',
    response_body: ''
}

const requestArea = $("#edit-request-textarea");
const responseHeaderArea = $("#edit-response-textarea-header");
const responseBodyArea = $("#edit-response-textarea-body");

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
        url: "/get_history_list",
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

    $.ajax({
        url: "/get_modify_apply",
        method: "GET",
        success: function (isSelected) {
            console.log("get_modify_apply["+isSelected+"]")
            const bt = $('#stop-start-apply');
            bt.attr('aria-selected', (isSelected === 'true' || isSelected === 'True')? 'true' : 'false');
            if (isSelected === 'true' || isSelected === 'True') {
                bt.addClass('btn-danger');
            } else {
                bt.removeClass('btn-danger');
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
    netItem.on('click', () => {
        current_uid = $(netItem).attr("id");
        $('#capture-list').children().removeClass('selected');
        $(netItem).addClass('selected');
        console.log("after ", $(netItem).attr("id"))
        getHistoryDetail(snap.uid);
    });
    cache[snap.uid] = new Capture(snap.uid, snap, null, null);
    if (current_uid === '') {
        current_uid = snap.uid;
        setTimeout(function () {
            getHistoryDetail(current_uid);
        }, 10);
    }
}

function getHistoryDetail(uid) {
    function setUI(captureDetail) {
        current_capture_detail = captureDetail;
        console.log("edit setUI " + captureDetail);
        parseHistoryDetail(captureDetail);
        parseDetailToEdit(captureDetail);
        getModifyDetail(uid);
        cache[uid] = captureDetail;
    }

    let capture = cache[uid];
    if (capture.request != null) {
        console.log(capture);
        setUI(capture);
        return;
    }
    $('#capture-detail').show();
    $("#capture-detail-blank").hide();
    $.ajax({
        url: "/history_detail/" + uid,
        method: "GET",
        dataType: "json",
        success: function (captureDetail) {
            setUI(captureDetail);
        },
        error: function (error) {
            console.error("Error fetching conversations:", error);
        },
    });
}

function getModifyDetail(uid) {
    $.ajax({
        url: `/get_modify_data/${uid}`,
        method: "GET",
        dataType: "json",
        success: function (modifyDetail) {
            console.log(modifyDetail);
            if (modifyDetail.requests_data !== '') {
                requestArea.val(modifyDetail.requests_data);
                modifyRequestBt.attr('aria-selected', 'true');
                modifyRequestBt.addClass('btn-danger');
            } else {
                modifyRequestBt.attr('aria-selected', 'false');
                modifyRequestBt.removeClass('btn-danger');
            }

            if (modifyDetail.response_header !== '') {
                responseHeaderArea.val(modifyDetail.response_header);
                modifyResponseHeaderBt.attr('aria-selected', 'true');
                modifyResponseHeaderBt.addClass('btn-danger');
            } else {
                modifyResponseHeaderBt.attr('aria-selected', 'false');
                modifyResponseHeaderBt.removeClass('btn-danger');
            }

            if (modifyDetail.response_body !== '') {
                responseBodyArea.val(modifyDetail.response_body);
                modifyResponseBodyBt.attr('aria-selected', 'true');
                modifyResponseBodyBt.addClass('btn-danger');
            } else {
                modifyResponseBodyBt.attr('aria-selected', 'false');
                modifyResponseBodyBt.removeClass('btn-danger');
            }
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


function parseHistoryDetail(captureDetail) {
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

    formattedRequest += request_info.content;
    requestArea.val(formattedRequest);
    modify_cache.requests_data = formattedRequest;
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
    responseHeaderArea.val(formattedResponse);
    modify_cache.response_header = formattedResponse;


    let formattedContent = "";
    if (response_info.content) {
        try {
            formattedContent = response_info.content;
        } catch (err) {
            formattedContent = response_info.content;
        }
    }
    responseBodyArea.val(formattedContent);
    modify_cache.response_body = formattedContent;
}


function parseDetailToEdit(captureDetail) {
    const request_info = captureDetail.request;
    const response_info = captureDetail.response;
    resetEditRequestInfo(request_info);
    resetEditResponseInfo(response_info);
    $('#target-url').text(`${request_info.url}`);
}

$('#clear-data').on('click', () => {
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


$('#import-data').on('click', () => {
    const fileInput = $("#history-file-input")[0];
    const file = fileInput.files[0];

    if (!file) {
        alert("请选择一个历史数据作为基础修改数据");
        return;
    }

    const formData = new FormData();
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
                url: "/get_history_list",
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

$('#stop-start-apply').on('click', () => {
    const bt = $('#stop-start-apply');
    const isSelected = bt.attr('aria-selected');
    console.log(isSelected)
    bt.attr('aria-selected', isSelected === 'true' ? 'false' : 'true');
    if (isSelected === 'true') {
        bt.removeClass('btn-danger');
    } else {
        bt.addClass('btn-danger');
    }
    $.ajax({
        url: "/set_modify_apply/" + bt.attr('aria-selected'),
        method: "GET",
        dataType: "text",
        success: function (result) {
            console.log("set_modify_apply " + result)
        },
        error: function (error) {
            console.error("apply_modify error:", error);
        },
    });
})

const modifyRequestBt = $('#modify-request');
modifyRequestBt.on('click', () => {
    const isSelected = modifyRequestBt.attr('aria-selected');
    console.log(isSelected)
    modifyRequestBt.attr('aria-selected', isSelected === 'true' ? 'false' : 'true');
    if (isSelected === 'true') {
        modifyRequestBt.removeClass('btn-danger');
    } else {
        modifyRequestBt.addClass('btn-danger');
    }
    setModifyData();
});


const modifyResponseHeaderBt = $('#modify-response-header');
modifyResponseHeaderBt.on('click', () => {
    const isSelected = modifyResponseHeaderBt.attr('aria-selected');
    console.log(isSelected)
    modifyResponseHeaderBt.attr('aria-selected', isSelected === 'true' ? 'false' : 'true');
    if (isSelected === 'true') {
        modifyResponseHeaderBt.removeClass('btn-danger');
    } else {
        modifyResponseHeaderBt.addClass('btn-danger');
    }
    setModifyData();
});

const modifyResponseBodyBt = $('#modify-response-body');
modifyResponseBodyBt.on('click', () => {
    const isSelected = modifyResponseBodyBt.attr('aria-selected');
    modifyResponseBodyBt.attr('aria-selected', isSelected === 'true' ? 'false' : 'true');
    if (isSelected === 'true') {
        modifyResponseBodyBt.removeClass('btn-danger');
    } else {
        modifyResponseBodyBt.addClass('btn-danger');
    }
    setModifyData();
});

function setModifyData() {
    const isRequestSelected = modifyRequestBt.attr('aria-selected');
    const isResponseHeaderSelected = modifyResponseHeaderBt.attr('aria-selected');
    const isResponseBodySelected = modifyResponseBodyBt.attr('aria-selected');

    const data = {
        uid: current_uid,
        url: $('#target-url').text(),
        requestTextarea: isRequestSelected === 'true' ? requestArea.val() : '',
        responseHeaderTextarea: isResponseHeaderSelected === 'true' ? responseHeaderArea.val() : '',
        responseBodyTextarea: isResponseBodySelected === 'true' ? responseBodyArea.val() : ''
    };

    if (isRequestSelected !== 'true') {
        requestArea.val(modify_cache.requests_data)
    }

    if (isResponseHeaderSelected !== 'true') {
        responseHeaderArea.val(modify_cache.response_header)
    }

    if (isResponseBodySelected !== 'true') {
        responseBodyArea.val(modify_cache.response_body)
    }

    $.ajax({
        url: "/set_modify_data",  // Flask 服务器端路由
        method: "POST",
        data: data,
        success: function (response) {
            console.log("Data sent successfully.");
        },
        error: function (xhr, status, error) {
            console.error("Error sending data:", error);
        }
    });
}
