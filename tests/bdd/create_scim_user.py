from __future__ import annotations
import re
import uuid
from uuid import UUID

from pytest_bdd import given, parsers
from pydantic import BaseModel, Field

from cloud_sync.models import EmailAddress
from cloud_sync.models.scim.scim_groups_response import ScimGroup
from cloud_sync.models.scim.scim_user_response import ScimUser, ZivverScimUser
from .fixtures import scim_resources, exo_mailboxes
import logging

from .parse_key_val_lines import parse_key_val_lines

logger = logging.getLogger(__name__)


class GherkinScimUser(BaseModel):
    id: UUID = Field(default_factory=uuid.uuid4)
    userName: EmailAddress
    name: str
    active: bool = Field(default=True)
    aliases: list[EmailAddress] = Field(default_factory=list)
    delegates: list[EmailAddress] = Field(default_factory=list)


@given(
    parsers.re(
        "I have a SCIM user with the following attributes:\n?(?P<content>.*)",
        flags=re.DOTALL,
    )
)
def create_scim_user(
    content: str, scim_resources: dict[EmailAddress, ScimUser | ScimGroup]
):
    parsed = parse_key_val_lines(content)
    gherkin = GherkinScimUser.model_validate(parsed)

    scim_user = ScimUser(
        id=gherkin.id,
        userName=gherkin.userName,
        name={
            "formatted": gherkin.name,
        },
        active=gherkin.active,
        zivver_scim_user=ZivverScimUser(
            aliases=gherkin.aliases, delegates=gherkin.delegates
        ),
    )

    if scim_user.userName in scim_resources:
        logger.warning(
            f"SCIM user {scim_user.userName} already exists in the resources. "
            f"It will be overwritten with new user"
        )

    scim_resources[scim_user.userName] = scim_user

    # print()
    # print(
    #     json.dumps(
    #         {k: s.model_dump(mode="json") for k, s in scim_resources.items()}, indent=2
    #     )
    # )
