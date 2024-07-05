from __future__ import annotations

from cloud_sync.models.email_address import EmailAddress
from cloud_sync.models.exo.mailbox_permissions import ExoMailboxPermissions
from cloud_sync.models.exo.mailbox_response import RecipientTypeDetailsEnum
from cloud_sync.models.exo.mailbox_with_permissions import ExoMailboxWithPermissions
import logging

Delegations = "dict[EmailAddress, frozenset[EmailAddress]]"

logger = logging.getLogger(__name__)


def get_delegations(
    accounts: list[ExoMailboxWithPermissions],
) -> Delegations:
    base_delegations = {
        account.mailbox.PrimarySmtpAddress: perms_to_delegations(account.permissions)
        for account in accounts
    }
    account_lookups = {
        account.mailbox.PrimarySmtpAddress: account for account in accounts
    }

    return {
        account.mailbox.PrimarySmtpAddress: frozenset(
            _get_delegation(
                account=account.mailbox.PrimarySmtpAddress,
                base_delegations=base_delegations,
                account_lookups=account_lookups,
                seen=list(),
            )
        )
        for account in accounts
    }


def _get_delegation(
    account: EmailAddress,
    base_delegations: Delegations,
    account_lookups: dict[EmailAddress, ExoMailboxWithPermissions],
    seen: list[EmailAddress],
    depth: int = 0,
) -> set[EmailAddress]:
    """
    fyi; recursive
    """
    if depth > 10:
        logger.warning(f"Max depth reached: {account=}, {depth=}, {seen=}")
        return set()

    if account in seen:
        logger.warning(f"Circular delegation detected: {account=}, {depth=}, {seen=}")
        return set()

    if account not in base_delegations:
        return set()

    new_seen = seen.copy()

    new_seen.append(account)

    results: set[EmailAddress] = set()
    for delegation in base_delegations[account]:
        if delegation not in account_lookups:
            results.add(delegation)
            continue

        if not is_group(account_lookups[delegation]):
            results.add(delegation)

        results.update(
            _get_delegation(
                account=delegation,
                base_delegations=base_delegations,
                account_lookups=account_lookups,
                seen=new_seen,
                depth=depth + 1,
            )
        )

    return results


def is_group(account: ExoMailboxWithPermissions) -> bool:
    return (
        account.mailbox.RecipientTypeDetails == RecipientTypeDetailsEnum.SHARED_MAILBOX
    )


def perms_to_delegations(
    exo_permissions: ExoMailboxPermissions,
) -> frozenset[EmailAddress]:
    return frozenset(
        delegation.User
        for delegation in exo_permissions.value
        if "NT AUTHORITY" not in delegation.User
        and "@" in delegation.User
        and any(
            "FullAccess" in permission.AccessRights
            for permission in delegation.PermissionList
        )
    )
