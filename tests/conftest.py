# Add every pytest-bdd step files here
pytest_plugins = [
    "tests.bdd.claimed_domains",
    "tests.bdd.standard_accounts",
    "tests.bdd.create_scim_user",
    "tests.bdd.create_scim_group",
    "tests.bdd.create_exo_usermailbox",
    "tests.bdd.create_exo_sharedmailbox",
    "tests.bdd.run_cloud_sync",
    "tests.bdd.expect_actions",
]
