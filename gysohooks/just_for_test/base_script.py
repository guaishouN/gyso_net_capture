import asyncio
from concurrent.futures import ThreadPoolExecutor
from mitmproxy import proxy, options, exceptions
from mitmproxy.tools.dump import DumpMaster
import aiohttp
from flask import Flask, redirect, render_template, request, url_for, Markup
import signal

app = Flask(__name__)
queue = asyncio.Queue()
exit_event = asyncio.Event()


class Addon:
    def __init__(self, app_s, queue_s):
        self.app = app_s
        self.queue = queue_s

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
                await self.queue.put((flow.request, status, headers, content))


@app.route("/", methods=("GET", "POST"))
def index():
    return render_template("data.html")


@app.route('/data')
def data():
    results = []
    while not queue.empty():
        results.append(Markup.escape(queue.get_nowait()))
    return str(results)


async def run_mitmdump():
    # 创建 mitmproxy 的选项对象
    mitm_options = options.Options()

    # 创建 mitmproxy 的主控制器对象
    mitm_master = DumpMaster(mitm_options)

    # 创建 Addon 实例并传递队列
    addon = Addon(app, queue)
    mitm_master.addons.add(addon)

    # 启动 mitmproxy
    await mitm_master.run()


def run_flask():
    app.run()


def run_mitm_app():
    # 在子线程中运行 mitm 应用
    loop_m = asyncio.get_event_loop()
    loop_m.run_until_complete(run_mitmdump())


async def shutdown():
    await asyncio.sleep(0.1)
    exit_event.set()


if __name__ == '__main__':
    # 创建线程池
    executor = ThreadPoolExecutor(max_workers=2)

    # 在线程池中运行 mitmproxy
    mitmdump_future = executor.submit(asyncio.run, run_mitmdump())

    # 在线程池中运行 Flask
    flask_future = executor.submit(run_flask)

    # 注册退出事件处理函数
    signal.signal(signal.SIGINT, lambda signum, frame: asyncio.ensure_future(shutdown()))

    # 创建事件循环
    loop = asyncio.get_event_loop()

    try:
        # 运行事件循环
        loop.run_until_complete(exit_event.wait())
    finally:
        # 取消 mitmproxy 和 Flask 任务
        mitmdump_future.cancel()
        flask_future.cancel()

        # 关闭事件循环
        loop.close()

        # 关闭线程池
        executor.shutdown(wait=False)
