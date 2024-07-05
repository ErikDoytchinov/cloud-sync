Feature: Create accounts
  Test the creation of users from EXO to SCIM
    
  Scenario: Create a user account from an exo user mailbox when delegates not found
    Given the claimed domains are:
      """
      demo.com
      zivver.com
      gmail.com
      zivvertest.onmicrosoft.com
      """
    Given I have an EXO user mailbox with the following attributes:
      """
      PrimarySmtpAddress: "erik@demo.com"
      DisplayName: "Erik Doytchinov"
      EmailAddresses: ["erik@zivver.com", "erik@gmail.com"]
      AccountDisabled: false
      ExternalDirectoryObjectId: "deadbeef-c0ff-ee12-bb86-3b76a1ff4203"
      Delegates: ["sam@zivver.com", "sam@gmail.com"]
      """
    #    Then show the exo mailboxes
    #    Then show the scim resources
    When I build cloudsync actions
    #    Then show the actions in the console
    Then we expect a CREATE action for account "erik@demo.com":
      """
        email_address: "erik@demo.com"
        full_name: "Erik Doytchinov"
        is_active: true
        aliases: ["erik@zivver.com", "erik@gmail.com"]
        delegations: []
        kind: "user"
        sso_key: "deadbeef-c0ff-ee12-bb86-3b76a1ff4203"
      """
    Then we expect no UPDATE actions

  Scenario: Create a user account from an exo user mailbox with delegates
    Given the claimed domains are:
      """
      demo.com
      zivver.com
      gmail.com
      zivvertest.onmicrosoft.com
      """
    Given I have an EXO user mailbox with the following attributes:
      """
      PrimarySmtpAddress: "sam@demo.com"
      DisplayName: "Sam"
      EmailAddresses: ["sam@demo.com"]
      AccountDisabled: false
      ExternalDirectoryObjectId: "deadbeef-c1ff-ee12-bb86-3b76a1ff4203"
      Delegates: []
      """
    Given I have an EXO user mailbox with the following attributes:
      """
      PrimarySmtpAddress: "erik@demo.com"
      DisplayName: "Erik Doytchinov"
      EmailAddresses: ["erik@zivver.com", "erik@gmail.com"]
      AccountDisabled: false
      ExternalDirectoryObjectId: "deadbeef-c0ff-ee12-bb86-3b76a1ff4203"
      Delegates: ["sam@demo.com"]
      """
    #    Then show the exo mailboxes
    #    Then show the scim resources
    When I build cloudsync actions
    #    Then show the actions in the console
    Then we expect a CREATE action for account "erik@demo.com":
      """
        email_address: "erik@demo.com"
        full_name: "Erik Doytchinov"
        is_active: true
        aliases: ["erik@zivver.com", "erik@gmail.com"]
        delegations: ["sam@demo.com"]
        kind: "user"
        sso_key: "deadbeef-c0ff-ee12-bb86-3b76a1ff4203"
      """
    Then we expect no UPDATE actions
