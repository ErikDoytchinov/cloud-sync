from pathlib import Path

from pydantic import ValidationError

import cloud_sync.api.make_httpx_client as mkclient
from cloud_sync.get_access_token import get_tenant_id
from cloud_sync.models.exo.mailbox_response import ExoMailbox, ExoMailboxResponse

import logging

logger = logging.getLogger(__name__)


async def get_exo_mailbox(access_token: str) -> ExoMailboxResponse:
    tenant_id = get_tenant_id(access_token)

    async with mkclient.make_httpx_client() as client:
        response = await client.get(
            "https://outlook.office365.com"
            + str(Path("/adminapi/beta") / tenant_id / "Mailbox"),
            # https://www.easy365manager.com/get-exomailbox/
            # https://learn.microsoft.com/en-us/powershell/exchange/cmdlet-property-sets?view=exchange-ps#get-exomailbox-property-sets
            params={
                "$select": ",".join(
                    [
                        "PrimarySmtpAddress",
                        "DisplayName",
                        "EmailAddresses",
                        "RecipientTypeDetails",
                        "Guid",
                        "AccountDisabled",
                        "ExternalDirectoryObjectId",
                    ]
                )
            },
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
    if "value" not in response.json():
        logger.error(
            "Could not find EXO mailboxes in the GetEXOMailbox response instead found: "
            + response.text
        )
        exit(1)
    mailboxes = response.json()["value"]
    exo_mailboxes: list[ExoMailbox] = []

    for mailbox in mailboxes:
        try:
            exo_mailboxes.append(ExoMailbox(**mailbox))
        except ValidationError as e:
            logger.error("Failed to parse ExoMailbox: " + str(e))

    if len(exo_mailboxes) == 0:
        logger.error("No valid ExoMailbox could be parsed from response. Aborting.")
        exit(1)

    return ExoMailboxResponse(value=exo_mailboxes)
