#!/usr/bin/env python
import subprocess


POWERSHELL_PATH = r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
# Powershell version = 5.1.17763.5328
POWERSHELL_CODE_SCRIPT = r""" 
    $ErrorActionPreference = "Stop"
    Set-PSDebug -Trace 0
    
    Install-PackageProvider -Name NuGet -Scope CurrentUser -Force
    Install-Module ExchangeOnlineManagement -Scope CurrentUser -Confirm:$False -Force -AllowClobber
        
    Import-Module ExchangeOnlineManagement

    Connect-ExchangeOnline -ManagedIdentity -Organization zivvertest.onmicrosoft.com
    $g = Get-Mailbox -ResultSize Unlimited -RecipientTypeDetails SharedMailbox -Debug
    Write-Host $g
"""


def main():
    filename = "script.ps1"
    with open(filename, "w") as f:
        f.write(POWERSHELL_CODE_SCRIPT)

    cmd = [POWERSHELL_PATH, "-File", filename]
    output = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    print(output.stdout.decode("utf-8"))


if __name__ == "__main__":
    main()
