from __future__ import annotations
import asyncio
import json
from uuid import UUID

from tqdm import tqdm

from cloud_sync.api.get_exo_mailbox import get_exo_mailbox
from cloud_sync.api.get_exo_mailbox_permission import (
    get_exo_mailbox_permission,
)
from cloud_sync.exchange.get_delegations import get_delegations
from cloud_sync.models.account import Account, AccountKind
from cloud_sync.models.email_address import EmailAddress
from cloud_sync.models.exo.exo_context import ExoContext
from cloud_sync.models.exo.mailbox_permissions import ExoMailboxPermissions
from cloud_sync.models.exo.mailbox_response import ExoMailbox, RecipientTypeDetailsEnum
from cloud_sync.models.exo.mailbox_with_permissions import ExoMailboxWithPermissions

SSOKey = UUID


async def get_exo_accounts(
    mailboxes: list[ExoMailboxWithPermissions],
) -> tuple[list[Account], ExoContext]:
    delegations = get_delegations(mailboxes)

    return [
        build_account(mailbox.mailbox, delegations[mailbox.mailbox.PrimarySmtpAddress])
        for mailbox in mailboxes
    ], ExoContext(
        sso_keys=get_sso_keys([mailbox.mailbox for mailbox in mailboxes]),
    )


def get_sso_keys(mailboxes: list[ExoMailbox]) -> dict[EmailAddress, UUID]:
    sso_keys = dict()
    for mailbox in mailboxes:
        if (
            mailbox.ExternalDirectoryObjectId is not None
            and mailbox.RecipientTypeDetails == RecipientTypeDetailsEnum.USER_MAILBOX
        ):
            sso_keys[mailbox.PrimarySmtpAddress] = mailbox.ExternalDirectoryObjectId

    return sso_keys


async def get_exo_mailboxes_with_permissions(
    access_token: str, limit: int | None = None
) -> list[ExoMailboxWithPermissions]:
    mailboxes: list[ExoMailbox] = (await get_exo_mailbox(access_token)).value[:limit]

    permissions: list[ExoMailboxPermissions] = await get_permissions(
        access_token=access_token,
        email_addresses=[mailbox.PrimarySmtpAddress for mailbox in mailboxes],
        batch_size=10,
    )

    # Dump it to create test assets
    with open("mailboxes.json", "w") as f:
        json.dump(
            {
                mailbox.PrimarySmtpAddress: mailbox.model_dump(mode="json")
                for mailbox in mailboxes
            },
            f,
        )
    with open("permissions.json", "w") as f:
        json.dump(
            {
                mailbox.PrimarySmtpAddress: perm.model_dump(mode="json")
                for mailbox, perm in zip(mailboxes, permissions)
            },
            f,
        )

    return [
        ExoMailboxWithPermissions(mailbox=mailbox, permissions=permission)
        for mailbox, permission in zip(mailboxes, permissions)
    ]


async def get_permissions(
    access_token: str, email_addresses: list[EmailAddress], batch_size: int
) -> list[ExoMailboxPermissions]:
    """
    Returns the permissions for the given email addresses.
    The permissions are returned in the same order as the email addresses.
    :param access_token:
    :param email_addresses:
    :param batch_size:
    :return:
    """
    batches: list[list[EmailAddress]] = [
        email_addresses[i : i + batch_size]
        for i in range(0, len(email_addresses), batch_size)
    ]

    pbar = tqdm(total=len(email_addresses), desc="Getting permissions from EXO")
    permissions: list[ExoMailboxPermissions] = []
    for batch in batches:
        permissions.extend(
            # the returned future's result is the list of results
            # (in the order of the original sequence, not necessarily the order of
            # results arrival)
            await asyncio.gather(
                *[get_exo_mailbox_permission(access_token, email) for email in batch]
            )
        )
        pbar.update(len(batch))

    return permissions


def build_account(
    exo_mailbox: ExoMailbox, delegations: frozenset[EmailAddress]
) -> Account:
    return Account(
        email_address=exo_mailbox.PrimarySmtpAddress,
        full_name=exo_mailbox.DisplayName,
        is_active=not exo_mailbox.AccountDisabled,
        aliases=frozenset(
            e for e in exo_mailbox.EmailAddresses if e != exo_mailbox.PrimarySmtpAddress
        ),
        delegations=delegations
        if exo_mailbox.RecipientTypeDetails == RecipientTypeDetailsEnum.USER_MAILBOX
        # If the shared mailbox is disabled, let's remove its delegations as we should add any.
        or not exo_mailbox.AccountDisabled
        else frozenset(),
        kind=AccountKind.USER
        if exo_mailbox.RecipientTypeDetails == RecipientTypeDetailsEnum.USER_MAILBOX
        else AccountKind.FUNCTIONAL,
    )
