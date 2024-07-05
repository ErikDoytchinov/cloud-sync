from __future__ import annotations
from cloud_sync.models import EmailAddress
from cloud_sync.models.account import Account, AccountKind
from cloud_sync.models.actions.update_action import Diff


def make_diff(old: Account, new: Account) -> Diff:
    """
    Compare two accounts and return a Diff object with the differences.
    Old should be SCIM. New should be Exo.
    """
    assert (
        old.email_address == new.email_address
    ), "Trying to diff two different accounts"

    # Trying to disable a functional account
    if (
        old.kind == new.kind == AccountKind.FUNCTIONAL
        and old.is_active
        and not new.is_active
    ):
        return Diff(
            is_active=False,  # Does nothing on Functional accounts
            # Actually "disables" the functional account since
            # is_active means len(members) > 0
            delegations=frozenset(),
        )

    full_name = None
    if old.full_name != new.full_name:
        full_name = new.full_name

    is_active = None
    if old.is_active != new.is_active:
        is_active = new.is_active

    aliases: frozenset[EmailAddress] | None = None
    if old.aliases != new.aliases:
        aliases = new.aliases

    delegations: frozenset[EmailAddress] | None = None
    if old.delegations != new.delegations:
        delegations = new.delegations

    return Diff(
        full_name=full_name,
        is_active=is_active,
        aliases=aliases,
        delegations=delegations,
    )
