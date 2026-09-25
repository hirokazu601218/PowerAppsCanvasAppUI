#Requires -Version 5.1
$ErrorActionPreference = 'Stop'

# Disabled after the isolated test on 2026-09-25. Canvas app owner transfer
# rejected the target service principal: the new owner must be a User.
# Keep this file as a guard so an old instruction cannot transfer ownership.
throw 'Owner transfer is disabled. Power Apps rejected the service principal as canvas app owner (principal type ServicePrincipal; required User). Do not retry this transfer.'
