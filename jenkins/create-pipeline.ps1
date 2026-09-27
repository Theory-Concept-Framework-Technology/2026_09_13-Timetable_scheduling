# Creates or updates the mouse-gaze Pipeline job on Jenkins.
# Requires an API token (Jenkins user -> Security -> Add new token), not the account password.
param(
    [string]$JenkinsUrl = "http://143.244.128.22:8081",
    [string]$JobName = "mouse-gaze",
    [string]$GitUrl = "",
    [string]$GitBranch = "*/master",
    [string]$User = $env:JENKINS_USER,
    [string]$Token = $env:JENKINS_API_TOKEN
)

$ErrorActionPreference = "Stop"

if (-not $User -or -not $Token) {
    throw "Set JENKINS_USER and JENKINS_API_TOKEN, or pass -User and -Token."
}
if (-not $GitUrl) {
    throw "Pass -GitUrl. Jenkins clones that repository and runs its Jenkinsfile."
}

$JenkinsUrl = $JenkinsUrl.TrimEnd("/")
$auth = "${User}:${Token}"
$configPath = Join-Path $PSScriptRoot "job-config.xml"
$config = Get-Content -Raw -Path $configPath
$config = $config.Replace("__GIT_URL__", [System.Security.SecurityElement]::Escape($GitUrl))
$config = $config.Replace("__GIT_BRANCH__", [System.Security.SecurityElement]::Escape($GitBranch))

$crumbJson = curl.exe -fsS -u $auth "$JenkinsUrl/crumbIssuer/api/json"
if ($LASTEXITCODE -ne 0) {
    throw "Could not get a Jenkins crumb. Check the URL, username, and API token."
}
$crumb = $crumbJson | ConvertFrom-Json

$tempConfig = Join-Path $env:TEMP "mouse-gaze-job-config.xml"
$utf8 = New-Object System.Text.UTF8Encoding $false
[System.IO.File]::WriteAllText($tempConfig, $config, $utf8)

$create = curl.exe -sS -o "$env:TEMP\mouse-gaze-jenkins-create.txt" -w "%{http_code}" -u $auth `
    -H "$($crumb.crumbRequestField): $($crumb.crumb)" `
    -H "Content-Type: application/xml" `
    --data-binary "@$tempConfig" `
    "$JenkinsUrl/createItem?name=$JobName"

if ($create -eq "200" -or $create -eq "201") {
    Write-Output "Created pipeline $JobName at $JenkinsUrl/job/$JobName/"
    exit 0
}

$createBody = ""
if (Test-Path "$env:TEMP\mouse-gaze-jenkins-create.txt") {
    $createBody = Get-Content -Raw "$env:TEMP\mouse-gaze-jenkins-create.txt"
}
if ($create -eq "400" -and $createBody -match "already exists") {
    $update = curl.exe -sS -o "$env:TEMP\mouse-gaze-jenkins-update.txt" -w "%{http_code}" -u $auth `
        -H "$($crumb.crumbRequestField): $($crumb.crumb)" `
        -H "Content-Type: application/xml" `
        --data-binary "@$tempConfig" `
        -X POST `
        "$JenkinsUrl/job/$JobName/config.xml"
    if ($update -eq "200") {
        Write-Output "Updated pipeline $JobName at $JenkinsUrl/job/$JobName/"
        exit 0
    }
    Write-Output (Get-Content -Raw "$env:TEMP\mouse-gaze-jenkins-update.txt")
    throw "Jenkins returned HTTP $update while updating $JobName."
}

Write-Output (Get-Content -Raw "$env:TEMP\mouse-gaze-jenkins-create.txt")
throw "Jenkins returned HTTP $create while creating $JobName."
