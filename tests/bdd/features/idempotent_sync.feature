Feature: Idempotent sync SCIM
  No matter the input state, we should be able to:
  1. Sync once --> actions are required
  2. We take those actions
  3. Sync again --> no more action suggested
  4. Sync again --> no action suggested
  5. Sync again --> no action suggested

  Scenario: Sync SCIM twice with standard accounts
    Given the claimed domains are:
      """
      zivver.com
      zivvertest.onmicrosoft.com
      """
    Given standard Zivver accounts and EXO mailboxes out of sync
    # First sync
    When I build cloudsync actions
    When I perform cloudsync actions
    # Some actions happen here...

    # Second sync
    When I build cloudsync actions

    Then we expect no CREATE actions
    Then we expect no UPDATE actions

    When I perform cloudsync actions

    # Third sync
    When I build cloudsync actions

    Then we expect no CREATE actions
    Then we expect no UPDATE actions

    When I perform cloudsync actions

    # Fourth sync
    When I build cloudsync actions

    Then we expect no CREATE actions
    Then we expect no UPDATE actions
