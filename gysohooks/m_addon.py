import json
import uuid

from mitmproxy import ctx, http

uuid_dict = {}
cache = {}


def get_capture_item(uid: str):
    if uid in cache:
        return cache[uid]
    else:
        return None


class SimpleInfo:
    """
    simple info for list
    """

    def __init__(self, uid: str, method: str, pretty_url: str):
        self.uid = uid
        self.method = method
        self.pretty_url = pretty_url

    def to_json(self):
        return json.dumps({
            'uid': self.uid,
            'method': self.method,
            'pretty_url': self.pretty_url
        })


class CaptureItem:
    """
    full  info for detail
    """
    request: dict = ...
    response: dict = ...

    def __init__(self, uid: str):
        self.uid = uid

    def __str__(self):
        return self.uid


class GysoAddon:
    def __init__(self, app_s, queue_s):
        self.app = app_s
        self.queue_m = queue_s

    def request(self, flow: http.HTTPFlow):
        request_time = flow.request.timestamp_start
        random_uuid = str(uuid.uuid4())
        request_info = {
            'uuid': random_uuid,
            'type': 'request',
            'url': flow.request.url,
            'method': flow.request.method,
            'headers': dict(flow.request.headers),
            'content': flow.request.content.decode(),
            'raw': flow.request.get_text(),
            'timestamp': str(request_time),
        }
        uuid_dict[str(request_time)] = random_uuid
        item: CaptureItem = CaptureItem(random_uuid)
        item.request = request_info
        cache[random_uuid] = item

        s_info = SimpleInfo(
            random_uuid,
            flow.request.method,
            flow.request.pretty_url
        ).to_json()

        self.queue_m.put(s_info)


    def response(self, flow: http.HTTPFlow) -> None:
        request_time = flow.request.timestamp_start
        response_time = flow.response.timestamp_end
        time_diff = response_time - request_time
        uid = uuid_dict[str(request_time)]
        if uid not in cache:
            print("No request info found!!!")
            return
        item = cache[uid]

        response_info = {
            'uuid': uid,
            'type': 'response',
            'url': flow.request.url,
            'status_code': flow.response.status_code,
            'headers': dict(flow.response.headers),
            'content': flow.response.content.decode(),
            'timestamp': str(response_time),
            'raw': flow.response.get_text(),
            'time_diff': str(time_diff),
        }
        item.response = response_info
        # res_package = json.dumps(response_info)
        # self.queue_m.put(res_package)
