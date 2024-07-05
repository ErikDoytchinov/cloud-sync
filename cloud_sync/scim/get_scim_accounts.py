from __future__ import annotations
from uuid import UUID
from cloud_sync.models.account import Account, AccountKind
from cloud_sync.models.scim.scim_groups_response import ScimGroup
from cloud_sync.models.scim.scim_user_response import ScimUser


async def get_scim_accounts(
    scim_resources: list[ScimUser | ScimGroup],
) -> list[Account]:
    users: list[ScimUser] = [
        resource for resource in scim_resources if isinstance(resource, ScimUser)
    ]
    groups: list[ScimGroup] = [
        resource for resource in scim_resources if isinstance(resource, ScimGroup)
    ]
    users_by_id: dict[UUID, ScimUser] = {user.id: user for user in users}

    return [build_account_from_user(user) for user in users] + [
        build_account_from_group(group, users_by_id) for group in groups
    ]


def build_account_from_user(user: ScimUser) -> Account:
    return Account(
        email_address=user.userName,
        full_name=user.name.formatted,
        is_active=user.active,
        aliases=user.zivver_scim_user.aliases,
        delegations=user.zivver_scim_user.delegates,
        kind=AccountKind.USER,
    )


def build_account_from_group(
    group: ScimGroup, users_by_id: dict[UUID, ScimUser]
) -> Account:
    return Account(
        email_address=group.externalId,
        full_name=group.displayName,
        is_active=len(group.members) > 0,
        aliases=frozenset(group.zivver_scim_group.aliases),
        delegations=frozenset(
            users_by_id[member.value].userName
            for member in group.members
            if member.value in users_by_id and group.id != member.value
        ),
        kind=AccountKind.FUNCTIONAL,
    )
