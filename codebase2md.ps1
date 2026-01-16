param (
    [Parameter(Mandatory=$true)]
    [string]$Path,

    [Parameter(Mandatory=$true)]
    [string]$Extension,

    [string]$OutFile
)

$ErrorActionPreference = "Stop"

# Resolve the absolute path of the target directory
if (-not (Test-Path -Path $Path -PathType Container)) {
    Write-Error "Directory not found: $Path"
    exit 1
}

$ResolvedPath = (Resolve-Path $Path).Path
$FolderName = Split-Path $ResolvedPath -Leaf

# Normalize Extension (remove * and . to get the clean extension name, e.g., "py")
$CleanExtension = $Extension.TrimStart("*").TrimStart(".")
# Create the wildcard pattern for filtering (e.g., "*.py")
$SearchPattern = "*.$CleanExtension"

# Determine default output filename if not provided
if ([string]::IsNullOrWhiteSpace($OutFile)) {
    $OutFile = Join-Path $PWD "$($FolderName)_$($CleanExtension).md"
}

# Find all matching files recursively
$Files = Get-ChildItem -Path $ResolvedPath -Filter $SearchPattern -Recurse -File

if ($Files.Count -eq 0) {
    Write-Warning "No files found with extension .$CleanExtension in $ResolvedPath"
    exit
}

# Initialize (create/overwrite) the output file
$null | Out-File -FilePath $OutFile -Encoding utf8

Write-Host "Found $($Files.Count) files. Processing..."

foreach ($File in $Files) {
    # Calculate relative path for the header
    $RelativePath = $File.FullName.Substring($ResolvedPath.Length)
    if ($RelativePath.StartsWith("\") -or $RelativePath.StartsWith("/")) {
        $RelativePath = $RelativePath.Substring(1)
    }

    # Read file content
    $Content = Get-Content -LiteralPath $File.FullName -Raw

    # Construct the Markdown entry parts to avoid complex string interpolation errors

    # 1. Path and Start of Code Block
    $Header = "$RelativePath`r`n`r`n" + '```' + $CleanExtension
    $Header | Out-File -FilePath $OutFile -Append -Encoding utf8

    # 2. File Content
    $Content | Out-File -FilePath $OutFile -Append -Encoding utf8

    # 3. End of Code Block and Spacing
    $Footer = '```' + "`r`n"
    $Footer | Out-File -FilePath $OutFile -Append -Encoding utf8
}

Write-Host "Successfully exported code to: $OutFile"
