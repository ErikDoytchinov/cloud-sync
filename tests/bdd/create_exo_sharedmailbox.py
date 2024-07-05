from __future__ import annotations

import json
import re
import uuid
from uuid import UUID

from pytest_bdd import given, parsers
from pydantic import BaseModel, Field

from cloud_sync.models import EmailAddress
from cloud_sync.models.exo.mailbox_permissions import ExoMailboxPermissions
from cloud_sync.models.exo.mailbox_response import ExoMailbox, RecipientTypeDetailsEnum
from cloud_sync.models.exo.mailbox_with_permissions import ExoMailboxWithPermissions
import logging

from .parse_key_val_lines import parse_key_val_lines

logger = logging.getLogger(__name__)


class GherkinExoSharedMailbox(BaseModel):
    PrimarySmtpAddress: EmailAddress
    DisplayName: str
    EmailAddresses: list[EmailAddress]
    AccountDisabled: bool = Field(default=False)
    Guid: UUID = Field(default_factory=uuid.uuid4)

    Delegates: list[EmailAddress] = Field(default_factory=list)


@given(
    parsers.re(
        "I have an EXO shared mailbox with the following attributes:\n?(?P<content>.*)",
        flags=re.DOTALL,
    )
)
def create_exo_shared_mailbox(
    content: str, exo_mailboxes: dict[EmailAddress, ExoMailboxWithPermissions]
):
    parsed = parse_key_val_lines(content)
    gherkin = GherkinExoSharedMailbox.model_validate(parsed)

    mailbox = ExoMailbox(
        PrimarySmtpAddress=gherkin.PrimarySmtpAddress,
        DisplayName=gherkin.DisplayName,
        EmailAddresses=gherkin.EmailAddresses,
        AccountDisabled=gherkin.AccountDisabled,
        Guid=gherkin.Guid,
        RecipientTypeDetails=RecipientTypeDetailsEnum.SHARED_MAILBOX,
    )

    permissions = ExoMailboxPermissions(
        value=[
            # Just for some test realism, we also add the NT AUTHORITY\SELF B.S.
            {
                "User": "NT AUTHORITY\\SELF",
                "PermissionList": [
                    {
                        "AccessRights": ["FullAccess", "ReadPermission"],
                    },
                    {
                        "AccessRights": [
                            "FullAccess",
                            "ExternalAccount",
                            "ReadPermission",
                        ]
                    },
                ],
            }
        ]
        + [
            {"User": delegate, "PermissionList": [{"AccessRights": ["FullAccess"]}]}
            for delegate in gherkin.Delegates
        ]
    )

    mailbox_with_perms = ExoMailboxWithPermissions(
        mailbox=mailbox, permissions=permissions
    )

    if mailbox.PrimarySmtpAddress in exo_mailboxes:
        logger.warning(
            f"EXO shared mailbox {mailbox.PrimarySmtpAddress} already exists in the mailboxes. "
            f"It will be overwritten with new mailbox"
        )

    exo_mailboxes[mailbox.PrimarySmtpAddress] = mailbox_with_perms

    print()
    print(
        json.dumps(
            {k: s.model_dump(mode="json") for k, s in exo_mailboxes.items()}, indent=2
        )
    )
