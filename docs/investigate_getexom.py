#!/usr/bin/env python3
import os
from pathlib import Path
import json
from tqdm import tqdm
import base64
import httpx
import asyncio

from cloud_sync.get_access_token import get_tenant_id

OUTLOOK_HOST = "https://outlook.office365.com"


async def main():
    # access_token = get_exo_access_token()
    # Access token look like that. Pop it in jwt.io to inspect ;)
    access_token = """
eyJ0eXAiOiJKV1QiLCJub25jZSI6Imh2S2Z4cmhpVVBRVmJZRExfSFowNGJBSkxyWFpobG5XSHBXTEZ5QjJDb1EiLCJhbGciOiJSUzI1NiIsIng1dCI6IkwxS2ZLRklfam5YYndXYzIyeFp4dzFzVUhIMCIsImtpZCI6IkwxS2ZLRklfam5YYndXYzIyeFp4dzFzVUhIMCJ9.eyJhdWQiOiJodHRwczovL291dGxvb2sub2ZmaWNlMzY1LmNvbS8iLCJpc3MiOiJodHRwczovL3N0cy53aW5kb3dzLm5ldC9jM2VhMTI2ZC0wOGRkLTRiNmEtYTIzYS00YTUxMzE2MGMxMWUvIiwiaWF0IjoxNzE1OTQ3Mzk5LCJuYmYiOjE3MTU5NDczOTksImV4cCI6MTcxNjAzNDA5OSwiYWlvIjoiRTJOZ1lOQitZL3o1Y3NvcmorVlhmZGM0OHJmdEFRQT0iLCJhcHBfZGlzcGxheW5hbWUiOiJhY2NvdW50LXByb3Zpc2lvbmluZyIsImFwcGlkIjoiZWVhZjhiYjQtZTM0Mi00ODQzLWFkNGUtN2M5NGZjYzVhN2I0IiwiYXBwaWRhY3IiOiIyIiwiaWRwIjoiaHR0cHM6Ly9zdHMud2luZG93cy5uZXQvYzNlYTEyNmQtMDhkZC00YjZhLWEyM2EtNGE1MTMxNjBjMTFlLyIsIm9pZCI6IjcyZDdiYTlhLTI5Y2EtNGEyZi04ZTQ5LTU0NDA3NWJkYzU3ZCIsInJoIjoiMC5BRWdBYlJMcXc5MElha3VpT2twUk1XREJIZ0lBQUFBQUFQRVB6Z0FBQUFBQUFBQklBQUEuIiwicm9sZXMiOlsiRXhjaGFuZ2UuTWFuYWdlQXNBcHAiXSwic2lkIjoiYzQ5NjIxZjEtYjBiZC00ODhmLThkZDktYmEwMTIxYmQwNjQwIiwic3ViIjoiNzJkN2JhOWEtMjljYS00YTJmLThlNDktNTQ0MDc1YmRjNTdkIiwidGlkIjoiYzNlYTEyNmQtMDhkZC00YjZhLWEyM2EtNGE1MTMxNjBjMTFlIiwidXRpIjoiajRTT3Z6T3VqazJmYWl0Mm9nYVdBQSIsInZlciI6IjEuMCIsIndpZHMiOlsiZjJlZjk5MmMtM2FmYi00NmI5LWI3Y2YtYTEyNmVlNzRjNDUxIiwiMDk5N2ExZDAtMGQxZC00YWNiLWI0MDgtZDVjYTczMTIxZTkwIl19.Msbpvs0GY80qOo6ZPNr_lXPfzgwwqIc7vDLi9OxGARoSxY_nvqxOaAORrq-sxqyOCajKnVDUciZ1obL0ODCioZBBBt6ISyGcENjVqQjZsvEdAF3Ue8KJXAGn_6EQ3G00dsn3CnBu6TnlEVzzHAaToW77YGeJ7__DhgZBn5AKE4WG5HYvZgYUoEvjQzIh-XUa5l6MBRoOJ_2zQrfR_bpO3jMXn4GCBAcO9ZquMvJu02ORgjT8EpJCT4DpiTCs3IPzm0lyqbHm5eQZ9nXcwdFJ_9SCs1l0mHQnEYBGhkOfrxPS8CIGZARa91IlC4aEHU8vX84ILSOdBqEdLeo-jiJ9_A
    """.strip()
    mailbox = await get_exo_mailbox(access_token)
    emails = [
        mailbox["value"][i]["PrimarySmtpAddress"] for i in range(len(mailbox["value"]))
    ]
    # print(json.dumps(mailbox, indent=2))

    permissions = [
        await get_exo_mailbox_permission(
            access_token=access_token,
            email_address=email,
        )
        for email in tqdm(emails)
    ]
    print(json.dumps(permissions, indent=2))


def get_api_base_url(tenant_id: str) -> Path:
    return Path("/adminapi/beta") / tenant_id


async def get_exo_access_token() -> str:
    endpoint = os.getenv("IDENTITY_ENDPOINT")
    if endpoint is None:
        raise ValueError("IDENTITY_ENDPOINT is not set")

    header = os.getenv("IDENTITY_HEADER")
    if header is None:
        raise ValueError("IDENTITY_HEADER is not set")

    response = await httpx.get(
        endpoint,
        params={
            "resource": "https://outlook.office365.com/",
            "api-version": "2019-08-01",
        },
        headers={"X-IDENTITY-HEADER": header},
    )
    return response.json()["access_token"]


async def get_exo_mailbox(access_token: str) -> dict:
    tenant_id = get_tenant_id(access_token)
    api_base_url = get_api_base_url(tenant_id)

    response = await httpx.get(
        OUTLOOK_HOST + str(api_base_url / "Mailbox"),
        # params={"RecipientTypeDetails": "SharedMailbox"},
        headers={
            "Accept": "application/json;odata.metadata=minimal",
            "Authorization": f"Bearer {access_token}",
            "ps-version": "7.2.9",
            "is-cloud-shell": "True",
            "os-version": "Unix 14.4.1",
            "exomodule-version": "3.4.0",
            "Prefer": "odata.maxpagesize=1000;",
            "OData-Version": "4.0",
            "OData-MaxVersion": "4.0",
        },
    )
    return response.json()


async def get_exo_mailbox_permission(access_token: str, email_address: str) -> dict:
    tenant_id = get_tenant_id(access_token)
    api_base_url = get_api_base_url(tenant_id)

    response = await httpx.get(
        OUTLOOK_HOST
        + str(
            api_base_url
            / f"Mailbox('{base64.b64encode(email_address.encode()).decode()}')"
            / "MailboxPermission"
        ),
        params={"isEncoded": "true"},
        headers={
            "Accept": "application/json;odata.metadata=minimal",
            "Authorization": f"Bearer {access_token}",
            "ps-version": "7.2.9",
            "is-cloud-shell": "True",
            "os-version": "Unix 14.4.1",
            "exomodule-version": "3.4.0",
            "Prefer": "odata.maxpagesize=1000;",
            "OData-Version": "4.0",
            "OData-MaxVersion": "4.0",
        },
    )
    return response.json()


if __name__ == "__main__":
    asyncio.run(main())
