from __future__ import annotations
import re

from pytest_bdd import given, parsers

from tests.bdd.parse_key_val_lines import parse_key_val_lines


@given(
    parsers.re(
        "the claimed domains are:\n?(?P<content>.*)",
        flags=re.DOTALL,
    ),
    # Be careful, this "given" can't be called twice in the same scenario,
    # as the second call won't override the fixture.
    target_fixture="claimed_domains",
)
def set_claimed_domains(content: str) -> frozenset[str]:
    domains = frozenset(line.strip() for line in content.strip().splitlines())
    assert all(
        "." in domain and domain.islower() for domain in domains
    ), "All claimed domains should have a dot and be lowercase"
    return domains
