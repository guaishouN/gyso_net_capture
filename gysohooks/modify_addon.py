from mitmproxy import ctx, http

MODIFY_CACHE = {}


class ModifyCache:
    url: str = ...
    requests_data: str = ...
    response_header: str = ...
    response_body: str = ...

    def __str__(self) -> str:
        return str({
            "url": self.url,
            "requests_data": self.requests_data,
            "response_header": self.response_header,
            "response_body": self.response_body
        })


def update_modify(modify_data: ModifyCache):
    MODIFY_CACHE[modify_data.url] = modify_data
    print(str(modify_data))


def get_modify_detail(url):
    if url in MODIFY_CACHE:
        return str(MODIFY_CACHE[url])
    else:
        return "null"
    pass


class GysoModifyAddon:
    """
       Http and Https 拦截
    """
    apply_modify = False

    def request(self, flow: http.HTTPFlow):
        print(f"apply_modify[{self.apply_modify}] url[{flow.request.pretty_url}]",
              f" catch [{(flow.request.pretty_url in MODIFY_CACHE)}]")
        if self.apply_modify and flow.request.pretty_url in MODIFY_CACHE:
            m_cache: ModifyCache = MODIFY_CACHE[flow.request.pretty_url]
            if m_cache.requests_data is not None and m_cache.requests_data != '':
                # flow.response.content = m_cache.response_body.encode('utf-8')
                pass
        pass

    def response(self, flow: http.HTTPFlow) -> None:
        print(f"apply_modify[{self.apply_modify}] url[{flow.request.pretty_url}]",
              f" catch [{(flow.request.pretty_url in MODIFY_CACHE)}]")
        if self.apply_modify and flow.request.pretty_url in MODIFY_CACHE:
            m_cache: ModifyCache = MODIFY_CACHE[flow.request.pretty_url]
            if m_cache.response_body is not None and m_cache.response_body != '':
                flow.response.content = m_cache.response_body.encode('utf-8')
            pass
