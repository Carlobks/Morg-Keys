# Comando único de testes do Morg Keys (só lê o repositório; não arranca o GlazeWM nem o Zebar — A2).
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts\testar.ps1
# Sai com 0 se todos os testes passarem e 1 se algum falhar.
# O lint (ruff, PSScriptAnalyzer, Biome) por agora só informa: passa a bloquear depois da refatoração
# (fase 2 da experiência 0001), quando o código antigo for reescrito.

# Continue: no PowerShell 5.1 o stderr dos programas nativos vira erro e pararia o script; conta o $LASTEXITCODE.
$ErrorActionPreference = 'Continue'
$Raiz = Split-Path -Parent $PSScriptRoot
$Pack = Join-Path $Raiz '2-configuracao\glzr\zebar\omarchy-catppuccin'
$Py = 'C:\Windows\py.exe'
$Falhas = New-Object System.Collections.Generic.List[string]

function Write-Titulo([string]$Texto) { Write-Output ''; Write-Output "== $Texto" }

Push-Location $Raiz
try {
    # 1. Python: unittest com cobertura de linhas e ramos. Sem -I: o coverage está nos pacotes do utilizador.
    Write-Titulo 'Python (unittest + coverage)'
    & $Py -m coverage run --branch "--source=$Pack,tests" -m unittest discover -s tests
    if ($LASTEXITCODE -ne 0) { $Falhas.Add('Python') }
    & $Py -m coverage report --skip-empty

    # 2. JavaScript: node --test, se houver testes.
    $TestesJs = @(Get-ChildItem -Path (Join-Path $Raiz 'tests') -Recurse -Filter '*.test.mjs' -ErrorAction SilentlyContinue)
    if ($TestesJs.Count -gt 0) {
        Write-Titulo 'JavaScript (node --test)'
        & node --test ($TestesJs | ForEach-Object { $_.FullName })
        if ($LASTEXITCODE -ne 0) { $Falhas.Add('JavaScript') }
    }

    # 3. PowerShell: Pester 6, se houver testes.
    $TestesPs = @(Get-ChildItem -Path (Join-Path $Raiz 'tests') -Recurse -Filter '*.Tests.ps1' -ErrorAction SilentlyContinue)
    if ($TestesPs.Count -gt 0) {
        Write-Titulo 'PowerShell (Pester)'
        Import-Module Pester -MinimumVersion 6.0
        $Resultado = Invoke-Pester -Path ($TestesPs | ForEach-Object { $_.FullName }) -PassThru -Output Normal
        if ($Resultado.FailedCount -gt 0) { $Falhas.Add('PowerShell') }
    }

    # 4. Lint (informativo).
    Write-Titulo 'Lint (informativo)'
    & $Py -m ruff check --statistics .
    Import-Module PSScriptAnalyzer
    Invoke-ScriptAnalyzer -Path (Join-Path $Raiz 'scripts') -Recurse |
        Group-Object Severity, RuleName | Select-Object Count, Name | Format-Table -AutoSize | Out-String -Width 200
    cmd /c 'npx --no-install biome lint 2>&1' | Select-String -Pattern '^Found '
}
finally {
    Pop-Location
}

Write-Titulo 'Resultado'
if ($Falhas.Count -gt 0) {
    Write-Output ("FALHOU: " + ($Falhas -join ', '))
    exit 1
}
Write-Output 'OK: todos os testes passaram.'
exit 0
