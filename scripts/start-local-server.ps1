param(
  [int]$Port = 8000,
  [string]$Bind = "localhost"
)

$ErrorActionPreference = "Stop"
$root = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")

& (Join-Path $PSScriptRoot "write-local-google-maps-config.ps1")

Set-Location -LiteralPath $root
Write-Host "Serving http://$Bind`:$Port/"

$python = Get-Command python -ErrorAction SilentlyContinue
if ($python) {
  & $python.Source -m http.server $Port --bind $Bind
  return
}

$node = Get-Command node -ErrorAction SilentlyContinue
if (-not $node) {
  throw "Neither python nor node was found on PATH. Install one of them or serve this directory with a static file server."
}

$env:LOCAL_STATIC_PORT = [string]$Port
$env:LOCAL_STATIC_BIND = $Bind
$serverCode = @'
const http = require("http");
const fs = require("fs");
const path = require("path");

const root = process.cwd();
const port = Number(process.env.LOCAL_STATIC_PORT || 8000);
const bind = process.env.LOCAL_STATIC_BIND || "127.0.0.1";
const types = {
  ".html": "text/html; charset=utf-8",
  ".js": "application/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".svg": "image/svg+xml",
  ".png": "image/png"
};

http.createServer((request, response) => {
  const url = new URL(request.url, `http://${bind}:${port}`);
  let pathname = decodeURIComponent(url.pathname);
  if (pathname === "/") pathname = "/index.html";

  const file = path.resolve(root, `.${pathname}`);
  const relative = path.relative(root, file);
  if (relative.startsWith("..") || path.isAbsolute(relative)) {
    response.writeHead(403);
    response.end("forbidden");
    return;
  }

  const stream = fs.createReadStream(file);
  stream.on("open", () => {
    response.writeHead(200, { "content-type": types[path.extname(file)] || "application/octet-stream" });
  });
  stream.on("error", () => {
    response.writeHead(404);
    response.end("not found");
  });
  stream.pipe(response);
}).listen(port, bind);
'@

& $node.Source -e $serverCode
