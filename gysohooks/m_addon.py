import json
from mitmproxy import ctx, http, dns

cache = {}


def get_capture_item(uid: str):
    if uid in cache:
        return cache[uid]
    else:
        return None


def get_capture_item_as_json(uid: str):
    if uid in cache:
        print(f'get uid={uid}')
        capture_detail: CaptureItem = cache[uid]
        result = {'uid': uid, 'code': 0, 'request': capture_detail.request, 'response': capture_detail.response}
        return json.dumps(result)
    else:
        print(f'get error uid={uid}')
        return json.dumps({
            'code': 1,
            'uid': uid,
            'snap': '',
            'request': '',
            'response': ''
        })


class SnapInfo:
    """
    simple info for list
    """

    def __init__(self, uid: str, method: str, pretty_url: str):
        self.uid = uid
        self.method = method
        self.pretty_url = pretty_url

    def to_json(self):
        return json.dumps({
            'type': 'snap',
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
    """
       Http and Https 拦截
    """

    def __init__(self, app_s, queue_s):
        self.app = app_s
        self.queue_m = queue_s

    def requestheaders(self, flow: http.HTTPFlow):
        s_info = SnapInfo(
            flow.id,
            flow.request.method,
            flow.request.pretty_url
        ).to_json()

        self.queue_m.put(s_info)
        pass

    def request(self, flow: http.HTTPFlow):
        request_time = flow.request.timestamp_start
        uid = flow.id
        try:
            content = flow.request.content.decode()
        except UnicodeDecodeError:
            content = "[(⊙o⊙)…， 这个数据抓包工具不能解析, 而不是没有request Body数据]"
            print("Failed request decoded!! UnicodeDecodeError")

        request_info = {
            'type': 'request',
            'uuid': uid,
            'url': flow.request.url,
            'method': flow.request.method,
            'headers': dict(flow.request.headers),
            'content': content,
            'timestamp': str(request_time),
        }
        item: CaptureItem = CaptureItem(uid)
        item.request = request_info
        cache[uid] = item

    def responseheaders(self, flow: http.HTTPFlow):
        pass

    def response(self, flow: http.HTTPFlow) -> None:
        request_time = flow.request.timestamp_start
        response_time = flow.response.timestamp_end
        time_diff = response_time - request_time
        uid = flow.id
        if uid not in cache:
            print("No request info found!!!")
            return
        item = cache[uid]
        try:
            content = flow.response.content.decode()
        except UnicodeDecodeError:
            content = "[(⊙o⊙)…， 这个数据抓包工具不能解析, 而不是没有response Body数据]"
            print("Failed request decoded!! UnicodeDecodeError")

        response_info = {
            'type': 'response',
            'uuid': uid,
            'url': flow.request.url,
            'status_code': flow.response.status_code,
            'headers': dict(flow.response.headers),
            'content': content,
            'timestamp': str(response_time),
            'time_diff': str(time_diff),
        }
        item.response = response_info
        # res_package = json.dumps(response_info)
        # self.queue_m.put(res_package)

    def error(self, flow: http.HTTPFlow):
        print(f"error  {flow}")
        pass

    def dns_request(self, flow: dns.DNSFlow):
        print(f"error dns_request {flow}")
        pass
