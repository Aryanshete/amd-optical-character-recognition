param(
    [string]$ImageName = "aryan-amd-ocr",
    [string]$TestImage = "sample_inputs\sample_01_california_plate.png"
)

$ErrorActionPreference = "Stop"

docker build -t $ImageName .

New-Item -ItemType Directory -Force -Path "input", "output" | Out-Null
$imgFileName = Split-Path $TestImage -Leaf
$imgStem = [System.IO.Path]::GetFileNameWithoutExtension($TestImage)
Copy-Item $TestImage "input\$imgFileName" -Force

$pwdPath = (Get-Location).Path
docker run --rm `
  -v "${pwdPath}/input:/app/input" `
  -v "${pwdPath}/output:/app/output" `
  $ImageName `
  python3 /app/app.py --input-image "/app/input/$imgFileName"

$outputFile = "output\${imgStem}_output.json"
if (Test-Path $outputFile) {
    Get-Content $outputFile
} else {
    Write-Host "Output $outputFile was not created" -ForegroundColor Red
    exit 1
}
