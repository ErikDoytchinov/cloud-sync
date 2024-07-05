from __future__ import annotations
from uuid import UUID
from pydantic import BaseModel

from cloud_sync.models.email_address import EmailAddress


class ExoContext(BaseModel):
    """
    EXO specific data obtained alongside the accounts
    """

    sso_keys: dict[EmailAddress, UUID]

    model_config = {
        "frozen": True,
    }
