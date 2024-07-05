from __future__ import annotations

from cloud_sync.models.account import Account
from cloud_sync.models.actions.create_action import CreateAction
from cloud_sync.models.exo.exo_context import ExoContext


def make_create_actions(
    *,
    exo_accounts: list[Account],
    scim_accounts: list[Account],
    exo_context: ExoContext,
) -> list[CreateAction]:
    exo_accounts_emails = {account.email_address for account in exo_accounts}

    scim_accounts_emails = {account.email_address for account in scim_accounts}
    new_emails = exo_accounts_emails - scim_accounts_emails

    return [
        CreateAction(
            account=account,
            sso_key=exo_context.sso_keys.get(account.email_address, None),
        )
        for account in exo_accounts
        if account.email_address in new_emails
    ]
