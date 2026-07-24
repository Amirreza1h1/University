$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$originalLocation = Get-Location
$results = @()

$scenarios = @(
    [PSCustomObject]@{
        Name = "default"
        Directory = "scenario-01-default"
        ExpectedInventory = "Final inventory: {A=2, B=0}"
        ExpectedBuyers = "Successful buyers: [1B, 2B]"
        ExtraMarkers = @()
    },
    [PSCustomObject]@{
        Name = "all-a"
        Directory = "scenario-02-all-a"
        ExpectedInventory = "Final inventory: {A=0, B=2}"
        ExpectedBuyers = "Successful buyers: [1B, 2B]"
        ExtraMarkers = @()
    },
    [PSCustomObject]@{
        Name = "balanced"
        Directory = "scenario-03-balanced"
        ExpectedInventory = "Final inventory: {A=0, B=0}"
        ExpectedBuyers = "Successful buyers: [1B, 2B, 3B, 4B]"
        ExtraMarkers = @()
    },
    [PSCustomObject]@{
        Name = "refusal-stock"
        Directory = "scenario-04-refusal-stock"
        ExpectedInventory = "Final inventory: {A=0, B=1}"
        ExpectedBuyers = "Successful buyers: [1B, 2B, 4B]"
        ExtraMarkers = @("[3B] Purchase refused", "[4B] Purchase successful: B")
    },
    [PSCustomObject]@{
        Name = "restriction-priority"
        Directory = "scenario-05-restriction-priority"
        ExpectedInventory = "Final inventory: {A=2, B=0}"
        ExpectedBuyers = "Successful buyers: [1B, 2B]"
        ExtraMarkers = @("[4B] Purchase failed", "[3B] Purchase refused")
    }
)

function Wait-ForPort7778Free {
    param([int]$TimeoutSeconds = 15)

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    do {
        $listener = Get-NetTCPConnection -LocalPort 7778 -State Listen -ErrorAction SilentlyContinue
        if (-not $listener) {
            return $true
        }
        Start-Sleep -Milliseconds 250
    } while ((Get-Date) -lt $deadline)

    return $false
}

try {
    Set-Location -LiteralPath $projectRoot

    Write-Host "Building project once with mvn clean package..."
    & mvn clean package
    if ($LASTEXITCODE -ne 0) {
        throw "Maven package failed with exit code $LASTEXITCODE"
    }

    foreach ($scenario in $scenarios) {
        if (-not (Wait-ForPort7778Free)) {
            throw "Port 7778 did not become free before scenario '$($scenario.Name)'."
        }

        $scenarioDirectory = Join-Path $projectRoot "docs\screenshots\$($scenario.Directory)"
        New-Item -ItemType Directory -Path $scenarioDirectory -Force | Out-Null
        $logPath = Join-Path $scenarioDirectory "run-output.txt"

        Write-Host ""
        Write-Host "Running scenario '$($scenario.Name)' in non-GUI mode..."
        $javaArguments = @(
            "-Djava.net.preferIPv4Stack=true",
            "-Dmas.gui=false",
            "-Dmas.scenario=$($scenario.Name)",
            "-Dmas.initialBuyerDelayMs=0",
            "-cp",
            "target\classes;lib\jade.jar",
            "ir.ac.mas.shop.Main"
        )

        # Windows PowerShell 5 represents native stderr as non-terminating ErrorRecord
        # objects. JADE logs normal platform information to stderr, so temporarily keep
        # those records as output without weakening error handling for the rest of script.
        $previousErrorActionPreference = $ErrorActionPreference
        $ErrorActionPreference = "Continue"
        $consoleOutput = @(& java @javaArguments 2>&1)
        $javaExitCode = $LASTEXITCODE
        $ErrorActionPreference = $previousErrorActionPreference
        $consoleOutput = @($consoleOutput | Where-Object {
            $_.ToString() -ne "System.Management.Automation.RemoteException"
        })
        $consoleOutput | Set-Content -LiteralPath $logPath -Encoding UTF8
        $consoleOutput | ForEach-Object { Write-Host $_ }

        $completeOutput = $consoleOutput -join [Environment]::NewLine
        $requiredMarkers = @(
            $scenario.ExpectedInventory,
            $scenario.ExpectedBuyers,
            "Processed requests: 4"
        ) + $scenario.ExtraMarkers

        $missingMarkers = @($requiredMarkers | Where-Object {
            -not $completeOutput.Contains($_)
        })
        $passed = $javaExitCode -eq 0 -and $missingMarkers.Count -eq 0

        $results += [PSCustomObject]@{
            Scenario = $scenario.Name
            ExitCode = $javaExitCode
            Passed = $passed
            MissingMarkers = $missingMarkers -join "; "
            Log = $logPath
        }

        if (-not (Wait-ForPort7778Free)) {
            throw "Port 7778 did not become free after scenario '$($scenario.Name)'."
        }
    }

    Write-Host ""
    Write-Host "Scenario run summary:"
    $results | Format-Table Scenario, ExitCode, Passed, MissingMarkers -AutoSize

    $failed = @($results | Where-Object { -not $_.Passed })
    if ($failed.Count -gt 0) {
        Write-Error "$($failed.Count) scenario run(s) failed validation."
        exit 1
    }

    Write-Host "All five scenarios passed."
    exit 0
} finally {
    Set-Location -LiteralPath $originalLocation
}
