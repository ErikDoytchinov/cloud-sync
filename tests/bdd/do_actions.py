from __future__ import annotations

import json
import uuid

import httpx
from pydantic import BaseModel, Field

from cloud_sync.models.email_address import EmailAddress
from cloud_sync.models.scim.scim_groups_response import (
    ScimGroup,
    MemberId,
    ZivverScimGroup,
)
from cloud_sync.models.scim.scim_user_response import ScimUser, ZivverScimUser

import logging

logger = logging.getLogger(__name__)


def make_mock_client(
    scim_resources: dict[EmailAddress, ScimUser | ScimGroup],
    claimed_domains: frozenset[str],
) -> httpx.AsyncClient:
    return httpx.AsyncClient(
        transport=httpx.MockTransport(
            handler=_route_handler(scim_resources, claimed_domains=claimed_domains)
        )
    )


def _route_handler(
    scim_resources: dict[EmailAddress, ScimUser | ScimGroup],
    claimed_domains: frozenset[str],
):
    def handler(request: httpx.Request) -> httpx.Response:
        # print("Request received:", request.method, request.url.path)
        if request.url.path == "/api/scim/v2/Users" and request.method == "POST":
            return handle_post_user(
                request=request,
                scim_resources=scim_resources,
                claimed_domains=claimed_domains,
            )
        if request.url.path == "/api/scim/v2/Groups" and request.method == "POST":
            return handle_post_group(
                request=request,
                scim_resources=scim_resources,
                claimed_domains=claimed_domains,
            )
        if "/api/scim/v2/Users/" in request.url.path and request.method == "PUT":
            return handle_put_user(
                request=request,
                scim_resources=scim_resources,
                claimed_domains=claimed_domains,
            )
        if "/api/scim/v2/Groups/" in request.url.path and request.method == "PUT":
            return handle_put_group(
                request=request,
                scim_resources=scim_resources,
                claimed_domains=claimed_domains,
            )
        if "/api/scim/v2/Groups/" in request.url.path and request.method == "PATCH":
            return handle_patch_group(
                request=request,
                scim_resources=scim_resources,
                claimed_domains=claimed_domains,
            )
        raise ValueError(f"Unexpected request: {request.method} {request.url.path}")

    return handler


class PostUserZivverUser(BaseModel):
    aliases: list[str]
    delegates: list[str]
    SsoAccountKey: str


class PostUser(BaseModel):
    userName: str
    name: dict[str, str]
    active: bool
    zivverUser: PostUserZivverUser = Field(
        alias="urn:ietf:params:scim:schemas:zivver:0.1:User"
    )


def handle_post_user(
    request: httpx.Request,
    scim_resources: dict[EmailAddress, ScimUser | ScimGroup],
    claimed_domains: frozenset[str],
) -> httpx.Response:
    body = request.read().decode()
    """
    example body
    {
      "userName": "agile.bottom@zivvertest.onmicrosoft.com",
      "name": {
        "formatted": "Agile Bottom"
      },
      "active": true,
      "urn:ietf:params:scim:schemas:zivver:0.1:User": {
        "aliases": [
          "agile@zivvertest.onmicrosoft.com"
        ],
        "delegates": [],
        "SsoAccountKey": "1b6e3cc5-d234-4d53-9fee-70c6d7c9f9ab"
      }
    }
    """
    user = PostUser.model_validate_json(body)
    scim_user = ScimUser(
        id=uuid.uuid4(),
        userName=user.userName,
        name={"formatted": user.name["formatted"]},
        active=user.active,
        zivver_scim_user=ZivverScimUser(
            aliases=user.zivverUser.aliases,
            delegates=user.zivverUser.delegates,
        ),
    )
    email = EmailAddress(user.userName)
    if email in scim_resources:
        return httpx.Response(status_code=httpx.codes.CONFLICT)

    if not is_domain_owned(email, claimed_domains):
        return httpx.Response(
            status_code=httpx.codes.BAD_REQUEST,
            text="Account is outside the organization",
        )

    if any(
        not is_domain_owned(alias, claimed_domains) for alias in user.zivverUser.aliases
    ):
        return httpx.Response(
            status_code=httpx.codes.BAD_REQUEST,
            text="Error creating alias: Domain Not Owned",
        )

    scim_resources[email] = scim_user
    return httpx.Response(
        status_code=httpx.codes.CREATED,
        json={
            "id": str(scim_user.id),
            "userName": email,
        },
    )


class PostGroupZivverGroup(BaseModel):
    aliases: list[str]


class PostGroupMembers(BaseModel):
    value: str


class PostGroup(BaseModel):
    externalId: str
    displayName: str
    members: list[PostGroupMembers]
    zivverGroup: PostGroupZivverGroup = Field(
        alias="urn:ietf:params:scim:schemas:zivver:0.1:Group"
    )


def handle_post_group(
    request: httpx.Request,
    scim_resources: dict[EmailAddress, ScimUser | ScimGroup],
    claimed_domains: frozenset[str],
) -> httpx.Response:
    body = request.read().decode()
    """
    example body
    {
      "externalId": "alias@zivvertest.onmicrosoft.com",
      "displayName": "displayname",
      "members": [],
      "urn:ietf:params:scim:schemas:zivver:0.1:Group": {
        "aliases": []
      }
    }
    """
    group = PostGroup.model_validate_json(body)
    scim_group = ScimGroup(
        id=uuid.uuid4(),
        externalId=group.externalId,
        displayName=group.displayName,
        members=[MemberId(value=uuid.UUID(member.value)) for member in group.members],
        zivver_scim_group=ZivverScimGroup(
            aliases=group.zivverGroup.aliases,
        ),
    )
    email = EmailAddress(group.externalId)
    if email in scim_resources:
        return httpx.Response(
            status_code=httpx.codes.BAD_REQUEST,
            text="Account is outside the organization",
        )

    if not is_domain_owned(email, claimed_domains):
        return httpx.Response(
            status_code=httpx.codes.BAD_REQUEST,
            text="Account is outside the organization",
        )

    # Checks that each member exists in the scim_resources
    existing_uuids = frozenset(resource.id for resource in scim_resources.values())
    for member in group.members:
        # A member can be either a user or a group apparently...
        member_uuid = uuid.UUID(member.value)
        if member_uuid not in existing_uuids:
            return httpx.Response(
                status_code=httpx.codes.BAD_REQUEST, text="Unknown in set"
            )

    if any(
        not is_domain_owned(alias, claimed_domains)
        for alias in group.zivverGroup.aliases
    ):
        return httpx.Response(
            status_code=httpx.codes.BAD_REQUEST,
            text="Error creating alias: Domain Not Owned",
        )

    scim_resources[email] = scim_group
    return httpx.Response(
        status_code=httpx.codes.CREATED,
        json={
            "id": str(scim_group.id),
            "externalId": email,
        },
    )


class PutUserZivverUser(BaseModel):
    aliases: list[str] | None = Field(default=None)
    delegates: list[str] | None = Field(default=None)
    SsoAccountKey: str | None = Field(default=None)


class PutUser(BaseModel):
    active: bool | None = Field(default=None)
    userName: str | None = Field(default=None)
    name: dict[str, str] | None = Field(default=None)
    zivver_scim_user: PutUserZivverUser | None = Field(
        serialization_alias="urn:ietf:params:scim:schemas:zivver:0.1:User", default=None
    )


def handle_put_user(
    request: httpx.Request,
    scim_resources: dict[EmailAddress, ScimUser | ScimGroup],
    claimed_domains: frozenset[str],
) -> httpx.Response:
    url_user_id = uuid.UUID(request.url.path.split("/")[-1].strip())
    body = request.read().decode()
    put_request = PutUser.model_validate_json(body)

    scim_user_ids = frozenset(
        resource.id
        for resource in scim_resources.values()
        if isinstance(resource, ScimUser)
    )
    if url_user_id not in scim_user_ids:
        # TODO: What to return here?
        return httpx.Response(status_code=httpx.codes.NOT_FOUND)

    existing_user: ScimUser = next(
        resource for resource in scim_resources.values() if resource.id == url_user_id
    )

    new_user: dict = existing_user.model_dump(mode="json", by_alias=True)
    if put_request.active is not None:
        new_user["active"] = put_request.active

    if put_request.userName is not None:
        new_user["userName"] = put_request.userName

    if put_request.name is not None:
        new_user["name"]["formatted"] = put_request.name["formatted"]

    if put_request.zivver_scim_user is not None:
        # If the content is even partially specified, every unspecified key
        # will be erased, hence why we "start blank" with a new dict
        new_zivver_scim_user = {"aliases": [], "delegates": []}
        if put_request.zivver_scim_user.aliases is not None:
            if any(
                not is_domain_owned(alias, claimed_domains)
                for alias in put_request.zivver_scim_user.aliases
            ):
                return httpx.Response(
                    status_code=httpx.codes.BAD_REQUEST,
                    text="Error creating alias: Domain Not Owned",
                )
            new_zivver_scim_user["aliases"] = put_request.zivver_scim_user.aliases

        if put_request.zivver_scim_user.delegates is not None:
            # There is not check in the BE that the delegates are existing account,
            # or that their domain is claimed...
            new_zivver_scim_user["delegates"] = put_request.zivver_scim_user.delegates

        # We don't PUT the SSO key in cloud sync for now (2024-06-28 afaik)
        # if put_request.zivver_scim_user.SsoAccountKey is not None:
        #     # Is the PUT update working or not? Is there even a way to know?
        #     new_zivver_scim_user["SsoAccountKey"] = (
        #         put_request.zivver_scim_user.SsoAccountKey
        #     )
        urn_key = "urn:ietf:params:scim:schemas:zivver:0.1:User"
        new_user[urn_key] = new_zivver_scim_user

    # Overwrite existing user and parse/validate the new user's data
    scim_resources[existing_user.userName] = ScimUser(**new_user)

    return httpx.Response(status_code=httpx.codes.OK)


class PutGroup(BaseModel):
    displayName: str | None = Field(default=None)
    externalId: str | None = Field(default=None)
    members: list[MemberId] | None = Field(default=None)
    zivver_scim_group: PostGroupZivverGroup | None = Field(
        alias="urn:ietf:params:scim:schemas:zivver:0.1:Group", default=None
    )


def handle_put_group(
    request: httpx.Request,
    scim_resources: dict[EmailAddress, ScimUser | ScimGroup],
    claimed_domains: frozenset[str],
) -> httpx.Response:
    url_group_id = uuid.UUID(request.url.path.split("/")[-1].strip())
    body = request.read().decode()
    put_request = PutGroup.model_validate_json(body)

    scim_group_ids = frozenset(
        resource.id
        for resource in scim_resources.values()
        if isinstance(resource, ScimGroup)
    )
    if url_group_id not in scim_group_ids:
        # TODO: What to return here?
        return httpx.Response(
            status_code=httpx.codes.BAD_REQUEST, text="Unknown account with uuid"
        )

    existing_group: ScimGroup = next(
        resource for resource in scim_resources.values() if resource.id == url_group_id
    )

    new_group: dict = existing_group.model_dump(mode="json", by_alias=True)

    if put_request.displayName is not None:
        new_group["displayName"] = put_request.displayName

    if put_request.externalId is not None:
        new_group["externalId"] = put_request.externalId

    if put_request.members is not None:
        if any(
            next((v for v in scim_resources.values() if v.id == member.value), None)
            is None
            for member in put_request.members
        ):
            return httpx.Response(
                status_code=httpx.codes.BAD_REQUEST,
                text="Error creating member: Member Not Found",
            )
        if len(put_request.members) != 0:
            new_group["members"] = put_request.members
        else:
            logger.error(
                "Getting request to set group members "
                "to empty through PUT, but there is a "
                "bug in the implem of the BE that makes "
                "this not work, yet you're doing it! "
                "Are you sure it's okay? "
                "Are you relying on this working?"
            )

    if put_request.zivver_scim_group is not None:
        if any(
            not is_domain_owned(alias, claimed_domains)
            for alias in put_request.zivver_scim_group.aliases
        ):
            return httpx.Response(
                status_code=httpx.codes.BAD_REQUEST,
                text="Error creating alias: Domain Not Owned",
            )
        urn_group = "urn:ietf:params:scim:schemas:zivver:0.1:Group"
        new_group[urn_group]["aliases"] = put_request.zivver_scim_group.aliases

    # Overwrite existing group and parse/validate the new group's data
    scim_resources[existing_group.externalId] = ScimGroup(**new_group)

    return httpx.Response(status_code=httpx.codes.OK)


def handle_patch_group(
    request: httpx.Request,
    scim_resources: dict[EmailAddress, ScimUser | ScimGroup],
    claimed_domains: frozenset[str],
) -> httpx.Response:
    if request.headers.get("Content-Type") != "application/scim+json":
        return httpx.Response(
            status_code=httpx.codes.UNSUPPORTED_MEDIA_TYPE,
            json={"code": 415, "message": "HTTP 415 Unsupported Media Type"},
        )

    # If Accept is unspecified, it also works
    if (
        request.headers.get("Accept", "application/scim+json")
        != "application/scim+json"
    ):
        return httpx.Response(
            status_code=httpx.codes.UNSUPPORTED_MEDIA_TYPE,
            json={"code": 415, "message": "HTTP 415 Unsupported Media Type"},
        )
    url_group_id = uuid.UUID(request.url.path.split("/")[-1].strip())
    body = json.loads(request.read().decode())

    scim_group_ids = frozenset(
        resource.id
        for resource in scim_resources.values()
        if isinstance(resource, ScimGroup)
    )
    if url_group_id not in scim_group_ids:
        # TODO: What to return here?
        return httpx.Response(
            status_code=httpx.codes.BAD_REQUEST, text="Unknown account with uuid"
        )
    """
    example
    {
        "Operations": [
            {
                "op": "remove",
                "path": "members"
            }
        ]
    }
    """
    # For now we only support one thing here: removing all members of
    # a group, so I'll keep it simple with this:
    try:
        if (
            body["Operations"][0]["op"] != "remove"
            or body["Operations"][0]["path"] != "members"
        ):
            raise ValueError("Unsupported operation")
    except (KeyError, IndexError, ValueError):
        return httpx.Response(
            status_code=httpx.codes.BAD_REQUEST,
            text="Unsupported operation",
        )

    group_to_update = next(
        resource for resource in scim_resources.values() if resource.id == url_group_id
    )
    scim_resources[group_to_update.externalId].members = []
    return httpx.Response(status_code=httpx.codes.OK)


def is_domain_owned(email: EmailAddress, claimed_domains: frozenset[str]) -> bool:
    return any(
        email.lower().strip().split("@")[1] == domain.lower().strip()
        for domain in claimed_domains
    )
