from __future__ import annotations

import re

from pytest_bdd import then, parsers

from cloud_sync.models import EmailAddress, Account
from cloud_sync.models.account import AccountKind
from cloud_sync.models.actions.create_action import CreateAction
from cloud_sync.models.actions.update_action import UpdateAction, Diff
from .parse_key_val_lines import parse_key_val_lines


@then(
    parsers.re(
        'we expect an UPDATE action for account "(?P<target_account>.*)":\n?(?P<content>.*)',
        flags=re.DOTALL,
    )
)
def expect_one_update_action(
    actions: list[CreateAction | UpdateAction],
    content: str,
    target_account: EmailAddress,
):
    parsed = parse_key_val_lines(content)
    gherkin_diff = Diff.model_validate(parsed)

    update_actions_on_account = [
        action
        for action in actions
        if action.account.email_address == target_account
        and isinstance(action, UpdateAction)
    ]

    assert len(update_actions_on_account) == 1, (
        f"Expected exactly one UpdateAction for account {target_account}, "
        f"got {len(update_actions_on_account)}"
    )
    update_action = update_actions_on_account[0]

    assert update_action.diff == gherkin_diff, (
        f"Expected UpdateAction's diff to be \n{gherkin_diff.model_dump_json(indent=2)}, "
        f"got \n{update_action.diff.model_dump_json(indent=2)}"
    )


@then(
    parsers.re(
        'we expect a CREATE action for account "(?P<target_account>.*)":\n?(?P<content>.*)',
        flags=re.DOTALL,
    )
)
def expect_one_create_action(
    actions: list[CreateAction | UpdateAction],
    content: str,
    target_account: EmailAddress,
):
    parsed = parse_key_val_lines(content)
    gherkin_account = Account.model_validate(parsed)
    sso_key = parsed["sso_key"] if gherkin_account.kind is AccountKind.USER else None
    expected = CreateAction(account=gherkin_account, sso_key=sso_key)

    create_actions_on_account = [
        action
        for action in actions
        if action.account.email_address == target_account
        and isinstance(action, CreateAction)
    ]

    assert len(create_actions_on_account) == 1, (
        f"Expected exactly one CreateAction for account {target_account}, "
        f"got {len(create_actions_on_account)}"
    )
    create_action = create_actions_on_account[0]

    assert create_action == expected, (
        f"Expected CreateAction to be \n{expected.model_dump_json(indent=2)}\n "
        f"\ngot,\n \n{create_action.model_dump_json(indent=2)}"
    )


@then("we expect no UPDATE actions")
def expect_no_update_action(actions: list[CreateAction | UpdateAction]):
    assert len([action for action in actions if isinstance(action, UpdateAction)]) == 0


@then("we expect no CREATE actions")
def expect_no_create_action(actions: list[CreateAction | UpdateAction]):
    assert len([action for action in actions if isinstance(action, CreateAction)]) == 0
