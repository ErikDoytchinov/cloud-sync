from __future__ import annotations
from uuid import UUID
import httpx
from pydantic import BaseModel, Field

import cloud_sync.api.make_httpx_client as mkclient
from cloud_sync.get_zivver_api_url import get_zivver_api_url
from cloud_sync.models.account import AccountKind
from cloud_sync.models.actions.create_action import CreateAction
from cloud_sync.models.email_address import EmailAddress
from cloud_sync.version import __version__
from tqdm import tqdm
import logging

logger = logging.getLogger(__name__)


class FormattedName(BaseModel):
    formatted: str


class ZivverScimUser(BaseModel):
    aliases: list[EmailAddress]
    delegates: list[EmailAddress]
    SsoAccountKey: str


class ScimCreateUserRequest(BaseModel):
    userName: EmailAddress
    name: FormattedName
    active: bool
    zivver_scim_user: ZivverScimUser = Field(
        serialization_alias="urn:ietf:params:scim:schemas:zivver:0.1:User"
    )


class ScimCreateUserResponse(BaseModel):
    id: UUID
    userName: EmailAddress


class ScimCreateGroupResponse(BaseModel):
    id: UUID
    externalId: EmailAddress


class ZivverScimGroup(BaseModel):
    aliases: list[EmailAddress]


class MemberId(BaseModel):
    # Documentation says this could be an email address, but the API expects a UUID
    value: UUID


class ScimCreateGroupRequest(BaseModel):
    externalId: EmailAddress
    displayName: str
    members: list[MemberId]
    zivver_scim_group: ZivverScimGroup = Field(
        serialization_alias="urn:ietf:params:scim:schemas:zivver:0.1:Group"
    )


async def do_creates(
    api_key: str, actions: list[CreateAction], scim_ids: dict[EmailAddress, UUID]
) -> None:
    """
    Performs creation of users and groups in Zivver.
    Record their SCIM IDs in the scim_ids dictionary, modifying it in place.
    """
    await _do_create_users(api_key=api_key, actions=actions, scim_ids=scim_ids)
    await _do_create_groups(api_key=api_key, actions=actions, scim_ids=scim_ids)


async def _do_create_users(
    api_key: str, actions: list[CreateAction], scim_ids: dict[EmailAddress, UUID]
):
    create_user_requests: list[ScimCreateUserRequest] = [
        _make_user_creation_request(action)
        for action in actions
        if action.account.kind is AccountKind.USER
    ]

    for request in tqdm(create_user_requests, desc="Creating User accounts in Zivver"):
        try:
            scim_user = await _create_user_api(api_key, request)
            scim_ids[scim_user.userName] = scim_user.id
        except httpx.HTTPError as e:
            logger.error(
                f"Failed to create user: {e}, request was: {request.model_dump_json(by_alias=True)}"
            )


async def _do_create_groups(
    api_key: str, actions: list[CreateAction], scim_ids: dict[EmailAddress, UUID]
):
    create_group_requests: list[ScimCreateGroupRequest] = [
        _make_group_creation_request(action, scim_ids)
        for action in actions
        if action.account.kind is AccountKind.FUNCTIONAL
    ]

    for request in tqdm(
        create_group_requests, desc="Creating Functional accounts in Zivver"
    ):
        try:
            scim_group = await _create_group_api(api_key, request)
            scim_ids[scim_group.externalId] = scim_group.id
        except httpx.HTTPError as e:
            logger.error(
                f"Failed to create group: {e}, request was: {request.model_dump_json(by_alias=True)}"
            )


async def _create_user_api(
    api_key: str, request: ScimCreateUserRequest
) -> ScimCreateUserResponse:
    async with mkclient.make_httpx_client() as client:
        response = await client.post(
            get_zivver_api_url() + "/scim/v2/Users",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
                "User-Agent": "CloudSync/" + __version__,
            },
            content=request.model_dump_json(by_alias=True),
        )
    if response.status_code != httpx.codes.CREATED:
        raise httpx.HTTPError(f"{response.status_code=} {response.text=}")

    return ScimCreateUserResponse(**response.json())


async def _create_group_api(
    api_key: str, request: ScimCreateGroupRequest
) -> ScimCreateGroupResponse:
    async with mkclient.make_httpx_client() as client:
        response = await client.post(
            get_zivver_api_url() + "/scim/v2/Groups",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
                "User-Agent": "CloudSync/" + __version__,
            },
            content=request.model_dump_json(by_alias=True),
        )
    if response.status_code != httpx.codes.CREATED:
        raise httpx.HTTPError(f"{response.status_code=} {response.text=}")

    return ScimCreateGroupResponse(**response.json())


def _make_user_creation_request(
    action: CreateAction,
) -> ScimCreateUserRequest:
    if action.account.kind is not AccountKind.USER:
        raise ValueError("Expected a user account")

    return ScimCreateUserRequest(
        userName=action.account.email_address,
        name=FormattedName(formatted=action.account.full_name),
        active=action.account.is_active,
        zivver_scim_user=ZivverScimUser(
            aliases=action.account.aliases,
            delegates=action.account.delegations,
            SsoAccountKey=str(action.sso_key),
        ),
    )


def _make_group_creation_request(
    action: CreateAction,
    scim_ids: dict[EmailAddress, UUID],
) -> ScimCreateGroupRequest:
    if action.account.kind is not AccountKind.FUNCTIONAL:
        raise ValueError("Expected a functional account")

    members = []
    for email_address in action.account.delegations:
        if email_address in scim_ids:
            members.append(MemberId(value=scim_ids[email_address]))
        else:
            logger.error(
                f"Delegation {email_address} not found in SCIM users. Skipping from delegation list."
            )

    return ScimCreateGroupRequest(
        externalId=action.account.email_address,
        displayName=action.account.full_name,
        members=members,
        zivver_scim_group=ZivverScimGroup(aliases=action.account.aliases),
    )
