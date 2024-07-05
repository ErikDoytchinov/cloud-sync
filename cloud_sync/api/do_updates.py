from __future__ import annotations

import logging
from uuid import UUID

import httpx
from pydantic import BaseModel, Field
from tqdm import tqdm

import cloud_sync.api.make_httpx_client as mkclient
from cloud_sync.curlify import Curlify
from cloud_sync.get_zivver_api_url import get_zivver_api_url
from cloud_sync.models.account import AccountKind
from cloud_sync.models.actions.update_action import UpdateAction
from cloud_sync.models.email_address import EmailAddress
from cloud_sync.version import __version__

logger = logging.getLogger(__name__)


class ZivverScimUser(BaseModel):
    aliases: list[EmailAddress] | None
    delegates: list[EmailAddress] | None
    SsoAccountKey: str | None


class FormattedName(BaseModel):
    formatted: str


class ScimUserUpdateRequest(BaseModel):
    active: bool | None
    userName: EmailAddress | None
    name: FormattedName | None
    zivver_scim_user: ZivverScimUser | None = Field(
        serialization_alias="urn:ietf:params:scim:schemas:zivver:0.1:User"
    )


class MemberId(BaseModel):
    value: UUID


class ZivverScimGroup(BaseModel):
    aliases: list[EmailAddress] | None


class ScimGroupUpdateRequest(BaseModel):
    displayName: str | None
    externalId: EmailAddress | None
    members: list[MemberId] | None
    zivver_scim_group: ZivverScimGroup | None = Field(
        serialization_alias="urn:ietf:params:scim:schemas:zivver:0.1:Group"
    )


async def do_updates(
    api_key: str, actions: list[UpdateAction], scim_ids: dict[EmailAddress, UUID]
) -> None:
    for action in tqdm(actions, desc="Updating accounts in Zivver: "):
        if action.account.kind == AccountKind.USER:
            await do_update_user(api_key=api_key, action=action, scim_ids=scim_ids)
        elif action.account.kind == AccountKind.FUNCTIONAL:
            await do_update_group(api_key=api_key, action=action, scim_ids=scim_ids)
        else:
            raise ValueError(f"Unsupported account kind: {action.account.kind}")


async def do_update_user(
    api_key: str, action: UpdateAction, scim_ids: dict[EmailAddress, UUID]
) -> None:
    if action.account.kind is not AccountKind.USER:
        raise ValueError(
            "Expected a user account for update, got: ", action.account.kind
        )
    if action.account.email_address not in scim_ids:
        raise ValueError(
            f"Account {action.account.email_address} not found in SCIM IDs. Cannot update it."
        )
    async with mkclient.make_httpx_client() as client:
        response = await client.put(
            get_zivver_api_url()
            + "/scim/v2/Users/"
            + str(scim_ids[action.account.email_address]),
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
                "User-Agent": "CloudSync/" + __version__,
            },
            content=_make_scim_user_update_request(action=action).model_dump_json(
                by_alias=True, exclude_none=True
            ),
        )
    curl = Curlify(response.request).to_curl()
    if len(curl) > 0:
        logger.info(curl)

    if response.status_code != httpx.codes.OK:
        raise httpx.HTTPError(f"{response.status_code=} {response.text=}")


async def do_update_group(
    api_key: str, action: UpdateAction, scim_ids: dict[EmailAddress, UUID]
) -> None:
    if action.account.kind != AccountKind.FUNCTIONAL:
        raise ValueError(
            "Expected a functional account for update, got: ", action.account.kind
        )
    if action.account.email_address not in scim_ids:
        raise ValueError(
            f"Account {action.account.email_address} not found in SCIM IDs. Cannot update it."
        )
    async with mkclient.make_httpx_client() as client:
        response = await client.put(
            get_zivver_api_url()
            + "/scim/v2/Groups/"
            + str(scim_ids[action.account.email_address]),
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
                "User-Agent": "CloudSync/" + __version__,
            },
            content=_make_scim_group_update_request(
                action=action, scim_ids=scim_ids
            ).model_dump_json(by_alias=True, exclude_none=True),
        )
    curl = Curlify(response.request).to_curl()
    if len(curl) > 0:
        logger.info(curl)

    if response.status_code != httpx.codes.OK:
        raise httpx.HTTPError(f"{response.status_code=} {response.text=}")

    if action.diff.delegations is not None and len(action.diff.delegations) == 0:
        # Our goal was to remove all members from the group, but we can't do that,
        # because of a bug in the PUT endpoint implem, so we need to make another
        # request to a different endpoint after the fact...
        await _do_update_group_remove_all_members(
            api_key=api_key, group_scim_id=scim_ids[action.account.email_address]
        )


def _make_scim_user_update_request(action: UpdateAction) -> ScimUserUpdateRequest:
    return ScimUserUpdateRequest(
        active=action.diff.is_active,
        userName=None,  # Not supported because we don't update email addresses of accounts
        name=FormattedName(formatted=action.diff.full_name)
        if action.diff.full_name
        else None,
        zivver_scim_user=ZivverScimUser(
            aliases=action.diff.aliases,
            delegates=action.diff.delegations,
            SsoAccountKey=None,  # Updates to the SSO account key are not supported yet
        )
        if action.diff.aliases is not None or action.diff.delegations is not None
        else None,
    )


def _make_scim_group_update_request(
    action: UpdateAction, scim_ids: dict[EmailAddress, UUID]
) -> ScimGroupUpdateRequest:
    return ScimGroupUpdateRequest(
        displayName=action.diff.full_name,
        externalId=None,  # Not supported because we don't update email addresses of accounts
        members=[
            MemberId(value=scim_ids[delegation])
            for delegation in action.diff.delegations
            if delegation in scim_ids
        ]
        if action.diff.delegations is not None
        else None,
        zivver_scim_group=ZivverScimGroup(
            aliases=action.diff.aliases,
        )
        if action.diff.aliases is not None
        else None,
    )


async def _do_update_group_remove_all_members(
    api_key: str, group_scim_id: UUID
) -> None:
    """
    Remove all members from a group in Zivver.

    There is a bug in the Zivver SCIM implementation that prevents us
    from removing ALL the members of a group. We can remove some members,
    or add some members, but removing all of them "fails" silently,
    meaning the response code is 200 as if it worked, but actually it did nothing.

    The workaround decided up top is: DO NOT fix the bug in the SCIM endpoint because it'd
    take too much work (multiple weeks), and has too much risk of breaking things, such
    as customers relying on this public API, or older versions of the SyncTool that could
    have a bug where they send an empty list sometime, and expect it to be a no-op (??).

    So now, we also have to work around it...
    :param api_key:
    :param group_scim_id:
    :return:
    """
    async with mkclient.make_httpx_client() as client:
        response = await client.patch(  # NOTE: PATCH is used to remove all members
            get_zivver_api_url() + "/scim/v2/Groups/" + str(group_scim_id),
            headers={
                # NOTE: You *need* this weird ass content type otherwise 406
                "Accept": "application/scim+json",
                # NOTE: You *need* this weird ass content type otherwise 415
                "Content-Type": "application/scim+json",
                "Authorization": f"Bearer {api_key}",
                "User-Agent": "CloudSync/" + __version__,
            },
            content=_make_scim_group_delete_all_members_request().model_dump_json(
                by_alias=True, exclude_none=True
            ),
        )
    curl = Curlify(response.request).to_curl()
    if len(curl) > 0:
        logger.info(curl)

    if response.status_code != httpx.codes.OK:
        raise httpx.HTTPError(f"{response.status_code=} {response.text=}")


class ScimPatchOperation(BaseModel):
    op: str
    path: str


class ScimGroupDeleteAllMembersRequest(BaseModel):
    operations: list[ScimPatchOperation] = Field(serialization_alias="Operations")


def _make_scim_group_delete_all_members_request() -> ScimGroupDeleteAllMembersRequest:
    return ScimGroupDeleteAllMembersRequest(
        operations=[ScimPatchOperation(op="remove", path="members")]
    )
