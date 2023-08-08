import asyncio
import queue
from concurrent.futures import ThreadPoolExecutor
import mitmproxy
from mitmproxy import options, ctx
from mitmproxy.tools.dump import DumpMaster
from flask import Flask, render_template, request, send_file
from flask_socketio import SocketIO
from flask_cors import CORS, cross_origin
from current_addon import GysoHookAddon, get_capture_item_as_json, get_current_capture_list
from modify_addon import update_modify, ModifyCache, GysoModifyAddon, get_modify_detail
from history_addon import get_history_detail_as_json, save_upload_file, get_history_list
from dumps_addon import GysoHooksDumpsAddOn, dumps_file_name

app = Flask(__name__)
queue_m = queue.Queue()
exit_event = asyncio.Event()
socketio = SocketIO(app, cors_allowed_origins="*")
cors = CORS(app)
gyso_io_addon_obj: GysoHooksDumpsAddOn = ...
current_hook_addon_obj: GysoHookAddon = ...
modify_addon_obj:  GysoModifyAddon = ...


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


@app.route("/history_detail/<uid>", methods=['GET'])
def history_detail(uid):
    return get_history_detail_as_json(uid)


@app.route("/dumps_file")
def save_dumps_file():
    if gyso_io_addon_obj is not None:
        gyso_io_addon_obj.dumps_as_file_to_client()
    return send_file(dumps_file_name, mimetype='text/plain', as_attachment=True)


@app.route("/upload_history_file", methods=["POST"])
def upload_history_file():
    if "file" not in request.files:
        return "No file part", 400

    file = request.files["file"]
    if file.filename == "":
        return "No selected file", 400
    save_upload_file(file)
    return "File uploaded successfully", 200


@app.route("/get_history_list", methods=["GET"])
def get_history_dumps_list():
    return get_history_list()


@app.route("/get_current_list", methods=["GET"])
def get_current_list():
    return get_current_capture_list()


@app.route("/set_modify_apply/<modify_type>", methods=["GET"])
def set_apply_modify(modify_type: str):
    print(f'apply_modify {modify_type}')
    if modify_addon_obj is not None:
        modify_addon_obj.apply_modify = (modify_type == 'true')
    return f'apply_modify set [{modify_addon_obj.apply_modify}]'


@app.route("/get_modify_apply", methods=["GET"])
def get_apply_modify():
    print(f'get_modify_apply[{modify_addon_obj.apply_modify}]')
    return f'{modify_addon_obj.apply_modify}'


@app.route("/set_modify_data", methods=["POST"])
def set_modify_data():
    data = request.form
    modify_data = ModifyCache()
    modify_data.url = data["url"]
    modify_data.uid = data["uid"]
    modify_data.requests_data = data["requestTextarea"]
    modify_data.response_header = data["responseHeaderTextarea"]
    modify_data.response_body = data["responseBodyTextarea"]
    update_modify(modify_data)
    return 'set_modify_data done!'


@app.route("/get_modify_data/<uid>", methods=["GET"])
def get_modify_data(uid):
    return get_modify_detail(uid)


@socketio.on('connect')
def handle_connect():
    print('Client connected')


@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')


@socketio.on('message')
def handle_message(data):
    print('Received message:', data)
    socketio.emit('response', 'Message received')


async def run_mitmdump():
    mitm_options = options.Options(ssl_insecure=True)
    mitm_master = DumpMaster(mitm_options)
    global gyso_io_addon_obj, current_hook_addon_obj, modify_addon_obj

    modify_addon_obj = GysoModifyAddon()
    current_hook_addon_obj = GysoHookAddon(app, queue_m)
    gyso_io_addon_obj = GysoHooksDumpsAddOn()

    mitm_master.addons.add(modify_addon_obj)
    mitm_master.addons.add(current_hook_addon_obj)
    mitm_master.addons.add(gyso_io_addon_obj)

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
