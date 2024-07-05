#!/usr/bin/env python
from __future__ import annotations

import asyncio
import logging
from uuid import UUID

import coloredlogs

from cloud_sync.actions.make_actions import make_actions
from cloud_sync.actions.show import show
from cloud_sync.api.do_creates import do_creates
from cloud_sync.api.do_updates import do_updates
from cloud_sync.api.get_scim_groups import get_scim_groups
from cloud_sync.api.get_scim_ids import get_scim_ids_from_models
from cloud_sync.api.get_scim_users import get_scim_users
from cloud_sync.boot_message import print_boot_message
from cloud_sync.exchange.get_exo_accounts import (
    get_exo_accounts,
    get_exo_mailboxes_with_permissions,
)
from cloud_sync.exchange.prune import prune
from cloud_sync.get_access_token import get_access_token
from cloud_sync.get_zivver_api_key import get_zivver_api_key
from cloud_sync.models.actions.create_action import CreateAction
from cloud_sync.models.actions.update_action import UpdateAction
from cloud_sync.models.email_address import EmailAddress
from cloud_sync.models.exo.mailbox_with_permissions import ExoMailboxWithPermissions
from cloud_sync.models.scim.scim_groups_response import ScimGroup
from cloud_sync.models.scim.scim_user_response import ScimUser
from cloud_sync.scim.get_scim_accounts import get_scim_accounts
from cloud_sync.settings.settings import Settings

claimed_domains = frozenset({"zivvertest.onmicrosoft.com"})


async def make_actions_from_responses(
    *,
    exo_mailboxes: list[ExoMailboxWithPermissions],
    scim_resources: list[ScimUser | ScimGroup],
    claimed_domains: frozenset[str],
) -> list[UpdateAction | CreateAction]:
    """This is what is testable in E2E tests with Gherkin."""
    exo_accounts, exo_ctx = await get_exo_accounts(mailboxes=exo_mailboxes)
    scim_accounts = await get_scim_accounts(scim_resources=scim_resources)

    exo_accounts = prune(accounts=exo_accounts, claimed_domains=claimed_domains)

    return make_actions(
        exo_accounts=exo_accounts,
        scim_accounts=scim_accounts,
        exo_context=exo_ctx,
    )


async def do_actions(
    *,
    api_key: str,
    actions: list[UpdateAction | CreateAction],
    scim_ids: dict[EmailAddress, UUID],
) -> None:
    create_actions = [action for action in actions if isinstance(action, CreateAction)]
    await do_creates(api_key=api_key, actions=create_actions, scim_ids=scim_ids)

    update_actions = [action for action in actions if isinstance(action, UpdateAction)]
    await do_updates(api_key=api_key, actions=update_actions, scim_ids=scim_ids)


async def main():
    print_boot_message()
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    coloredlogs.install(level="INFO")

    settings = Settings()
    print(settings.model_dump_json(indent=2))

    return

    access_token = get_access_token()
    api_key: str = get_zivver_api_key()
    mailboxes = await get_exo_mailboxes_with_permissions(
        access_token,
    )

    users: list[ScimUser] = (await get_scim_users(api_key)).Resources
    groups: list[ScimGroup] = (await get_scim_groups(api_key)).Resources

    actions = await make_actions_from_responses(
        exo_mailboxes=mailboxes,
        scim_resources=users + groups,
        claimed_domains=claimed_domains,
    )

    print(show(actions))

    val = input("Press Enter to proceed...")
    if len(val.strip()) != 0:
        print("Exiting...")
        return

    scim_ids = get_scim_ids_from_models(users + groups)
    await do_actions(api_key=get_zivver_api_key(), actions=actions, scim_ids=scim_ids)


if __name__ == "__main__":
    asyncio.run(main())
