import json
from mitmproxy import ctx, http, dns

CACHE = {}


def get_capture_item(uid: str):
    if uid in CACHE:
        return CACHE[uid]
    else:
        return None


def get_capture_item_as_json(uid: str):
    if uid in CACHE:
        sdf: str = ""
        try:
            print(f'get uid={uid}')
            capture_detail: CaptureItem = CACHE[uid]
            response = capture_detail.response if capture_detail.response is not None else ""
            result = {'uid': uid,
                      'code': 0,
                      'request': capture_detail.request,
                      'response': response,
                      'error_msg': capture_detail.error_msg}
            sdf = json.dumps(result)

        except Exception as e:
            print(str(e))
        finally:
            return sdf
    else:
        print(f'get error uid={uid}')
        return json.dumps({
            'code': 1,
            'uid': uid,
            'snap': '',
            'request': '',
            'response': '',
            'error_msg': ''
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
    response: dict = None
    error_msg: str = ""

    def __init__(self, uid: str):
        self.uid = uid

    def __str__(self):
        return self.uid


def ensure_cache(flow: http.HTTPFlow):
    uid = flow.id
    if uid not in CACHE:
        item: CaptureItem = CaptureItem(uid)
        CACHE[uid] = item


class GysoAddon:
    """
       Http and Https 拦截
    """

    def __init__(self, app_s, queue_s):
        self.app = app_s
        self.queue_m = queue_s

    def check_emit_flow(self, flow):
        ensure_cache(flow)
        if flow is not None:
            s_info = SnapInfo(
                flow.id,
                flow.request.method,
                flow.request.pretty_url
            ).to_json()
            self.queue_m.put(s_info)
            request_info = {
                'type': 'request',
                'uuid': flow.id,
                'url': flow.request.url,
                'http_version': flow.request.http_version,
                'headers': dict(flow.request.headers),
                'content': "",
                'timestamp_start': flow.request.timestamp_start,
                'timestamp_end': flow.request.timestamp_end,
                'host': flow.request.host,
                'port': flow.request.port,
                'method': flow.request.method,
                'scheme': flow.request.scheme,
                'authority': flow.request.authority,
                'path': flow.request.path,
            }
            item = CACHE[flow.id]
            item.request = request_info

    def http_connect(self, flow: http.HTTPFlow):
        """
        HTTPS will come here first; HTTP on requestheaders
        """
        print(f'http_connect {str(flow)}')
        self.check_emit_flow(flow)

    def http_connect_upstream(self, flow: http.HTTPFlow):
        print(f'http_connect_upstream {str(flow)}')

    def requestheaders(self, flow: http.HTTPFlow):
        """
        HTTP will come here first
        """
        print(f'requestheaders {str(flow)}')
        self.check_emit_flow(flow)
        pass

    def request(self, flow: http.HTTPFlow):
        print(f'request {str(flow)}')
        uid = flow.id
        try:
            content = flow.request.content.decode('utf-8', 'ignore')
        except UnicodeDecodeError:
            content = "[(⊙o⊙)…， 这个数据抓包工具不能解析, 而不是没有request Body数据]"
            print("Failed request decoded!! UnicodeDecodeError")

        request_info = {
            'type': 'request',
            'uuid': uid,
            'url': flow.request.url,
            'http_version': flow.request.http_version,
            'headers': dict(flow.request.headers),
            'content': content,
            'timestamp_start': flow.request.timestamp_start,
            'timestamp_end': flow.request.timestamp_end,
            'host': flow.request.host,
            'port': flow.request.port,
            'method': flow.request.method,
            'scheme': flow.request.scheme,
            'authority': flow.request.authority,
            'path': flow.request.path,
        }
        ensure_cache(flow)
        item = CACHE[uid]
        item.request = request_info

    def responseheaders(self, flow: http.HTTPFlow):
        print(f'responseheaders {str(flow)}')
        pass

    def response(self, flow: http.HTTPFlow) -> None:
        print(f'response {str(flow)}')
        request_time = flow.request.timestamp_start
        response_time = flow.response.timestamp_end
        time_diff = response_time - request_time
        uid = flow.id
        ensure_cache(flow)
        item = CACHE[uid]

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
            'http_version': flow.response.http_version,
            'reason': flow.response.reason,
            'headers': dict(flow.response.headers),
            'content': content,
            'timestamp': str(response_time),
            'time_diff': str(time_diff),
            'timestamp_start': flow.response.timestamp_start,
            'timestamp_end': flow.response.timestamp_end,
        }
        item.response = response_info

    def error(self, flow: http.HTTPFlow):
        ensure_cache(flow)
        item: CaptureItem = CACHE[flow.id]
        request_time = flow.request.timestamp_start
        time_diff = request_time
        try:
            content = flow.response.content.decode()
        except UnicodeDecodeError:
            content = "[(⊙o⊙)…， 这个数据抓包工具不能解析, 而不是没有response Body数据]"
            print("Failed request decoded!! UnicodeDecodeError")
        item.response = {
            'type': 'response',
            'uuid': flow.id,
            'url': flow.request.url,
            'status_code': flow.response.status_code,
            'headers': dict(flow.response.headers),
            'content': content,
            'time_diff': str(time_diff),
            'http_version': flow.response.http_version,
            'timestamp_start': flow.response.timestamp_start,
            'reason': flow.response.reason,
        }
        print(f"error flow {item.error_msg}")
        pass

    def dns_request(self, flow: dns.DNSFlow):
        print(f'dns_request {str(flow)}')
        pass
