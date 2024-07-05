from __future__ import annotations

import json
import re
import uuid
from uuid import UUID

from pytest_bdd import given, parsers
from pydantic import BaseModel, Field

from cloud_sync.models import EmailAddress
from cloud_sync.models.scim.scim_groups_response import ScimGroup, ZivverScimGroup
from cloud_sync.models.scim.scim_user_response import ScimUser
from .fixtures import scim_resources, exo_mailboxes
import logging

from .parse_key_val_lines import parse_key_val_lines

logger = logging.getLogger(__name__)


class GherkinScimGroup(BaseModel):
    id: UUID = Field(default_factory=uuid.uuid4)
    externalId: EmailAddress
    displayName: str
    members: list[EmailAddress] = Field(default_factory=list)
    aliases: list[EmailAddress] = Field(default_factory=list)


@given(
    parsers.re(
        "I have a SCIM group with the following attributes:\n?(?P<content>.*)",
        flags=re.DOTALL,
    )
)
def create_scim_group(
    content: str, scim_resources: dict[EmailAddress, ScimUser | ScimGroup]
):
    parsed = parse_key_val_lines(content)
    gherkin = GherkinScimGroup.model_validate(parsed)

    scim_group = ScimGroup(
        id=gherkin.id,
        externalId=gherkin.externalId,
        displayName=gherkin.displayName,
        members=[
            dict(value=mid)
            for mid in _members_email_to_id(scim_resources, gherkin.members)
        ],
        zivver_scim_group=ZivverScimGroup(aliases=gherkin.aliases),
    )

    if scim_group.externalId in scim_resources:
        logger.warning(
            f"SCIM group {scim_group.externalId} already exists in the resources. "
            f"It will be overwritten with new group"
        )

    scim_resources[scim_group.externalId] = scim_group

    # print()
    # print(
    #     json.dumps(
    #         {k: s.model_dump(mode="json") for k, s in scim_resources.items()}, indent=2
    #     )
    # )


def _members_email_to_id(
    scim_resources: dict[EmailAddress, ScimUser], members: list[EmailAddress]
) -> list[UUID]:
    return [scim_resources[member].id for member in members]
