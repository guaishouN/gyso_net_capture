import asyncio
import queue
from concurrent.futures import ThreadPoolExecutor
from mitmproxy import proxy, options, exceptions
from mitmproxy.tools.dump import DumpMaster
from flask import Flask, redirect, render_template, request, url_for, Markup, escape
from flask_socketio import SocketIO
from flask_cors import CORS, cross_origin
from m_addon import GysoAddon, get_capture_item_as_json

app = Flask(__name__)
queue_m = queue.Queue()
exit_event = asyncio.Event()
socketio = SocketIO(app, cors_allowed_origins="*")
cors = CORS(app)


@app.route("/", methods=("GET", "POST"))
@cross_origin()  # 允许跨源访问该路由
def index():
    return render_template("data.html")


@app.route("/connect", methods=("GET", "POST"))
@cross_origin()
def connect():
    return render_template("connect.html")


@app.route("/captureDetail/<uid>", methods=['GET'])
def capture_detail(uid):
    return get_capture_item_as_json(uid)


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
    mitm_options = options.Options()

    # 创建 mitmproxy 的主控制器对象
    mitm_master = DumpMaster(mitm_options)

    # 创建 Addon 实例并传递队列
    addon = GysoAddon(app, queue_m)
    mitm_master.addons.add(addon)

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
        print("flask_queue_emit  --- queue data", str(package))
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

        # 关闭线程池
        executor.shutdown(wait=False)


if __name__ == '__main__':
    start_server()

