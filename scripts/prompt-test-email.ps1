$ErrorActionPreference = 'Stop'
$inputPath = Join-Path $env:TEMP 'boursnegar-test-email.input'
Remove-Item -LiteralPath $inputPath -Force -ErrorAction SilentlyContinue
$testEmail = Read-Host 'Enter the test recipient email for Boursnegar, then press Enter'
if ($testEmail -notmatch '^[^\s@]+@[^\s@]+\.[^\s@]+$') {
  Write-Host 'Invalid email. Close this window and ask Codex to retry.' -ForegroundColor Red
  Start-Sleep -Seconds 10
  exit 1
}
[System.IO.File]::WriteAllText($inputPath, $testEmail, [System.Text.UTF8Encoding]::new($false))
$acl = Get-Acl -LiteralPath $inputPath
$acl.SetAccessRuleProtection($true, $false)
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
  [System.Security.Principal.WindowsIdentity]::GetCurrent().Name,
  'FullControl',
  'Allow'
)
$acl.SetAccessRule($rule)
Set-Acl -LiteralPath $inputPath -AclObject $acl
Clear-Variable testEmail
Write-Host 'Email received securely. You may close this window.' -ForegroundColor Green
Start-Sleep -Seconds 5
