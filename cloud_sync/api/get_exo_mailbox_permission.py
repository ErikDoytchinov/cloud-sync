import asyncio
from cloud_sync.get_access_token import get_tenant_id
from cloud_sync.models.account import EmailAddress
from cloud_sync.models.exo.mailbox_permissions import ExoMailboxPermissions
from pathlib import Path
import base64
import httpx
from tenacity import (
    stop_after_attempt,
    wait_random_exponential,
    AsyncRetrying,
    RetryError,
)
import logging

logger = logging.getLogger(__name__)


async def get_exo_mailbox_permission(
    access_token: str, email_address: EmailAddress
) -> ExoMailboxPermissions:
    tenant_id = get_tenant_id(access_token)

    try:
        async for attempt in AsyncRetrying(
            sleep=log_sleep,
            wait=wait_random_exponential(multiplier=1, max=60),
            stop=stop_after_attempt(7),
        ):
            with attempt:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(
                        "https://outlook.office365.com"
                        + str(
                            Path("/adminapi/beta")
                            / tenant_id
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
    except RetryError:
        raise RetryError("Failed to get mailbox permission")
    else:
        return ExoMailboxPermissions(**response.json())


async def log_sleep(seconds: float):
    logger.info(f"Backing off for {seconds:.2f} seconds")
    await asyncio.sleep(seconds)
