import json

from mitmproxy import ctx, http

MODIFY_CACHE = {}


def clear_edit_cache():
    MODIFY_CACHE.clear()
    pass

class ModifyCache:
    url: str = ...
    uid: str = ...
    requests_data: str = ...
    response_header: str = ...
    response_body: str = ...

    def as_json(self):
        return json.dumps({
            "url": self.url,
            "uid": self.uid,
            "requests_data": self.requests_data,
            "response_header": self.response_header,
            "response_body": self.response_body
        })

    def __str__(self) -> str:
        return self.as_json()


def update_modify(modify_data: ModifyCache):
    MODIFY_CACHE[modify_data.url] = modify_data
    print(str(modify_data))


def get_modify_detail(uid):
    print(f"get_modify_detail uid[{uid}]")
    if uid == '':
        return ''

    for url in MODIFY_CACHE:
        modify = MODIFY_CACHE[url]
        if uid == modify.uid:
            return modify.as_json()

    print(f"get_modify_detail end uid[{uid}]")
    return json.dumps({
            "url": '',
            "uid": uid,
            "requests_data": '',
            "response_header": '',
            "response_body": ''
        })


class GysoModifyAddon:
    """
       Http and Https 拦截
    """
    apply_modify = False

    def request(self, flow: http.HTTPFlow):
        print(f"request apply_modify[{self.apply_modify}] url[{flow.request.pretty_url}]",
              f" catch [{(flow.request.pretty_url in MODIFY_CACHE)}]")
        if self.apply_modify and flow.request.pretty_url in MODIFY_CACHE:
            m_cache: ModifyCache = MODIFY_CACHE[flow.request.pretty_url]
            if m_cache.requests_data is not None and m_cache.requests_data != '':
                # flow.response.content = m_cache.response_body.encode('utf-8')
                pass
        pass

    def response(self, flow: http.HTTPFlow) -> None:
        print(f"response apply_modify[{self.apply_modify}] url[{flow.request.pretty_url}]",
              f" catch [{(flow.request.pretty_url in MODIFY_CACHE)}]")
        if self.apply_modify and flow.request.pretty_url in MODIFY_CACHE:
            m_cache: ModifyCache = MODIFY_CACHE[flow.request.pretty_url]
            if m_cache.response_body is not None and m_cache.response_body != '':
                flow.response.content = m_cache.response_body.encode('utf-8')
            pass
