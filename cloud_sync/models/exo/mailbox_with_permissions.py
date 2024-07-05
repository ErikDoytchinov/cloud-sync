from pydantic import BaseModel

from .mailbox_permissions import ExoMailboxPermissions
from .mailbox_response import ExoMailbox


class ExoMailboxWithPermissions(BaseModel):
    mailbox: ExoMailbox
    permissions: ExoMailboxPermissions
