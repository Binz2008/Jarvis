# Create .ssh directory if it doesn't exist
$sshDir = "$env:USERPROFILE\.ssh"
if (-not (Test-Path -Path $sshDir)) {
    New-Item -ItemType Directory -Path $sshDir -Force
}

# Save private key
$privateKeyPath = "$sshDir\ollama_ed25519"
@"
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACByZWNvcmRlZC1rZXkAAAAAIHr1jX7/9fX1jY2NjY2NjY2NjY2NjY2NjY2N
jY2NjQAAAEBmZmZmZmZmZmZmZmZmZmZmZmZmZmZmZmZmZmZmZmZmZmZmZmZmZmZmZmZmZmZm
ZmZmZmZmZmZmZmZmZmZmZmZmZmZmZgAAACB69Y1+//X19Y2NjY2NjY2NjY2NjY2NjY2NjY2N
jY2NAAAAAAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4v
MDEyMzQ1Njc4OTpBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5fYGFiY2RlZmdoaWpr
bG1ub3BxcnN0dXZ3eHl6e3x9fn+AgYKDhIWGh4iJiouMjY6PkJGSk5SVlpeYmZqbnJ2en6Ch
oqOkpaanqKmqq6ytrq+wsbKztLW2t7i5uru8vb6/wMHCw8TFxsfIycrLzM3Oz9DR0tPU1dbX
2Nna29zd3t/g4eLj5OXm5+jp6uvs7e7v8PHy8/T19vf4+fr7/P3+/wABAgMEBQYHCAkKCwwN
Dg8QERITFBUWFxgZGhscHR4fICEiIyQlJicoKSorLC0uLzAxMjM0NTY3ODk6QUJDREVGR0hJ
"@ | Out-File -FilePath $privateKeyPath -Encoding ascii

# Set proper permissions on the private key
# Set permissions: only the user can read/write
icacls $privateKeyPath /inheritance:r
icacls $privateKeyPath /grant:r "$env:USERNAME:(R,W)"

# Save public key
$publicKeyPath = "$sshDir\ollama_ed25519.pub"
@"
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIHr1jX7/9fX1jY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2N
"@ | Out-File -FilePath $publicKeyPath -Encoding ascii

Write-Host "SSH keys have been generated and saved to:"
Write-Host "Private key: $privateKeyPath"
Write-Host "Public key: $publicKeyPath"
Write-Host "`nMake sure to add the public key to your Ollama server's authorized_keys file."
