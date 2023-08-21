import json
import socket
from mitmproxy import ctx, http, dns
from http.client import responses

MODIFY_CACHE = {}
MODIFY_HOST_CACHE = {}


def clear_edit_cache():
    MODIFY_CACHE.clear()
    MODIFY_HOST_CACHE.clear()
    pass


class ModifyCache:
    url: str = ''
    uid: str = ''
    host: str = ''
    requests_data: str = ''
    response_header: str = ''
    response_body: str = ''

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
    print("update_modify * ", str(modify_data))
    if modify_data.requests_data == '' and modify_data.response_header == '' and modify_data.response_body == '':
        if modify_data.url in MODIFY_CACHE:
            MODIFY_CACHE.pop(modify_data.url)
        if modify_data.host in MODIFY_HOST_CACHE:
            MODIFY_HOST_CACHE.pop(modify_data.host)
    else:
        MODIFY_CACHE[modify_data.url] = modify_data
        MODIFY_HOST_CACHE[modify_data.host] = ''



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

    def http_connect(self, flow: http.HTTPFlow):
        print(f"GysoModifyAddon http_connect {str(flow)}")
        print("http_connect URL:", flow.request.url)
        print("http_connect pretty_URL:", flow.request.pretty_url)
        hostname = flow.request.host
        if hostname in MODIFY_HOST_CACHE:
            try:
                ip = socket.gethostbyname(hostname)
                MODIFY_HOST_CACHE[hostname] = ip
                print(f"modify DNS resolution for {hostname}: {ip}")
            except socket.gaierror:
                print(f"modify DNS resolution failed for {hostname}")
                flow.response = http.Response.make(status_code=200)

    def request(self, flow: http.HTTPFlow):
        print(f"request apply_modify[{self.apply_modify}] url[{flow.request.pretty_url}]",
              f" catch [{(flow.request.pretty_url in MODIFY_CACHE)}]")
        if self.apply_modify and flow.request.pretty_url in MODIFY_CACHE:
            m_cache: ModifyCache = MODIFY_CACHE[flow.request.pretty_url]
            if m_cache.requests_data is not None and m_cache.requests_data != '':
                # flow.response.content = m_cache.response_body.encode('utf-8')
                pass
        hostname = flow.request.host
        if hostname in MODIFY_HOST_CACHE and MODIFY_HOST_CACHE[hostname] == '':
            try:
                ip = socket.gethostbyname(hostname)
                MODIFY_HOST_CACHE[hostname] = ip
                print(f"request modify DNS resolution for {hostname}: {ip}")
            except socket.gaierror:
                print("request make request ok")
                flow.response = http.Response.make(status_code=200)


    def response(self, flow: http.HTTPFlow) -> None:
        is_modify_target = flow.request.pretty_url in MODIFY_CACHE
        print(f"response modify ctrl stat[{self.apply_modify}]"
              f"url[{flow.request.pretty_url}]"
              f"is_modify_target[{is_modify_target}]")
        if not self.apply_modify or not is_modify_target:
            pass
        else:
            m_cache: ModifyCache = MODIFY_CACHE[flow.request.pretty_url]
            if m_cache.response_header != '':
                header_lines = m_cache.response_header.split('\n')
                http_version, response_code, *_ = header_lines[0].split(' ')
                response_reason = responses.get(int(response_code), '')

                flow.response.http_version = http_version
                flow.response.status_code = int(response_code)
                flow.response.reason = response_reason

            if m_cache.response_body != '':
                flow.response.content = m_cache.response_body.encode('utf-8')

            print(f"after response modify [{str(flow.response)}]")


    def error(self, flow: http.HTTPFlow):
        print(f"error apply_modify {str(flow)}")
