"""
Wrapper around Curlify to make it transparent
in production, where it's not installed
"""

try:
    from curlify2 import Curlify as _real_Curlify
except ImportError:
    _real_Curlify = None

import httpx


# noinspection PyMethodMayBeStatic
class _FakeCurlify:
    def __init__(self, request: httpx.Request):
        self.request = request

    def to_curl(self) -> str:
        return ""


Curlify = _real_Curlify if _real_Curlify is not None else _FakeCurlify
