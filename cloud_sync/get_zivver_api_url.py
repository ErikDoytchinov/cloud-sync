import os
from functools import lru_cache


@lru_cache
def get_zivver_api_url() -> str:
    if "CLOUD_SYNC__ZIVVER_API_URL" in os.environ:
        url = os.getenv("CLOUD_SYNC__ZIVVER_API_URL").strip('"').strip()
        if not url.startswith("http"):
            raise ValueError("CLOUD_SYNC__ZIVVER_API_URL must start with 'https://'")
        # if not url.startswith("https"):
        #     raise ValueError("CLOUD_SYNC__ZIVVER_API_URI must end with 'https://'")
        if url.endswith("/"):
            raise ValueError(
                "CLOUD_SYNC__ZIVVER_API_URL must not end with a trailing slash"
            )
        return url

    raise ValueError("CLOUD_SYNC__ZIVVER_API_URL is not set")
