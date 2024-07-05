from __future__ import annotations

from cloud_sync.models.account import Account
import logging

from cloud_sync.models.email_address import EmailAddress

logger = logging.getLogger(__name__)


def prune(accounts: list[Account], claimed_domains: frozenset[str]) -> list[Account]:
    accounts = _prune_unknown_delegations(accounts)
    accounts = _prune_domain_ownership(
        accounts=accounts, claimed_domains=claimed_domains
    )

    return accounts


def _prune_unknown_delegations(accounts: list[Account]) -> list[Account]:
    emails = {account.email_address for account in accounts}

    cleaned = []

    for account in accounts:
        cleaned_delegations = {
            delegation for delegation in account.delegations if delegation in emails
        }

        pruned = set(account.delegations) - cleaned_delegations
        if len(pruned) > 0:
            logger.warning(
                f"Pruned {len(pruned)} delegations for {account.email_address}: {pruned}"
            )

        cleaned.append(
            account.model_copy(
                update={
                    "delegations": frozenset(cleaned_delegations),
                }
            )
        )

    return cleaned


def _prune_domain_ownership(
    accounts: list[Account], claimed_domains: frozenset[str]
) -> list[Account]:
    all_emails = {account.email_address for account in accounts}

    owned_emails = {
        email for email in all_emails if _is_domain_owned(email, claimed_domains)
    }
    for email in all_emails - owned_emails:
        logger.warning(f"Pruned {email} as it is not owned by the organization")

    return [
        account.model_copy(
            update={
                "delegations": frozenset(
                    [
                        delegation
                        for delegation in account.delegations
                        if _is_domain_owned(delegation, claimed_domains)
                    ]
                ),
                "aliases": frozenset(
                    [
                        alias
                        for alias in account.aliases
                        if _is_domain_owned(alias, claimed_domains)
                    ]
                ),
            }
        )
        for account in accounts
        if _is_domain_owned(account.email_address, claimed_domains)
    ]


def _is_domain_owned(email: EmailAddress, claimed_domains: frozenset[str]) -> bool:
    return any(
        email.lower().strip().split("@")[1] == domain.lower().strip()
        for domain in claimed_domains
    )
