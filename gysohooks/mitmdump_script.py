import asyncio

from flask import Flask

from mitmproxy import proxy, options, exceptions
from mitmproxy.tools.dump import DumpMaster
import aiohttp


class Addon:
    def __init__(self, app):
        self.app = app

    async def request(self, flow):
        async with aiohttp.ClientSession() as session:
            async with session.request(
                    method=flow.request.method,
                    url=flow.request.url,
                    headers=flow.request.headers,
                    data="hello gyson!!!"
            ) as response:
                status = response.status
                headers = response.headers
                content = await response.read()

                # 将结果发送到 Flask 应用
                await self.app.queue.put((flow.request, status, headers, content))


async def run_mitmdump():
    # 创建 mitmproxy 的选项对象
    mitm_options = options.Options()

    # 创建 mitmproxy 的主控制器对象
    mitm_master = DumpMaster(mitm_options)

    # 创建 Flask 应用并传递给 Addon 类
    app = Flask(__name__)
    addon = Addon(app)
    mitm_master.addons.add(addon)

    # 启动 mitmproxy
    await mitm_master.run()


if __name__ == '__main__':
    asyncio.run(run_mitmdump())
