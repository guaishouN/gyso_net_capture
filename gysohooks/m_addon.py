import json
from mitmproxy import ctx, http
from datetime import datetime
import aiohttp


class GysoAddon:
    def __init__(self, app_s, queue_s):
        self.app = app_s
        self.queue_m = queue_s
        self.data = []

    def response(self, flow: http.HTTPFlow) -> None:
        request_time = flow.request.timestamp_start
        response_time = flow.response.timestamp_end
        time_diff = response_time - request_time

        request_info = {
            'url': flow.request.url,
            'method': flow.request.method,
            'headers': dict(flow.request.headers),
            'content': flow.request.content.decode(),
            'raw': flow.request.get_text(),
            'timestamp': str(request_time),
        }

        response_info = {
            'status_code': flow.response.status_code,
            'headers': dict(flow.response.headers),
            'content': flow.response.content.decode(),
            'timestamp': str(response_time),
            'raw': flow.response.get_text(),
            'time_diff': str(time_diff),
        }

        self.data = {
            'request': request_info,
            'response': response_info
        }
        req_package = json.dumps(self.data, indent=2)
        self.queue_m.put(req_package)

    def done(self):
        print("done**********************************************")
