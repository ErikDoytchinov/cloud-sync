from __future__ import annotations
from pydantic import BaseModel, Field

from cloud_sync.models.account import Account
from cloud_sync.models.email_address import EmailAddress


class Diff(BaseModel):
    full_name: str | None = Field(default=None)
    is_active: bool | None = Field(default=None)
    aliases: frozenset[EmailAddress] | None = Field(default=None)
    delegations: frozenset[EmailAddress] | None = Field(default=None)

    model_config = {
        "frozen": True,
    }

    @property
    def all_none(self) -> bool:
        return all(
            v is None
            for v in [self.full_name, self.is_active, self.aliases, self.delegations]
        )

    def __repr__(self):
        """
        This override enabled better "Click to see difference" in PyCharm
        during test failures as it allows the git-like text diff to show
        which JSON field are different, while if it was all on one line,
        it wouldn't be easy to read.
        """
        return self.model_dump_json(indent=2)

    def __eq__(self, other):
        if not isinstance(other, Diff):
            return False

        return all(
            getattr(self, field) == getattr(other, field)
            for field in ["full_name", "is_active", "aliases", "delegations"]
        )


class UpdateAction(BaseModel):
    account: Account
    diff: Diff
