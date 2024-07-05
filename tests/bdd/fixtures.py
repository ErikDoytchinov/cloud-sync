from __future__ import annotations

import inspect
from functools import wraps
from unittest import mock

import httpx
import pytest

from cloud_sync.api.make_httpx_client import make_httpx_client
from cloud_sync.models import EmailAddress
from cloud_sync.models.actions.create_action import CreateAction
from cloud_sync.models.actions.update_action import UpdateAction
from cloud_sync.models.exo.mailbox_with_permissions import ExoMailboxWithPermissions
from cloud_sync.models.scim.scim_groups_response import ScimGroup
from cloud_sync.models.scim.scim_user_response import ScimUser
from tests.bdd.do_actions import make_mock_client


@pytest.fixture()
def scim_resources() -> dict[EmailAddress, ScimUser | ScimGroup]:
    """Containers for the SCIM Users and Groups
    read from the mocked Zivver SCIM server."""
    return dict()


@pytest.fixture()
def exo_mailboxes() -> dict[EmailAddress, ExoMailboxWithPermissions]:
    """Containers for the EXO mailboxes and their
    permissions read from the mocked EXO server."""
    return dict()


@pytest.fixture()
def actions() -> list[CreateAction | UpdateAction]:
    return list()


@pytest.fixture()
def mock_client(
    scim_resources: dict[EmailAddress, ScimUser | ScimGroup],
    claimed_domains: frozenset[str],
) -> mock.Mock:
    """
    Create a function to replace the "make_httpx_client" function.
    That new function outputs an HTTPX client that receives the emitted
    request, processes it, and returns a legitimate looking response,
    essentially mocking the Backend behaviour of the SCIM endpoints.

    When a request comes in, e.g. to create a user, the handler will
    check the request, and if valid, will modify the scim_resources
    dict in consequence. It will also generate scim UUIDs, which the
    client needs.
    """

    def patched_client():
        return make_mock_client(scim_resources, claimed_domains=claimed_domains)

    return mock.Mock(wraps=patched_client)


def get_qualified_name(func):
    """
    Get the fully qualified name of a function, i.e. module.class.function
    Used for mocker.patch
    """
    return f"{func.__module__}.{func.__name__}"


def async_step(step):
    """
    Convert an async pytest-bdd step function to a normal one.
    https://github.com/pytest-dev/pytest-bdd/issues/223#issuecomment-1647998987
    """

    signature = inspect.signature(step)
    parameters = list(signature.parameters.values())
    has_event_loop = any(parameter.name == "event_loop" for parameter in parameters)
    if not has_event_loop:
        parameters.append(
            inspect.Parameter("event_loop", inspect.Parameter.POSITIONAL_OR_KEYWORD)
        )
        step.__signature__ = signature.replace(parameters=parameters)

    @wraps(step)
    def run_step(*args, **kwargs):
        loop = kwargs["event_loop"] if has_event_loop else kwargs.pop("event_loop")
        return loop.run_until_complete(step(*args, **kwargs))

    return run_step
