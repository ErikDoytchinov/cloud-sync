from __future__ import annotations
from uuid import UUID
from pydantic import BaseModel, Field, field_validator, ConfigDict

from cloud_sync.models.email_address import EmailAddress


# {
#     "id": "8745c208-fb0b-4624-be02-bb0f298d7a23",
#     "externalId": "primairfunctioneel@zivver.com",
#     "displayName": "primairfunctioneel@zivver.com",
#     "members": [
#         {
#             "value": "175db8a0-eb6a-48ac-8360-bff287a89165"
#         }
#     ],
#     "meta": {
#         "created": "2022-07-20",
#         "location": "/scim/v2/Groups/8745c208-fb0b-4624-be02-bb0f298d7a23",
#         "resourceType": "Group"
#     },
#     "schemas": [
#         "urn:ietf:params:scim:schemas:core:2.0:Group",
#         "urn:ietf:params:scim:schemas:zivver:0.1:Group",
#         "urn:ietf:params:scim:schemas:extension:enterprise:2.0:User"
#     ],
#     "urn:ietf:params:scim:schemas:extension:enterprise:2.0:User": {
#         "division": "/"
#     },
#     "urn:ietf:params:scim:schemas:zivver:0.1:Group": {
#         "aliases": [
#             "aliasfunctioneel@zivver.com"
#         ]
#     }
# },


class ScimGroupResponse(BaseModel):
    Resources: list[ScimGroup]


class ScimGroup(BaseModel):
    id: UUID
    externalId: EmailAddress
    displayName: str
    members: list[MemberId]
    zivver_scim_group: ZivverScimGroup = Field(
        alias="urn:ietf:params:scim:schemas:zivver:0.1:Group"
    )

    model_config = ConfigDict(
        # https://stackoverflow.com/a/69434012
        populate_by_name=True,
    )

    @field_validator("externalId", mode="after")
    @classmethod
    def validate_external_id(cls, value: str):
        if "@" not in value:
            raise ValueError("externalId must contain @")

        # lowercase all email addresses
        value = value.lower().strip()

        return value


class ZivverScimGroup(BaseModel):
    aliases: list[EmailAddress]


class MemberId(BaseModel):
    value: UUID
