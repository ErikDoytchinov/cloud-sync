from __future__ import annotations
from enum import Enum
import re
from uuid import UUID
from pydantic import BaseModel, field_validator, Field
import logging

from cloud_sync.models.email_address import EmailAddress

logger = logging.getLogger(__name__)


class ExoMailboxResponse(BaseModel):
    value: list[ExoMailbox]


"""
    {
      "PrimarySmtpAddress": "ORGsharedmailbox@zivvertest.onmicrosoft.com",
      "DisplayName": "[ORG] Shared Mailbox Test",
      "EmailAddresses": [
        "SMTP:ORGsharedmailbox@zivvertest.onmicrosoft.com",
        "smtp:enforcesharedmailbox@zivvertest.onmicrosoft.com"
      ],
      "RecipientTypeDetails": "SharedMailbox",  
      "Guid": "2a1faf15-c06d-42d9-b442-7755d3d2f5cf"
    },
"""

"""
    {
      "PrimarySmtpAddress": "testplugin5@zivvertest.onmicrosoft.com",
      "DisplayName": "testplugin 5",
      "EmailAddresses": [
        "SMTP:testplugin5@zivvertest.onmicrosoft.com"
      ],
      "RecipientTypeDetails": "UserMailbox",
      "Guid": "5d17bcee-35ed-4445-80d4-9d152af49f83"
    },
"""


class RecipientTypeDetailsEnum(str, Enum):
    SHARED_MAILBOX = "SharedMailbox"
    USER_MAILBOX = "UserMailbox"


class ExoMailbox(BaseModel):
    PrimarySmtpAddress: EmailAddress
    DisplayName: str
    EmailAddresses: list[EmailAddress]
    RecipientTypeDetails: RecipientTypeDetailsEnum
    AccountDisabled: bool
    ExternalDirectoryObjectId: UUID | None = Field(default=None)
    Guid: UUID

    @field_validator("EmailAddresses", mode="after")
    @classmethod
    def validate_email_addresses(cls, values: list[str]):
        values = [v for v in values if ":" not in v or v.upper().startswith("SMTP:")]
        if len(values) == 0:
            raise ValueError("EmailAddresses must not be empty")

        if not all("@" in value for value in values):
            raise ValueError("EmailAddresses must contain @")

        values = [
            re.sub(pattern=r"^SMTP:", repl="", string=email, flags=re.IGNORECASE)
            for email in values
        ]

        # lowercase all email addresses
        values = [v.lower().strip() for v in values]

        valid_emails = []
        for value in values:
            # At least an @ and a dot after
            if re.match(r"^[^@]+@[^@]+\.[^@]+$", value, re.IGNORECASE):
                valid_emails.append(value)
            else:
                logger.warning(f"Invalid email address: {value} skipping from aliases.")

        return valid_emails

    @field_validator("PrimarySmtpAddress", mode="after")
    @classmethod
    def validate_primary_smtp_address(cls, value: str):
        if "@" not in value:
            raise ValueError("PrimarySmtpAddress must contain @")

        # lowercase all email addresses
        value = value.lower().strip()

        return value
