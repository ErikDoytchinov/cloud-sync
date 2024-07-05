from __future__ import annotations
from pydantic import BaseModel

from cloud_sync.models.email_address import EmailAddress


"""
    {
        "value": [
            {
                "PermissionId": "TlQgQVVUSE9SSVRZXFNFTEY=",
                "MailboxIdentity": "vasilis.prantzos",
                "User": "NT AUTHORITY\\SELF",
                "IsOwner": false,
                "PermissionList": [{"ChangedProperties": [], "AccessRights": ["FullAccess", "ReadPermission"], "IsInherited": false, "Deny": false, "InheritanceType": "All"}]
            }
        ]
    },
"""

"""
   {
        "value": [
            {
                "PermissionId": "TlQgQVVUSE9SSVRZXFNFTEY=",
                "MailboxIdentity": "UserPropertiesTest",
                "User": "NT AUTHORITY\\SELF",
                "IsOwner": false,
                "PermissionList": [
                    {"ChangedProperties": [], "AccessRights": ["FullAccess", "ReadPermission"], "IsInherited": false, "Deny": false, "InheritanceType": "None"},
                    {"ChangedProperties": [], "AccessRights": ["FullAccess", "ExternalAccount", "ReadPermission"], "IsInherited": false, "Deny": false, "InheritanceType": "Descendents"}
                ]
            },
            {
                "PermissionId": "cmljay5nb3VkQHppdnZlcnRlc3Qub25taWNyb3NvZnQuY29t",
                "MailboxIdentity": "UserPropertiesTest",
                "User": "rick.goud@zivvertest.onmicrosoft.com",
                "IsOwner": false,
                "PermissionList": [{"ChangedProperties": [], "AccessRights": ["FullAccess"], "IsInherited": false, "Deny": false, "InheritanceType": "All"}]
            },

            {
                "PermissionId": "dG9tLnZyZWVzd2lqa0B6aXZ2ZXJ0ZXN0Lm9ubWljcm9zb2Z0LmNvbQ==",
                "MailboxIdentity": "UserPropertiesTest",
                "User": "tom.vreeswijk@zivvertest.onmicrosoft.com",
                "IsOwner": false,
                "PermissionList": [{"ChangedProperties": [], "AccessRights": ["FullAccess"], "IsInherited": false, "Deny": false, "InheritanceType": "All"}]
            }
        ]
    },
"""


class ExoMailboxPermissions(BaseModel):
    value: list[MailboxPermission]


class MailboxPermission(BaseModel):
    User: EmailAddress
    PermissionList: list[PermissionItem]


class PermissionItem(BaseModel):
    AccessRights: list[str]
