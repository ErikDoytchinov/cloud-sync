from __future__ import annotations
from cloud_sync.actions.make.make_create import make_create_actions
from cloud_sync.actions.make.make_update import make_update_actions
from cloud_sync.models.account import Account
from cloud_sync.models.actions.create_action import CreateAction
from cloud_sync.models.actions.update_action import UpdateAction
from cloud_sync.models.exo.exo_context import ExoContext


def make_actions(
    *,
    exo_accounts: list[Account],
    scim_accounts: list[Account],
    exo_context: ExoContext,
) -> list[UpdateAction | CreateAction]:
    return make_create_actions(
        exo_accounts=exo_accounts,
        scim_accounts=scim_accounts,
        exo_context=exo_context,
    ) + make_update_actions(
        exo_accounts=exo_accounts,
        scim_accounts=scim_accounts,
    )
