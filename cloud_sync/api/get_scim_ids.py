from __future__ import annotations
from uuid import UUID
from cloud_sync.api.get_scim_groups import get_scim_groups
from cloud_sync.api.get_scim_users import get_scim_users
from cloud_sync.models.email_address import EmailAddress
from cloud_sync.models.scim.scim_groups_response import ScimGroup
from cloud_sync.models.scim.scim_user_response import ScimUser


async def get_scim_user_ids(api_key: str) -> dict[EmailAddress, UUID]:
    scim_users = (await get_scim_users(api_key)).Resources
    return {user.userName: user.id for user in scim_users}


async def get_scim_group_ids(api_key: str) -> dict[EmailAddress, UUID]:
    scim_groups = (await get_scim_groups(api_key)).Resources
    return {group.externalId: group.id for group in scim_groups}


async def get_all_scim_ids(api_key: str) -> dict[EmailAddress, UUID]:
    return {
        **(await get_scim_user_ids(api_key)),
        **(await get_scim_group_ids(api_key)),
    }


def get_scim_ids_from_models(
    scim_resources: list[ScimUser | ScimGroup],
) -> dict[EmailAddress, UUID]:
    return {
        resource.userName
        if isinstance(resource, ScimUser)
        else resource.externalId: resource.id
        for resource in scim_resources
    }
