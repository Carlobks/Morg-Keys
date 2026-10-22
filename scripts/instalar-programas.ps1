# Parte do instalar.ps1 que precisa de administrador (é chamada por ele com UAC).
# Instala só o que falta: Visual C++ (runtime), GlazeWM + Zebar, Python (com o py.exe em C:\Windows).
param([Parameter(Mandatory)][string]$Pacote, [Parameter(Mandatory)][string]$Registo)
$ErrorActionPreference = 'Continue'
$inst = Join-Path $Pacote '1-instaladores'
function Log($m) { Add-Content -Path $Registo -Value "[admin] $m" -Encoding UTF8 }

function Correr($exe, $argumentos) {
  Log "a instalar $(Split-Path $exe -Leaf) ..."
  $p = Start-Process -FilePath $exe -ArgumentList $argumentos -Wait -PassThru
  if ($p.ExitCode -in 0, 1638, 3010) { Log "  ok (código $($p.ExitCode))" } else { Log "  ERRO: código $($p.ExitCode)" }
}

# 1. Visual C++ 2015-2022 x64
$vc = Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64' -ErrorAction SilentlyContinue
if ($vc -and $vc.Installed -eq 1) { Log 'Visual C++ já instalado' }
else { Correr (Join-Path $inst 'VisualC++-Redistribuivel-x64.exe') '/install /quiet /norestart' }

# 2. GlazeWM (inclui o Zebar)
$glaze = Join-Path $env:ProgramFiles 'glzr.io\GlazeWM\glazewm.exe'
$zebar = Join-Path $env:ProgramFiles 'glzr.io\Zebar\zebar.exe'
if ((Test-Path $glaze) -and (Test-Path $zebar)) { Log 'GlazeWM e Zebar já instalados' }
else { Correr (Join-Path $inst 'GlazeWM-3.10.1-com-Zebar.exe') '/quiet /norestart' }

# O arranque é feito pela tarefa agendada do instalar.ps1: tira arranques automáticos
# que o instalador do GlazeWM/Zebar possa ter criado (para não arrancarem duas vezes).
foreach ($k in 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run', 'HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Run') {
  $p = Get-ItemProperty $k -ErrorAction SilentlyContinue
  if ($p) { $p.PSObject.Properties | Where-Object { $_.Name -match 'glaze|zebar' } | ForEach-Object {
      Remove-ItemProperty -Path $k -Name $_.Name; Log "removido arranque automático $($_.Name) ($k)" } }
}
Get-ChildItem "$env:ProgramData\Microsoft\Windows\Start Menu\Programs\Startup" -ErrorAction SilentlyContinue |
  Where-Object { $_.Name -match 'glaze|zebar' } | ForEach-Object { Remove-Item $_.FullName; Log "removido atalho de arranque $($_.Name)" }

# 3. Python 3 (para todos os utilizadores, com o lançador C:\Windows\py.exe e pyw.exe)
$py = Join-Path $env:windir 'py.exe'
$pyOk = $false
if (Test-Path $py) {
  & $py -3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" 2>$null
  $pyOk = ($LASTEXITCODE -eq 0)
}
if ($pyOk) { Log 'Python 3.10+ e py.exe já instalados' }
else {
  Correr (Join-Path $inst 'Python-3.11.9-amd64.exe') `
    '/quiet InstallAllUsers=1 Include_launcher=1 InstallLauncherAllUsers=1 PrependPath=0 Include_test=0 Include_doc=0 Shortcuts=0'
}
Log 'fim da parte de administrador'
