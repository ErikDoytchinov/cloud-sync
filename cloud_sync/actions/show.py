from __future__ import annotations
from cloud_sync.models.account import Account
from cloud_sync.models.actions.create_action import CreateAction
from cloud_sync.models.actions.update_action import Diff, UpdateAction
from colorama import Fore, Style


def show(actions: list[UpdateAction | CreateAction]) -> str:
    update_actions = [action for action in actions if isinstance(action, UpdateAction)]
    create_actions = [action for action in actions if isinstance(action, CreateAction)]

    return (
        Fore.CYAN
        + "Updates: \n"
        + Style.RESET_ALL
        + "\t\n".join(_show_action(action) for action in update_actions)
        + "\n\n"
        + Fore.GREEN
        + "Creates: \n"
        + Style.RESET_ALL
        + "\t\n".join(_show_action(action) for action in create_actions)
        + Style.RESET_ALL
    )


def _show_action(action: UpdateAction | CreateAction) -> str:
    if isinstance(action, CreateAction):
        return _show_account(action.account)
    if isinstance(action, UpdateAction):
        return (
            action.account.email_address
            + "\n"
            + Fore.CYAN
            + _show_diff(action.diff, old_account=action.account)
            + Style.RESET_ALL
        )


def _show_diff(diff: Diff, old_account: Account) -> str:
    s = ""
    if diff.full_name is not None:
        s += f"  full_name:\t{old_account.full_name} -> {diff.full_name} \n"

    if diff.is_active is not None:
        s += f"  is_active:\t{old_account.is_active} -> {diff.is_active} \n"

    if diff.aliases is not None:
        old = old_account.aliases
        new = diff.aliases or frozenset()
        added = new - old
        removed = old - new
        if len(added) > 0 or len(removed) > 0:
            s += "  aliases:\n"
        for email in added:
            s += f"\t{Fore.GREEN}+{Fore.CYAN} {email}\n"

        for email in removed:
            s += f"\t{Fore.RED}-{Fore.CYAN} {email}\n"

    if diff.delegations is not None:
        old = old_account.delegations
        new = diff.delegations or frozenset()
        added = new - old
        removed = old - new
        if len(added) > 0 or len(removed) > 0:
            s += "  delegations:\n"
        for email in added:
            s += f"\t{Fore.GREEN}+{Fore.CYAN} {email}\n"

        for email in removed:
            s += f"\t{Fore.RED}-{Fore.CYAN} {email}\n"

    return s


def _show_account(account: Account) -> str:
    s = ""
    s += f"{account.email_address}\n"
    s += Fore.GREEN
    s += f"\tkind:\t{account.kind}\n"
    s += f"\tfull_name:\t{account.full_name}\n"
    s += f"\tis_active:\t{account.is_active}\n"
    s += "\taliases:\n"
    for alias in account.aliases:
        s += f"\t\t{alias}\n"
    s += "\tdelegations:\n"
    for delegation in account.delegations:
        s += f"\t\t{delegation}\n"
    s += Style.RESET_ALL
    return s.strip()
