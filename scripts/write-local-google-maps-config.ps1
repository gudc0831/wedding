param(
  [string]$EnvPath = ".env",
  [string]$OutputPath = "assets/google-maps-config.local.json"
)

$ErrorActionPreference = "Stop"

function Read-DotEnv {
  param([string]$Path)

  $values = @{}
  if (-not (Test-Path -LiteralPath $Path)) {
    return $values
  }

  Get-Content -LiteralPath $Path | ForEach-Object {
    $line = $_.Trim()
    if (-not $line -or $line.StartsWith("#")) {
      return
    }

    $separatorIndex = $line.IndexOf("=")
    if ($separatorIndex -lt 1) {
      return
    }

    $key = $line.Substring(0, $separatorIndex).Trim()
    $value = $line.Substring($separatorIndex + 1).Trim()
    if (($value.StartsWith('"') -and $value.EndsWith('"')) -or ($value.StartsWith("'") -and $value.EndsWith("'"))) {
      $value = $value.Substring(1, $value.Length - 2)
    }

    $values[$key] = $value
  }

  return $values
}

function Convert-ToBoolean {
  param([object]$Value)

  if ($null -eq $Value) {
    return $false
  }

  $text = "$Value".Trim().ToLowerInvariant()
  return $text -in @("1", "true", "yes", "y", "on")
}

function Read-JsonConfig {
  param([string]$Path)

  if (-not (Test-Path -LiteralPath $Path)) {
    return $null
  }

  try {
    return Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json -ErrorAction Stop
  } catch {
    return $null
  }
}

$root = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
Set-Location -LiteralPath $root

$outputFullPath = Join-Path $root $OutputPath
$existingConfig = Read-JsonConfig -Path $outputFullPath

$dotenv = Read-DotEnv -Path $EnvPath
$apiKey = if ($env:GOOGLE_MAPS_API_KEY) { $env:GOOGLE_MAPS_API_KEY } elseif ($dotenv["GOOGLE_MAPS_API_KEY"]) { $dotenv["GOOGLE_MAPS_API_KEY"] } else { $existingConfig.apiKey }
$mapId = if ($env:GOOGLE_MAPS_MAP_ID) { $env:GOOGLE_MAPS_MAP_ID } elseif ($dotenv["GOOGLE_MAPS_MAP_ID"]) { $dotenv["GOOGLE_MAPS_MAP_ID"] } else { $existingConfig.mapId }
$routeEngine = if ($env:GOOGLE_MAPS_ROUTE_ENGINE) { $env:GOOGLE_MAPS_ROUTE_ENGINE } elseif ($dotenv["GOOGLE_MAPS_ROUTE_ENGINE"]) { $dotenv["GOOGLE_MAPS_ROUTE_ENGINE"] } else { $existingConfig.googleRouteEngine }
$authReferrerPolicy = if ($env:GOOGLE_MAPS_AUTH_REFERRER_POLICY) { $env:GOOGLE_MAPS_AUTH_REFERRER_POLICY } elseif ($dotenv["GOOGLE_MAPS_AUTH_REFERRER_POLICY"]) { $dotenv["GOOGLE_MAPS_AUTH_REFERRER_POLICY"] } else { $existingConfig.authReferrerPolicy }
$placesEnrichment = if ($env:GOOGLE_MAPS_PLACES_ENRICHMENT) { $env:GOOGLE_MAPS_PLACES_ENRICHMENT } elseif ($dotenv["GOOGLE_MAPS_PLACES_ENRICHMENT"]) { $dotenv["GOOGLE_MAPS_PLACES_ENRICHMENT"] } else { $existingConfig.googlePlacesEnrichment }
$mapMonthlyLimit = if ($env:GOOGLE_MAPS_MAP_MONTHLY_LIMIT) { $env:GOOGLE_MAPS_MAP_MONTHLY_LIMIT } elseif ($dotenv["GOOGLE_MAPS_MAP_MONTHLY_LIMIT"]) { $dotenv["GOOGLE_MAPS_MAP_MONTHLY_LIMIT"] } else { $existingConfig.googleMapMonthlyLimit }
$routeComputeMonthlyLimit = if ($env:GOOGLE_MAPS_ROUTE_COMPUTE_MONTHLY_LIMIT) { $env:GOOGLE_MAPS_ROUTE_COMPUTE_MONTHLY_LIMIT } elseif ($dotenv["GOOGLE_MAPS_ROUTE_COMPUTE_MONTHLY_LIMIT"]) { $dotenv["GOOGLE_MAPS_ROUTE_COMPUTE_MONTHLY_LIMIT"] } else { $existingConfig.googleRouteComputeMonthlyLimit }
$placesMonthlyLimit = if ($env:GOOGLE_MAPS_PLACES_MONTHLY_LIMIT) { $env:GOOGLE_MAPS_PLACES_MONTHLY_LIMIT } elseif ($dotenv["GOOGLE_MAPS_PLACES_MONTHLY_LIMIT"]) { $dotenv["GOOGLE_MAPS_PLACES_MONTHLY_LIMIT"] } else { $existingConfig.googlePlacesMonthlyLimit }

$normalizedRouteEngine = "$routeEngine".Trim().ToLowerInvariant()
if ($normalizedRouteEngine -eq "") {
  $normalizedRouteEngine = "routes"
} elseif ($normalizedRouteEngine -in @("embed", "iframe", "google-embed")) {
  $normalizedRouteEngine = "embed"
} else {
  $normalizedRouteEngine = "routes"
}

if ($normalizedRouteEngine -eq "routes" -and (-not $apiKey -or $apiKey -eq "your-google-maps-api-key")) {
  throw "GOOGLE_MAPS_ROUTE_ENGINE=routes requires GOOGLE_MAPS_API_KEY. Create .env from .env.example or set the environment variable before starting the local site."
}

if ($normalizedRouteEngine -eq "embed" -and (-not $apiKey -or $apiKey -eq "your-google-maps-api-key")) {
  throw "GOOGLE_MAPS_ROUTE_ENGINE=embed without GOOGLE_MAPS_API_KEY would create a keyless local config. Restore .env or a keyed assets/google-maps-config.local.json before starting the local site."
}

$config = [ordered]@{
  apiKey = if ($apiKey -and $apiKey -ne "your-google-maps-api-key") { $apiKey } else { "" }
  language = "ko"
  region = "IT"
  routeMapProvider = "google"
  googleRouteEngine = $normalizedRouteEngine
  googlePlacesEnrichment = if ($null -ne $placesEnrichment -and "$placesEnrichment" -ne "") { Convert-ToBoolean -Value $placesEnrichment } else { $true }
  googleMapMonthlyLimit = if ($mapMonthlyLimit) { [int]$mapMonthlyLimit } else { 990 }
  googleRouteComputeMonthlyLimit = if ($routeComputeMonthlyLimit) { [int]$routeComputeMonthlyLimit } else { 990 }
  googlePlacesMonthlyLimit = if ($placesMonthlyLimit) { [int]$placesMonthlyLimit } else { 990 }
}

if ($authReferrerPolicy) {
  $config.authReferrerPolicy = $authReferrerPolicy
}

if ($mapId -and $mapId -ne "your-google-maps-map-id") {
  $config.mapId = $mapId
} elseif ($normalizedRouteEngine -eq "routes") {
  $config.mapId = "DEMO_MAP_ID"
}

$outputDirectory = Split-Path -Parent $outputFullPath
if ($outputDirectory -and -not (Test-Path -LiteralPath $outputDirectory)) {
  New-Item -ItemType Directory -Path $outputDirectory | Out-Null
}

$config | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $outputFullPath -Encoding UTF8
Write-Host "Wrote local Google Maps config to $OutputPath"
