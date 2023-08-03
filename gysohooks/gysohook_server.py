import asyncio
import json
import queue
from concurrent.futures import ThreadPoolExecutor

import mitmproxy
from gysohooks import io_addon, m_addon
from mitmproxy import options, ctx
from mitmproxy.tools.dump import DumpMaster
from flask import Flask, render_template, request, send_file, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS, cross_origin
from m_addon import GysoAddon, get_capture_item_as_json, SnapInfo, get_current_capture_list, update_modify, ModifyCache
from io_addon import GysoHooksIO, FLOW_CACHE

app = Flask(__name__)
queue_m = queue.Queue()
exit_event = asyncio.Event()
socketio = SocketIO(app, cors_allowed_origins="*")
cors = CORS(app)
gysoio_addon: GysoHooksIO = ...


@app.route("/", methods=("GET", "POST"))
@cross_origin()  # 允许跨源访问该路由
def index():
    return render_template("data.html")


@app.route("/edit", methods=("GET", "POST"))
@cross_origin()  # 允许跨源访问该路由
def edit():
    return render_template("edit_data.html")


@app.route("/settings", methods=("GET", "POST"))
@cross_origin()
def connect():
    return render_template("settings.html")


@app.route("/captureDetail/<uid>", methods=['GET'])
def capture_detail(uid):
    return get_capture_item_as_json(uid)


@app.route("/dumps_file")
def save_dumps_file():
    if gysoio_addon is not None:
        gysoio_addon.dumps_as_to_file()
    return send_file(io_addon.dumps_file_name, mimetype='text/plain', as_attachment=True)


@app.route("/upload_history_file", methods=["POST"])
def load_dumps_file():
    if "file" not in request.files:
        return "No file part", 400

    file = request.files["file"]
    if file.filename == "":
        return "No selected file", 400

    # 保存上传的文件到指定路径
    file.save(io_addon.history_file_name)
    return "File uploaded successfully", 200


@app.route("/get_edit_list", methods=["GET"])
def get_edit_list():
    if gysoio_addon is not None:
        gysoio_addon.load_history_file()

    snap_list = []
    ab = GysoAddon()
    for flow in FLOW_CACHE:
        s = SnapInfo(flow.id, flow.request.method, flow.request.pretty_url)
        m_addon.add_cache(ab, flow)
        snap_list.append(s.to_dict())
    return json.dumps(snap_list)


@app.route("/get_current_list", methods=["GET"])
def get_current_list():
    return get_current_capture_list()


@app.route("/apply_modify/<modify_type>", methods=["GET"])
def set_apply_modify(modify_type: str):
    print(f'apply_modify {modify_type}')
    if modify_type == 'true':
        m_addon.apply_modify = True
    else:
        m_addon.apply_modify = False
    return 'done'


@app.route("/set_modify_data", methods=["POST"])
def set_modify_data():
    data = request.form
    modify_data = ModifyCache()
    modify_data.url = data["url"]
    modify_data.requests_data = data["requestTextarea"]
    modify_data.response_header = data["responseHeaderTextarea"]
    modify_data.response_body = data["responseBodyTextarea"]
    update_modify(modify_data)
    return 'set_modify_data done!'


@socketio.on('connect')
def handle_connect():
    print('Client connected')


@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')


@socketio.on('message')
def handle_message(data):
    # 处理收到的消息
    print('Received message:', data)
    # 在这里根据需要，将消息推送给其他客户端

    # 发送响应消息给发送方客户端
    socketio.emit('response', 'Message received')


async def run_mitmdump():
    # 创建 mitmproxy 的选项对象
    mitm_options = options.Options(ssl_insecure=True)

    # 创建 mitmproxy 的主控制器对象
    mitm_master = DumpMaster(mitm_options)

    # 创建 Addon 实例并传递队列
    addon = GysoAddon(app, queue_m)
    global gysoio_addon
    gysoio_addon = GysoHooksIO()

    mitm_master.addons.add(addon)
    mitm_master.addons.add(gysoio_addon)

    # 启动 mitmproxy
    await mitm_master.run()


def run_flask():
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)


def run_mitm_app():
    # 在子线程中运行 mitm 应用
    loop_m = asyncio.get_event_loop()
    loop_m.run_until_complete(run_mitmdump())


def flask_queue_emit():
    print("flask_queue_emit begin running")
    while True:
        package = queue_m.get()
        # print("flask_queue_emit  --- queue data", str(package))
        socketio.emit('response', str(package))
        queue_m.task_done()


def start_server():
    # 创建线程池
    executor = ThreadPoolExecutor(max_workers=3)

    # 在线程池中运行 Flask
    flask_future = executor.submit(run_flask)

    # Queue process
    queue_future = executor.submit(flask_queue_emit)

    # 在线程池中运行 mitmproxy
    mitmdump_future = executor.submit(asyncio.run, run_mitmdump())

    # 创建事件循环
    loop = asyncio.get_event_loop()
    try:
        # 运行事件循环
        loop.run_forever()
    finally:
        # 取消 mitmproxy 和 Flask 任务
        mitmdump_future.cancel()
        flask_future.cancel()
        queue_future.cancel()

        # 关闭事件循环
        loop.close()
        mitmproxy.ctx.master.shutdown()
        # 关闭线程池
        executor.shutdown(wait=False)


if __name__ == '__main__':
    start_server()
