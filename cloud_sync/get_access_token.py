#!/usr/bin/env python
import base64
import json
import os
import httpx
from functools import lru_cache


@lru_cache
def get_access_token() -> str:
    if "CLOUD_SYNC__ACCESS_TOKEN" in os.environ:
        return os.getenv("CLOUD_SYNC__ACCESS_TOKEN").strip('"').strip()

    endpoint = os.getenv("IDENTITY_ENDPOINT")
    if endpoint is None:
        raise ValueError("IDENTITY_ENDPOINT is not set")

    header = os.getenv("IDENTITY_HEADER")
    if header is None:
        raise ValueError("IDENTITY_HEADER is not set")

    response = httpx.get(
        endpoint,
        params={
            "resource": "https://outlook.office365.com/",
            "api-version": "2019-08-01",
        },
        headers={"X-IDENTITY-HEADER": header},
    )
    return response.json()["access_token"]


def main():
    access_token = get_access_token()
    print(access_token)


if __name__ == "__main__":
    main()


def get_tenant_id(access_token: str) -> str:
    _, payload, _ = access_token.split(".")
    # tid == tenant id
    return json.loads(base64.b64decode(payload + "==").decode())["tid"]
