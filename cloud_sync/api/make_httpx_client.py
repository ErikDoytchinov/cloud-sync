import httpx


def make_httpx_client() -> httpx.AsyncClient:
    """
    Wraps client creation in a function to allow overwrite with mock patching during testing.
    https://www.b-list.org/weblog/2023/dec/08/mock-python-httpx/
    """
    return httpx.AsyncClient()
