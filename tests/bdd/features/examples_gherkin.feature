Feature: Sync SCIM
  Test the Update and Create SCIM users from EXO users
    
#  Scenario: Sync SCIM
#    Given the claimed domains are:
#      """
#      demo.com
#      zivver.com
#      gmail.com
#      zivvertest.onmicrosoft.com
#      """
#    Given standard Zivver accounts and EXO mailboxes out of sync
#    When I build cloudsync actions
#    When I perform cloudsync actions
# These are the possible instructions, and examples:
#
#   Given I have a SCIM user with the following attributes:
#     """
#     id: "deadbeef-c0ff-ee12-bb86-3b76a1ff4203"
#     userName: "erik@demo.com"
#     name: "Erik Doytchinov"
#     active: true
#     aliases: ["erik@ziver.com", "erik@gmail.com"]
#     delegates: ["sam@gmail.com"]
#     """
#   Given I have a SCIM group with the following attributes:
#     """
#     id: "deadbeef-c0ff-ee12-bb86-3b76a1ff4203"
#     externalId: "erikgroup@demo.com"
#     displayName: "Erik Group Doytchinov"
#     members: ["erik@demo.com", "jack.housego+org@zivver.com"]
#     aliases: ["erik@ziver.com", "erik@gmail.com"]
#     """
#   Given I have an EXO user mailbox with the following attributes:
#     """
#     PrimarySmtpAddress: "erik@demo.com"
#     DisplayName: "Erik Doytchinov"
#     EmailAddresses: ["erik@zivver.com", "erik@gmail.com"]
#     AccountDisabled: false
#     ExternalDirectoryObjectId: "deadbeef-c0ff-ee12-bb86-3b76a1ff4203"
#     Delegates: ["sam@zivver.com", "sam@gmail.com"]
#     """
#   Given I have an EXO shared mailbox with the following attributes:
#     """
#     PrimarySmtpAddress: "erikmarketing@demo.com"
#     DisplayName: "Erik Marketing Doytchinov"
#     EmailAddresses: ["erikmarketing@ziver.com", "erik@gmail.com"]
#     AccountDisabled: false
#     Delegates: ["sam@zivver.com", "sam@gmail.com"]
#     """
#   Then show the exo mailboxes
#   Then show the scim resources
#   When I run cloud sync
#   Then show the actions in the console
#   Then we expect an UPDATE action for account "erik@demo.com":
#     """
#     aliases: ["erik@zivver.com", "erik@gmail.com"]
#     """
#   Then we expect a CREATE action for account "erik@demo.com":
#     """
#     email_address: "erik@demo.com"
#     full_name: "Erik Doytchinov"
#     is_active: true
#     aliases: ["erik@zivver.com", "erik@gmail.com"]
#     delegations: []
#     kind: "user"
#     sso_key: "deadbeef-c0ff-ee12-bb86-3b76a1ff4203"
#     """
#   Then we expect no CREATE actions
#   Then we expect no UPDATE actions