from __future__ import annotations
import json
from pytest_bdd import given

from cloud_sync.models import EmailAddress
from cloud_sync.models.exo.mailbox_permissions import ExoMailboxPermissions
from cloud_sync.models.exo.mailbox_response import ExoMailbox
from cloud_sync.models.exo.mailbox_with_permissions import ExoMailboxWithPermissions
from cloud_sync.models.scim.scim_groups_response import ScimGroup
from cloud_sync.models.scim.scim_user_response import ScimUser
from .fixtures import scim_resources, exo_mailboxes


@given("standard Zivver accounts and EXO mailboxes out of sync")
def standard_accounts(
    exo_mailboxes: dict[EmailAddress, ExoMailboxWithPermissions],
    scim_resources: dict[EmailAddress, ScimUser | ScimGroup],
):
    _read_exo(exo_mailboxes)
    _read_scim(scim_resources)


def _read_exo(exo_mailboxes: dict[EmailAddress, ExoMailboxWithPermissions]) -> None:
    filepath_exo_mailboxes = "tests/assets/2024-06-21_exo_mailboxes.json"
    filepath_exo_permissions = "tests/assets/2024-06-21_exo_permissions.json"

    with open(filepath_exo_mailboxes, "r") as file:
        raw_exo_mailboxes = json.load(file)
        exo_mailboxes_only = {
            email: ExoMailbox.model_validate(raw)
            for email, raw in raw_exo_mailboxes.items()
        }

    with open(filepath_exo_permissions, "r") as file:
        raw_exo_perms = json.load(file)
        exo_permissions = {
            email: ExoMailboxPermissions.model_validate(raw)
            for email, raw in raw_exo_perms.items()
        }

    for email, mailbox in exo_mailboxes_only.items():
        assert email in exo_permissions, "EXO permissions missing for mailbox file."
        exo_mailboxes[email] = ExoMailboxWithPermissions(
            mailbox=mailbox, permissions=exo_permissions[email]
        )


def _read_scim(scim_resources: dict[EmailAddress, ScimUser | ScimGroup]) -> None:
    filepath_scim_users = "tests/assets/2024-06-21_zivver_org_scim_users.json"
    filepath_scim_groups = "tests/assets/2024-06-21_zivver_org_scim_groups.json"

    with open(filepath_scim_users, "r") as file:
        raw_scim_users = json.load(file)["Resources"]
        scim_users = {
            raw["userName"]: ScimUser.model_validate(raw) for raw in raw_scim_users
        }

    with open(filepath_scim_groups, "r") as file:
        raw_scim_groups = json.load(file)["Resources"]
        scim_groups = {
            raw["externalId"]: ScimGroup.model_validate(raw) for raw in raw_scim_groups
        }

    for email, user in scim_users.items():
        scim_resources[email] = user

    for email, group in scim_groups.items():
        scim_resources[email] = group
