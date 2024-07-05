from __future__ import annotations
from enum import Enum
from pydantic import BaseModel

from .email_address import EmailAddress


class AccountKind(str, Enum):
    FUNCTIONAL = "functional"
    USER = "user"


class Account(BaseModel):
    email_address: EmailAddress
    full_name: str
    is_active: bool
    aliases: frozenset[EmailAddress]
    delegations: frozenset[EmailAddress]
    kind: AccountKind

    model_config = {
        "frozen": True,
    }

    def __repr__(self):
        """
        This override enabled better "Click to see difference" in PyCharm
        during test failures as it allows the git-like text diff to show
        which JSON field are different, while if it was all on one line,
        it wouldn't be easy to read.
        """
        return self.model_dump_json(indent=2)

    def __eq__(self, other):
        if not isinstance(other, Account):
            return False

        return all(
            getattr(self, field) == getattr(other, field)
            for field in [
                "email_address",
                "full_name",
                "is_active",
                "aliases",
                "delegations",
                "kind",
            ]
        )
