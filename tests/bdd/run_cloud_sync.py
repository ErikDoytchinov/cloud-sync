from __future__ import annotations

import json
from unittest import mock

import pytest
from pytest_bdd import when, then

from cloud_sync.actions.show import show
from cloud_sync.api.get_scim_ids import get_scim_ids_from_models
from cloud_sync.api.make_httpx_client import make_httpx_client
from cloud_sync.main import do_actions, make_actions_from_responses
from cloud_sync.models import EmailAddress
from cloud_sync.models.actions.create_action import CreateAction
from cloud_sync.models.actions.update_action import UpdateAction
from cloud_sync.models.exo.mailbox_with_permissions import ExoMailboxWithPermissions
from cloud_sync.models.scim.scim_groups_response import ScimGroup
from cloud_sync.models.scim.scim_user_response import ScimUser
from .fixtures import (
    get_qualified_name,
    scim_resources,
    exo_mailboxes,
    async_step,
    mock_client,
    actions,
)


@when("I build cloudsync actions")
@async_step
async def build_cloud_sync_actions(
    actions: list[CreateAction | UpdateAction],
    exo_mailboxes: dict[EmailAddress, ExoMailboxWithPermissions],
    scim_resources: dict[EmailAddress, ScimUser | ScimGroup],
    claimed_domains: frozenset[str],
) -> None:
    # It looks like we could use target_fixture here, but if we do,
    # it would fuck up the second time we call this step, as it wouldn't override
    # the fixture...
    output_actions = await make_actions_from_responses(
        exo_mailboxes=list(exo_mailboxes.values()),
        scim_resources=list(scim_resources.values()),
        claimed_domains=claimed_domains,
    )
    actions.clear()
    actions.extend(output_actions)


@when("I perform cloudsync actions")
@async_step
async def perform_cloud_sync_actions(
    actions: list[CreateAction | UpdateAction],
    mock_client: mock.Mock,
    scim_resources: dict[EmailAddress, ScimUser | ScimGroup],
):
    scim_ids = get_scim_ids_from_models(list(scim_resources.values()))
    try:
        with mock.patch(target=get_qualified_name(make_httpx_client), new=mock_client):
            await do_actions(
                api_key="ed and sp are legends", actions=actions, scim_ids=scim_ids
            )
    except Exception:
        actions.clear()
        raise


@then("show the actions in the console")
def show_actions(actions: list[CreateAction | UpdateAction]):
    # This is just a "debugging" action for QAs to see the actions being generated
    print(show(actions))


@then("show the exo mailboxes")
def show_actions(exo_mailboxes: dict[EmailAddress, ExoMailboxWithPermissions]):
    print("EXO mailboxes:")
    print(
        json.dumps(
            {k: s.model_dump(mode="json") for k, s in exo_mailboxes.items()}, indent=2
        )
    )


@then("show the scim resources")
def show_actions(scim_resources: dict[EmailAddress, ScimUser | ScimGroup]):
    print("SCIM resources:")
    print(
        json.dumps(
            {k: s.model_dump(mode="json") for k, s in scim_resources.items()}, indent=2
        )
    )
