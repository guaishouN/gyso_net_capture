import asyncio
import queue
from concurrent.futures import ThreadPoolExecutor
from mitmproxy import proxy, options, exceptions
from mitmproxy.tools.dump import DumpMaster
import aiohttp
from flask import Flask, redirect, render_template, request, url_for, Markup
from flask_socketio import SocketIO
from flask_cors import CORS, cross_origin
import signal

app = Flask(__name__)
queue_m = queue.Queue()
exit_event = asyncio.Event()
socketio = SocketIO(app, cors_allowed_origins="*")
cors = CORS(app)


class Addon:
    def __init__(self, app_s, queue_s):
        self.app = app_s
        self.queue_m = queue_s

    async def request(self, flow):
        async with aiohttp.ClientSession() as session:
            async with session.request(
                    method=flow.request.method,
                    url=flow.request.url,
                    headers=flow.request.headers,
                    # data=await flow.request.content.read()
            ) as response:
                status = response.status
                headers = response.headers
                content = await response.read()

                # 将结果发送到 Flask 应用
                self.queue_m.put((flow.request, status, headers, content))


@app.route("/", methods=("GET", "POST"))
@cross_origin()  # 允许跨源访问该路由
def index():
    return render_template("data.html")


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
    addon = Addon(app, queue_m)
    mitm_master.addons.add(addon)

    # 启动 mitmproxy
    await mitm_master.run()


def run_flask():
    socketio.run(app, allow_unsafe_werkzeug=True)


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
        print("flask_queue_emit  #########")


if __name__ == '__main__':
    # 创建线程池
    executor = ThreadPoolExecutor(max_workers=2)

    # 在线程池中运行 mitmproxy
    mitmdump_future = executor.submit(asyncio.run, run_mitmdump())

    # 在线程池中运行 Flask
    flask_future = executor.submit(run_flask)

    # Queue process
    queue_future = executor.submit(flask_queue_emit())

    # 创建事件循环
    loop = asyncio.get_event_loop()
    try:
        # 运行事件循环
        loop.run_forever()
    finally:
        # 取消 mitmproxy 和 Flask 任务
        mitmdump_future.cancel()
        flask_future.cancel()

        # 关闭事件循环
        loop.close()

        # 关闭线程池
        executor.shutdown(wait=False)
