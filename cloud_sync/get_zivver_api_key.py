import os
from functools import lru_cache


@lru_cache
def get_zivver_api_key() -> str:
    if "CLOUD_SYNC__ZIVVER_API_KEY" in os.environ:
        return os.getenv("CLOUD_SYNC__ZIVVER_API_KEY").strip('"').strip()

    raise ValueError("CLOUD_SYNC__ZIVVER_API_KEY is not set")
