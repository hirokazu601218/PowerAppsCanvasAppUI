#Requires -Version 5.1
$ErrorActionPreference = 'Stop'

# Run in Windows PowerShell 5.1 as an administrator of the target Power Platform environment.
# Install the official module to CurrentUser before running:
# Install-Module Microsoft.PowerApps.Administration.PowerShell -Scope CurrentUser

Import-Module Microsoft.PowerApps.Administration.PowerShell
Add-PowerAppsAccount

$environmentName = '68e00049-b7e5-eda6-9888-9a3cc493c5be'
$appName = 'c5dece33-b799-43be-a55b-3344c83979d9'
$expectedDisplayName = 'DEPLOYPROBE_AUTOPUBLISH_20260924'
$expectedOldOwner = '山下 浩和'
$newOwner = 'aa8d08a7-54c4-4e49-9395-6a2c50904815'

$app = Get-AdminPowerApp -AppName $appName -EnvironmentName $environmentName
if ($null -eq $app -or $app.AppName -ne $appName -or
    $app.DisplayName -ne $expectedDisplayName -or
    $app.Owner.DisplayName -ne $expectedOldOwner) {
    throw 'The target app or current owner differs from the approved isolated copy. Nothing was changed.'
}

Write-Host ('Target: {0} ({1})' -f $app.DisplayName, $app.AppName)
Write-Host ('Current owner: {0}' -f $app.Owner.DisplayName)
Write-Host ('New owner object ID: {0}' -f $newOwner)
Set-AdminPowerAppOwner -AppName $appName -EnvironmentName $environmentName -AppOwner $newOwner

$after = Get-AdminPowerApp -AppName $appName -EnvironmentName $environmentName
if ($after.Owner.Id -ne $newOwner) {
    throw 'The transfer was requested but new ownership was not confirmed. Check Maker before retrying.'
}
Write-Host ('Verified new owner: {0} ({1})' -f $after.Owner.DisplayName, $after.Owner.Id)
