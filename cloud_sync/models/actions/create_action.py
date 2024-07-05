from __future__ import annotations
from pydantic import BaseModel, Field, model_validator

from cloud_sync.exchange.get_exo_accounts import SSOKey
from cloud_sync.models.account import Account, AccountKind


class CreateAction(BaseModel):
    account: Account
    sso_key: SSOKey | None = Field(
        default=None,
        description=(
            "SSO key for the account. Only available for user accounts. "
            "Functional account don't have one."
        ),
    )

    @model_validator(mode="after")
    @classmethod
    def check_sso_key(cls, v):
        if v.account.kind == AccountKind.USER and v.sso_key is None:
            raise ValueError("SSO key must be specified")

        if v.account.kind == AccountKind.FUNCTIONAL and v.sso_key is not None:
            raise ValueError("SSO key must not be specified")

        return v

    def __eq__(self, other):
        if not isinstance(other, CreateAction):
            return False

        return self.account == other.account and self.sso_key == other.sso_key
