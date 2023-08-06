import os
from typing import BinaryIO
from mitmproxy import io, http


folder_path = "./data"
dumps_file_name = folder_path + "/dumps.data"


def checkout_data_dir():
    # 创建文件夹
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # 创建文件
    if not os.path.exists(dumps_file_name):
        with open(dumps_file_name, "w+") as f:
            # 可以在这里写入文件内容，如果需要的话
            pass


checkout_data_dir()


class GysoHooksDumpsAddOn:
    flow_cache = set[http.HTTPFlow]()

    def __init__(self) -> None:
        self.f: BinaryIO = open(dumps_file_name, "wb")
        self.w = io.FlowWriter(self.f)

    def response(self, flow: http.HTTPFlow) -> None:
        self.flow_cache.add(flow)

    def dumps_as_file_to_client(self):
        for flow in self.flow_cache:
            self.w.add(flow)

    def clear_cache(self):
        self.flow_cache.clear()

    def done(self):
        self.flow_cache.clear()
        self.f.close()