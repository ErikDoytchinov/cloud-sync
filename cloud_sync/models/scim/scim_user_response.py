from __future__ import annotations
from uuid import UUID
from pydantic import BaseModel, Field, field_validator, ConfigDict

from cloud_sync.models.email_address import EmailAddress


#   {
#         "id": "fed41afe-3a5e-43cc-bfa2-3c485a132b92",
#         "name": {
#             "formatted": "Hugo van Haagen"
#         },
#         "meta": {
#             "created": "2023-09-05",
#             "location": "/scim/v2/Users/fed41afe-3a5e-43cc-bfa2-3c485a132b92",
#             "resourceType": "User"
#         },
#         "phoneNumbers": [],
#         "schemas": [
#             "urn:ietf:params:scim:schemas:core:2.0:User",
#             "urn:ietf:params:scim:schemas:extension:enterprise:2.0:User",
#             "urn:ietf:params:scim:schemas:zivver:0.1:User"
#         ],
#         "userName": "hugo.vanhaagen@zivver.com",
#         "active": true,
#         "urn:ietf:params:scim:schemas:extension:enterprise:2.0:User": {
#             "division": "/"
#         },
#         "urn:ietf:params:scim:schemas:zivver:0.1:User": {
#             "aliases": [
#                 "hugo.vanhaagen@zivver.nl",
#                 "hugo.vanhaagen@zivver.co.uk",
#                 "hugo.vanhaagen.alias@zivver.com",
#                 "hugo.vanhaagen@zivver.eu"
#             ],
#             "delegates": []
#         }
#     },


class ScimUserResponse(BaseModel):
    Resources: list[ScimUser]


class ScimUser(BaseModel):
    id: UUID
    userName: EmailAddress
    name: FormattedName
    # SSO NOT FOUND
    active: bool
    zivver_scim_user: ZivverScimUser = Field(
        alias="urn:ietf:params:scim:schemas:zivver:0.1:User"
    )

    model_config = ConfigDict(
        # https://stackoverflow.com/a/69434012
        populate_by_name=True,
    )

    @field_validator("userName", mode="after")
    @classmethod
    def validate_user_name(cls, value: str):
        if "@" not in value:
            raise ValueError("userName must contain @")

        # lowercase all email addresses
        value = value.lower().strip()

        return value


class ZivverScimUser(BaseModel):
    aliases: list[EmailAddress]
    delegates: list[EmailAddress]


class FormattedName(BaseModel):
    formatted: str
