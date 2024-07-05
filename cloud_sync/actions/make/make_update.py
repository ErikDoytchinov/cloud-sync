from __future__ import annotations
from cloud_sync.actions.make_diff import make_diff
from cloud_sync.models.account import Account, AccountKind
from cloud_sync.models.actions.update_action import Diff, UpdateAction
from cloud_sync.models.email_address import EmailAddress
import logging

from typing import NamedTuple


logger = logging.getLogger(__name__)


def make_update_actions(
    exo_accounts: list[Account], scim_accounts: list[Account]
) -> list[UpdateAction]:
    disable_update_actions = _make_disable_update_actions(exo_accounts, scim_accounts)
    common_update_actions = _make_common_update_actions(exo_accounts, scim_accounts)

    return disable_update_actions + common_update_actions


def _make_disable_update_actions(
    exo_accounts: list[Account], scim_accounts: list[Account]
) -> list[UpdateAction]:
    exo_emails = {account.email_address for account in exo_accounts}
    scim_emails = {account.email_address for account in scim_accounts}
    disable_emails = scim_emails - exo_emails

    # jack.housego+org2@zivver.com

    return [
        # Disables User accounts
        UpdateAction(account=account, diff=Diff(is_active=False))
        for account in scim_accounts
        if account.email_address in disable_emails
        and account.kind is AccountKind.USER
        and account.is_active
    ] + [
        # Disables Functional accounts
        # delegations=[] actually "disables" the functional account since
        # is_active means len(member) > 0
        UpdateAction(
            account=account,
            diff=Diff(is_active=False, delegations=[]),
        )
        for account in scim_accounts
        if account.email_address in disable_emails
        and account.kind is AccountKind.FUNCTIONAL
        and account.is_active
    ]


def _make_common_update_actions(
    exo_accounts: list[Account], scim_accounts: list[Account]
) -> list[UpdateAction]:
    common_accounts = _get_common_accounts(exo_accounts, scim_accounts)

    # Ignore account that are groups in scim but usermailbox in exo and vice versa
    for email, common_account in common_accounts.items():
        if common_account.exo.kind != common_account.scim.kind:
            logger.warning(
                f"Skipping account {email} because it is a group in one system and a user mailbox in the other."
            )
            del common_accounts[email]

    common_diffs = [
        (
            common_account.scim,
            make_diff(old=common_account.scim, new=common_account.exo),
        )
        for common_account in common_accounts.values()
    ]

    return [
        UpdateAction(account=account, diff=diff)
        for account, diff in common_diffs
        if not diff.all_none
    ]


class CommonAccount(NamedTuple):
    exo: Account
    scim: Account


def _get_common_accounts(
    exo_accounts: list[Account], scim_accounts: list[Account]
) -> dict[EmailAddress, CommonAccount]:
    exo_map: dict[EmailAddress, Account] = {
        account.email_address: account for account in exo_accounts
    }
    return {
        scim.email_address: CommonAccount(
            exo=exo_map[scim.email_address],
            scim=scim,
        )
        for scim in scim_accounts
        if scim.email_address in exo_map.keys()
    }
