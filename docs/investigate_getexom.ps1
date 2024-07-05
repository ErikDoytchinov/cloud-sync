# Install-Module ExchangeOnlineManagement
# Import-Module ExchangeOnlineManagement
# Install-Module Az.Accounts
# Import-Module Az.Accounts
# Import-Module Az.Automation
# Install-Module Az.Automation
# Import-Module Az.Resources
# Install-Module Az.Resources
# 
# 3.4 is latest
Install-Module -Name ExchangeOnlineManagement #-RequiredVersion 3.2.0
Import-Module ExchangeOnlineManagement
# 
# Install-Module Microsoft.Graph -Scope CurrentUser
# Install-Module Microsoft.Graph.Identity.Governance -Scope CurrentUser
# Import-Module Microsoft.Graph.Identity.Governance


# Extracted from the runtime env of Azure Automate
$env:AUTOMATION_ASSET_ACCOUNTID = '0d6b7f60-1e1e-4f5c-83f0-e8516e328b6a'
$env:AUTOMATIONSERVICEENDPOINT = 'https://azat-jdps-we.azure-automation.net:443/'
$env:AZUREPS_HOST_ENVIRONMENT = 'AzureAutomation'
$env:CLIENTID = '8a0c55ac-5899-43b0-bd59-0e912df1441d'
$env:CLIENTKEY = 'jUUa9y+oDCcC4kk9V/JA4KXgxF0yVwHUWPO+27KuQJk='
$env:COMPUTERNAME = 'SANDBOXHOST-638'
$env:FABRIC_APPLICATIONNAME = 'caas-ba8c363d86ef4452a33872dd70e9e5de'
$env:FABRIC_CODEPACKAGENAME = 'azat-sandbox-container-main'
$env:FABRIC_EPOCH = '133600725874094132:8589934592'
$env:FABRIC_ID = '718485da-f67a-46b1-99a2-90fdd05a2d88'
$env:FABRIC_NETWORKINGMODE = 'Other'
$env:FABRIC_NODEIPORFQDN = '10.92.0.16'
$env:FABRIC_REPLICAID = '133600725881125551'
$env:FABRIC_REPLICANAME = '0'
$env:FABRIC_SERVICEDNSNAME = 'service.caas-ba8c363d86ef4452a33872dd70e9e5de'
$env:FABRIC_SERVICENAME = 'service'
$env:IDENTITY_ENDPOINT = 'http://localhost/metadata/identity/oauth2/token'
$env:IDENTITY_HEADER = 'MSIHeaderValue'
$env:MSI_ENDPOINT = 'http://localhost/metadata/identity/oauth2/token'
$env:MSI_SECRET = 'MSIHeaderValue'
$env:NUMBER_OF_PROCESSORS = '1'
$env:OS = 'Windows_NT'
$env:PATHEXT = '.COM;.EXE;.BAT;.CMD;.VBS;.VBE;.JS;.JSE;.WSF;.WSH;.MSC;.PY;.PYW;.CPL'
$env:PROCESSOR_ARCHITECTURE = 'AMD64'
$env:PROCESSOR_IDENTIFIER = 'Intel64 Family 6 Model 85 Stepping 4, GenuineIntel'
$env:PROCESSOR_LEVEL = '6'
$env:PROCESSOR_REVISION = '5504'
$env:PROMPT = '$P$G'
$env:STORESTREAMSINCOSMOSFEATURE = 'True'
$env:STORESTREAMSINSAFEATURE = 'False'
$env:SYSTEMDRIVE = 'C:'
$env:USERDOMAIN = 'User Manager'
$env:USERNAME = 'ContainerUser'

## CONNECT TO EXO
# As runbook
Connect-ExchangeOnline -ManagedIdentity -Organization zivvertest.onmicrosoft.com

# Local
# Connect-ExchangeOnline -Credential anke.bodewes@zivvertest.onmicrosoft.com
# Connect-ExchangeOnline -Credential sam.prevost@zivvertest.onmicrosoft.com -EnableErrorReporting -LogLevel All -Verbose
# Get-ConnectionInformation

# The most important vendor-locked cmdlet...
$g = Get-EXOMailbox -ResultSize Unlimited -RecipientTypeDetails SharedMailbox -Debug
Write-Host $g

$gg = Get-EXOMailbox -RecipientTypeDetails UserMailbox
Write-Host $gg
Get-EXOMailbox -RecipientTypeDetails SharedMailbox

$perm = Get-EXOMailboxPermission -Identity test-shared1@zivvertest.onmicrosoft.com
Write-Host $perm

$ggg = Get-DistributionGroup
Write-Host $ggg

$ggwp = Get-DynamicDistributionGroup
Write-Host $ggwp
