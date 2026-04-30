$ErrorActionPreference = 'Stop'

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot '..')
$outputDir = Join-Path $repoRoot 'output\google-map-routes'
$workDir = Join-Path ([System.IO.Path]::GetTempPath()) ('wedding-google-map-routes-' + [guid]::NewGuid().ToString('N'))
$rawDir = Join-Path $workDir 'raw'
$renderDir = Join-Path $workDir 'render'
$profileDir = Join-Path $workDir 'chrome-profile'

New-Item -ItemType Directory -Force -Path $outputDir, $rawDir, $renderDir, $profileDir | Out-Null

$chromeCandidates = @(
  'C:\Program Files\Google\Chrome\Application\chrome.exe',
  'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
  'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
  'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
)

$chrome = $chromeCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $chrome) {
  throw 'Chrome or Edge executable was not found.'
}

function Encode-MapSegment {
  param([Parameter(Mandatory = $true)][string]$Text)
  return ([System.Uri]::EscapeDataString($Text)).Replace("'", '%27')
}

function New-GoogleMapsRouteUrl {
  param(
    [Parameter(Mandatory = $true)][string[]]$Points,
    [Parameter(Mandatory = $true)][string]$Center,
    [Parameter(Mandatory = $true)][string]$Zoom,
    [Parameter(Mandatory = $true)][string]$ModeCode
  )

  $segments = ($Points | ForEach-Object { Encode-MapSegment $_ }) -join '/'
  return "https://www.google.com/maps/dir/$segments/@$Center,$Zoom/data=!4m2!4m1!$ModeCode`?hl=ko"
}

function ConvertTo-FileUri {
  param([Parameter(Mandatory = $true)][string]$Path)
  return ([System.Uri]((Resolve-Path $Path).Path)).AbsoluteUri
}

function Escape-Html {
  param([AllowNull()][string]$Text)
  return [System.Net.WebUtility]::HtmlEncode($Text)
}

function Wait-ForFile {
  param(
    [Parameter(Mandatory = $true)][string]$Path,
    [int]$TimeoutSeconds = 30
  )

  $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
  while ((Get-Date) -lt $deadline) {
    if ((Test-Path $Path) -and ((Get-Item $Path).Length -gt 0)) {
      return
    }
    Start-Sleep -Milliseconds 500
  }

  throw "Expected file was not created: $Path"
}

function Invoke-Chrome {
  param([Parameter(Mandatory = $true)][string[]]$Arguments)

  & $chrome @Arguments
  $exitCode = $LASTEXITCODE
  if ($null -ne $exitCode -and $exitCode -ne 0) {
    Write-Warning "Chrome exited with code $exitCode. Checking expected output file anyway."
  }
}

$routes = @(
  [pscustomobject]@{
    Key = '01_day1_arrival'
    Title = 'Day 1 | 07.21 도착일'
    Subtitle = 'Porta Nuova 첫날 산책'
    ModeLabel = '도보 중심'
    Center = '45.4788,9.1942'
    Zoom = '14z'
    ModeCode = '3e2'
    CropX = 220
    CropY = 70
    Points = @(
      'UNA HOTELS Century Milano, Milan, Italy',
      'Pavé Milano, Milan, Italy',
      'Porta Nuova, Milan, Italy',
      'Piazza Gae Aulenti, Milan, Italy',
      'BAM Biblioteca degli Alberi Milano, Milan, Italy',
      'Bosco Verticale, Milan, Italy',
      'Casa della Memoria, Milan, Italy',
      'Ratanà, Milan, Italy'
    )
    Labels = @(
      'UNA HOTELS Century Milano',
      'Pavé Milano',
      'Porta Nuova',
      'Piazza Gae Aulenti',
      'BAM Biblioteca degli Alberi',
      'Bosco Verticale',
      'Casa della Memoria',
      'Ratanà'
    )
    Backups = @('Eataly Milano Smeraldo', 'The Hall Bar & Restaurant')
  },
  [pscustomobject]@{
    Key = '02_day2_milan_core'
    Title = 'Day 2 | 07.22 밀라노 핵심'
    Subtitle = 'Duomo, Brera, Navigli'
    ModeLabel = '도보 + 짧은 대중교통'
    Center = '45.4623,9.1848'
    Zoom = '14z'
    ModeCode = '3e2'
    CropX = 220
    CropY = 70
    Points = @(
      'UNA HOTELS Century Milano, Milan, Italy',
      'Duomo di Milano, Milan, Italy',
      'Galleria Vittorio Emanuele II, Milan, Italy',
      'Rinascente Milano Duomo, Milan, Italy',
      'Marchesi 1824 Galleria, Milan, Italy',
      'Brera, Milan, Italy',
      'Pinacoteca di Brera, Milan, Italy',
      "N'Ombra de Vin, Milan, Italy",
      'Navigli, Milan, Italy',
      'Osteria del Binari, Milan, Italy'
    )
    Labels = @(
      'UNA HOTELS Century Milano',
      'Duomo di Milano',
      'Galleria Vittorio Emanuele II',
      'Rinascente Milano Duomo',
      'Marchesi 1824 Galleria',
      'Brera',
      'Pinacoteca di Brera',
      "N'Ombra de Vin",
      'Navigli',
      'Osteria del Binari'
    )
    Backups = @()
  },
  [pscustomobject]@{
    Key = '03_day3_birthday_shopping'
    Title = 'Day 3 | 07.23 생일·쇼핑'
    Subtitle = 'Montenapoleone 쇼핑과 기념일 디너'
    ModeLabel = '쇼핑 동선 참고'
    Center = '45.4683,9.1915'
    Zoom = '15z'
    ModeCode = '3e0'
    CropX = 220
    CropY = 70
    Points = @(
      'UNA HOTELS Century Milano, Milan, Italy',
      'Via Montenapoleone, Milan, Italy',
      'Quadrilatero della Moda, Milan, Italy',
      'Maio Restaurant & Terrace, Milan, Italy'
    )
    Labels = @(
      'UNA HOTELS Century Milano',
      'Via Montenapoleone',
      'Quadrilatero della Moda',
      'Maio Restaurant & Terrace'
    )
    Backups = @('Ceresio 7')
  },
  [pscustomobject]@{
    Key = '04_day4_como'
    Title = 'Day 4 | 07.24 꼬모'
    Subtitle = 'Varenna와 Bellagio 당일치기'
    ModeLabel = '광역 이동 + 현지 도보'
    Center = '45.8050,9.2380'
    Zoom = '10z'
    ModeCode = '3e0'
    CropX = 500
    CropY = 60
    Points = @(
      'UNA HOTELS Century Milano, Milan, Italy',
      'Milano Centrale, Milan, Italy',
      'Varenna, Italy',
      'Passeggiata degli Innamorati, Varenna, Italy',
      'Riva Grande, Varenna, Italy',
      'Bellagio, Italy',
      'B-Lake Restaurant Bellagio, Bellagio, Italy',
      'La Pergola Bellagio, Bellagio, Italy',
      'Punta Spartivento, Bellagio, Italy'
    )
    Labels = @(
      'UNA HOTELS Century Milano',
      'Milano Centrale',
      'Varenna',
      'Passeggiata degli Innamorati',
      'Riva Grande',
      'Bellagio',
      'Bellagio Restaurant & Bar',
      'La Pergola Bellagio',
      'Punta Spartivento'
    )
    Backups = @('Villa Monastero')
  },
  [pscustomobject]@{
    Key = '05_day5_bergamo'
    Title = 'Day 5 | 07.25 베르가모'
    Subtitle = 'Città Alta 역사 지구'
    ModeLabel = '광역 이동 + 현지 도보'
    Center = '45.6050,9.4180'
    Zoom = '11z'
    ModeCode = '3e0'
    CropX = 500
    CropY = 60
    Points = @(
      'UNA HOTELS Century Milano, Milan, Italy',
      'Milano Centrale, Milan, Italy',
      'Bergamo Città Alta, Bergamo, Italy',
      'Piazza Vecchia, Bergamo, Italy',
      'Basilica di Santa Maria Maggiore, Bergamo, Italy',
      'Cappella Colleoni, Bergamo, Italy',
      'Caffè del Tasso, Bergamo, Italy',
      'Il Circolino Città Alta, Bergamo, Italy',
      'Da Mimmo, Bergamo, Italy'
    )
    Labels = @(
      'UNA HOTELS Century Milano',
      'Milano Centrale',
      'Bergamo Città Alta',
      'Piazza Vecchia',
      'Basilica di Santa Maria Maggiore',
      'Cappella Colleoni',
      'Caffè del Tasso',
      'Il Circolino Città Alta',
      'Da Mimmo'
    )
    Backups = @('Mura Veneziane', 'San Vigilio')
  }
)

foreach ($route in $routes) {
  $rawPath = Join-Path $rawDir ($route.Key + '_google.png')
  $htmlPath = Join-Path $renderDir ($route.Key + '.html')
  $finalPath = Join-Path $outputDir ($route.Key + '.png')
  $captureProfile = Join-Path $profileDir ($route.Key + '-capture')
  $renderProfile = Join-Path $profileDir ($route.Key + '-render')
  New-Item -ItemType Directory -Force -Path $captureProfile, $renderProfile | Out-Null
  $mapsUrl = New-GoogleMapsRouteUrl -Points $route.Points -Center $route.Center -Zoom $route.Zoom -ModeCode $route.ModeCode

  Write-Host "Capturing Google Maps route: $($route.Key)"
  $captureArgs = @(
    '--headless',
    '--disable-gpu',
    '--disable-extensions',
    '--disable-background-networking',
    '--no-first-run',
    '--no-default-browser-check',
    '--lang=ko-KR',
    "--user-data-dir=$captureProfile",
    '--window-size=2100,1200',
    '--virtual-time-budget=18000',
    "--screenshot=$rawPath",
    $mapsUrl
  )
  Invoke-Chrome -Arguments $captureArgs
  Wait-ForFile -Path $rawPath -TimeoutSeconds 45

  $steps = for ($i = 0; $i -lt $route.Labels.Count; $i++) {
    $number = $i + 1
    '<li><span class="num">' + $number + '</span><span>' + (Escape-Html $route.Labels[$i]) + '</span></li>'
  }
  $stepsHtml = $steps -join "`n"

  if ($route.Backups.Count -gt 0) {
    $backupItems = ($route.Backups | ForEach-Object { '<span>' + (Escape-Html $_) + '</span>' }) -join ''
    $backupHtml = '<div class="backup"><b>Backup</b>' + $backupItems + '</div>'
  } else {
    $backupHtml = '<div class="backup muted"><b>Backup</b><span>별도 백업 장소 없음</span></div>'
  }

  $rawUri = ConvertTo-FileUri $rawPath
  $title = Escape-Html $route.Title
  $subtitle = Escape-Html $route.Subtitle
  $modeLabel = Escape-Html $route.ModeLabel
  $cropX = [int]$route.CropX
  $cropY = [int]$route.CropY

  $html = @"
<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    * { box-sizing: border-box; }
    body {
      margin: 0;
      width: 1600px;
      height: 1000px;
      overflow: hidden;
      font-family: "Malgun Gothic", "Segoe UI", Arial, sans-serif;
      background: #e9eef2;
      color: #17211d;
    }
    .stage {
      position: relative;
      width: 1600px;
      height: 1000px;
      overflow: hidden;
    }
    .map {
      position: absolute;
      left: -${cropX}px;
      top: -${cropY}px;
      width: 2100px;
      height: 1200px;
      max-width: none;
    }
    .shade {
      position: absolute;
      inset: 0;
      background:
        linear-gradient(90deg, rgba(10, 22, 20, .68), rgba(10, 22, 20, .16) 34%, rgba(10, 22, 20, 0) 62%),
        linear-gradient(0deg, rgba(255,255,255,.16), rgba(255,255,255,0) 30%);
      pointer-events: none;
    }
    .panel {
      position: absolute;
      left: 32px;
      top: 32px;
      width: 410px;
      max-height: 908px;
      padding: 24px 24px 20px;
      border-radius: 8px;
      background: rgba(255, 255, 255, .985);
      box-shadow: 0 18px 48px rgba(19, 38, 33, .25);
      border: 1px solid rgba(21, 49, 42, .12);
    }
    .eyebrow {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 6px 10px;
      border-radius: 999px;
      background: #e6f0ed;
      color: #17372f;
      font-size: 15px;
      font-weight: 700;
      line-height: 1;
      margin-bottom: 14px;
    }
    h1 {
      margin: 0 0 7px;
      font-size: 28px;
      line-height: 1.18;
      letter-spacing: 0;
      word-break: keep-all;
    }
    .subtitle {
      margin: 0 0 18px;
      font-size: 18px;
      color: #56645f;
      line-height: 1.38;
      font-weight: 600;
    }
    ol {
      list-style: none;
      padding: 0;
      margin: 0;
      display: grid;
      gap: 8px;
    }
    li {
      display: grid;
      grid-template-columns: 30px 1fr;
      align-items: start;
      gap: 10px;
      font-size: 15px;
      line-height: 1.32;
      font-weight: 700;
      color: #1d2c27;
    }
    .num {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 28px;
      height: 28px;
      border-radius: 50%;
      background: #17372f;
      color: white;
      font-size: 14px;
      font-weight: 800;
    }
    .backup {
      margin-top: 18px;
      display: flex;
      align-items: center;
      flex-wrap: wrap;
      gap: 8px;
      padding: 12px 14px;
      border-radius: 8px;
      background: rgba(255,255,255,.985);
      border: 1px solid rgba(121, 96, 56, .20);
      box-shadow: 0 14px 40px rgba(19, 38, 33, .20);
    }
    .backup b {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      height: 30px;
      padding: 0 12px;
      border-radius: 999px;
      background: #cda16a;
      color: #1f231d;
      font-size: 14px;
      font-weight: 800;
    }
    .backup span {
      display: inline-flex;
      align-items: center;
      min-height: 30px;
      padding: 0 10px;
      border-radius: 999px;
      background: rgba(205, 161, 106, .16);
      color: #31413b;
      font-size: 14px;
      font-weight: 700;
      white-space: nowrap;
    }
    .backup.muted span {
      background: #eef2f0;
      color: #6a756f;
    }
    .watermark {
      position: absolute;
      right: 32px;
      top: 32px;
      padding: 9px 12px;
      border-radius: 8px;
      background: rgba(255,255,255,.88);
      color: #42504b;
      font-size: 13px;
      font-weight: 700;
      box-shadow: 0 10px 28px rgba(19, 38, 33, .14);
    }
  </style>
</head>
<body>
  <div class="stage">
    <img class="map" src="$rawUri" alt="">
    <div class="shade"></div>
    <section class="panel">
      <div class="eyebrow">$modeLabel</div>
      <h1>$title</h1>
      <p class="subtitle">$subtitle</p>
      <ol>
        $stepsHtml
      </ol>
      $backupHtml
    </section>
    <div class="watermark">Google Maps capture + route overlay</div>
  </div>
</body>
</html>
"@

  [System.IO.File]::WriteAllText($htmlPath, $html, [System.Text.UTF8Encoding]::new($false))

  Write-Host "Rendering annotated image: $($route.Key)"
  $htmlUri = ConvertTo-FileUri $htmlPath
  $renderArgs = @(
    '--headless',
    '--disable-gpu',
    '--disable-extensions',
    '--disable-background-networking',
    '--no-first-run',
    '--no-default-browser-check',
    "--user-data-dir=$renderProfile",
    '--window-size=1600,1000',
    '--virtual-time-budget=3000',
    "--screenshot=$finalPath",
    $htmlUri
  )
  Invoke-Chrome -Arguments $renderArgs
  Wait-ForFile -Path $finalPath -TimeoutSeconds 30
}

Write-Host ''
Write-Host 'Created route images:'
Get-ChildItem $outputDir -Filter '*.png' |
  Sort-Object Name |
  Select-Object Name, Length |
  Format-Table -AutoSize
