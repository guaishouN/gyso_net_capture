import json
import uuid

from mitmproxy import ctx, http


uuid_dict = {}


class GysoAddon:
    def __init__(self, app_s, queue_s):
        self.app = app_s
        self.queue_m = queue_s

    def request(self, flow: http.HTTPFlow):
        request_time = flow.request.timestamp_start
        random_uuid = uuid.uuid4()
        request_info = {
            'type': 'request',
            'url': flow.request.url,
            'method': flow.request.method,
            'headers': dict(flow.request.headers),
            'content': flow.request.content.decode(),
            'raw': flow.request.get_text(),
            'timestamp': str(request_time),
        }
        uuid_dict[str(request_time)] = random_uuid
        req_package = json.dumps(request_info)
        self.queue_m.put(req_package)

    def response(self, flow: http.HTTPFlow) -> None:
        request_time = flow.request.timestamp_start
        response_time = flow.response.timestamp_end
        time_diff = response_time - request_time

        response_info = {
            'type': 'response',
            'url': flow.request.url,
            'status_code': flow.response.status_code,
            'headers': dict(flow.response.headers),
            'content': flow.response.content.decode(),
            'timestamp': str(response_time),
            'raw': flow.response.get_text(),
            'time_diff': str(time_diff),
        }

        res_package = json.dumps(response_info)
        self.queue_m.put(res_package)
