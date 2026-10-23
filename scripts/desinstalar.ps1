<#
  Desfaz o instalar.ps1 para o utilizador atual. Não apaga nada de forma definitiva:
  a pasta ~\.glzr é movida para ~\.glzr.removido-<data> (pode apagá-la depois à mão).
  Os programas (GlazeWM, Python, Visual C++) e a fonte ficam instalados;
  para os remover: Definições > Aplicações > Aplicações instaladas.
#>
$ErrorActionPreference = 'Continue'
$Casa = $env:USERPROFILE
$Glzr = Join-Path $Casa '.glzr'
function Passo($m) { Write-Host ""; Write-Host "==> $m" -ForegroundColor Cyan }
function Info($m)  { Write-Host "    $m" }

$estado = $null
try { $estado = Get-Content (Join-Path $Glzr 'instalacao.json') -Raw -Encoding UTF8 | ConvertFrom-Json } catch {}

Passo 'Arranque automático'
Unregister-ScheduledTask -TaskName 'GlazeWM (arranque)' -Confirm:$false -ErrorAction SilentlyContinue
if (Get-ScheduledTask -TaskName 'GlazeWM (arranque)' -ErrorAction SilentlyContinue) {
  # Criada com privilégios de administrador: só sai com eles. Sem a configuração
  # (~\.glzr), a tarefa arranca e não faz nada, mas convém tirá-la.
  Write-Host '    ! Não consegui remover a tarefa "GlazeWM (arranque)" (foi criada como administrador).' -ForegroundColor Yellow
  Info 'Para a remover: PowerShell como administrador e  schtasks /Delete /TN "GlazeWM (arranque)" /F'
} else {
  Info 'Tarefa "GlazeWM (arranque)" removida.'
}

Passo 'A fechar GlazeWM, Zebar e os ajudantes'
$cli = "$env:ProgramFiles\glzr.io\GlazeWM\cli\glazewm.exe"
if ((Get-Process glazewm -ErrorAction SilentlyContinue) -and (Test-Path $cli)) { try { & $cli command wm-exit 2>$null | Out-Null } catch {}; Start-Sleep 2 }
Get-Process glazewm, zebar -ErrorAction SilentlyContinue | Stop-Process -Force
# pythonw do "café" (impede a suspensão) e dos ícones dos programas .bat
Get-CimInstance Win32_Process -Filter "Name='pythonw.exe' OR Name='python.exe'" |
  Where-Object { $_.CommandLine -match '\.glzr' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
# Janelas que o GlazeWM tenha deixado escondidas ("cloaked") voltam a aparecer.
$uncloak = Join-Path $Glzr 'zebar\omarchy-catppuccin\uncloak.ps1'
if (Test-Path $uncloak) { powershell -NoProfile -ExecutionPolicy Bypass -File $uncloak | Out-Null; Info 'Janelas escondidas repostas.' }
Info 'Os programas .bat de arranque.txt que estavam a correr continuam; feche-os pelo Gestor de Tarefas se quiser.'

Passo 'Ambiente de trabalho do Windows'
$adv = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced'
$hide = 0; if ($estado -and $null -ne $estado.hideicons_antes) { $hide = [int]$estado.hideicons_antes }
Set-ItemProperty $adv -Name HideIcons -Value $hide -Type DWord
$sr = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\StuckRects3'
$bin = (Get-ItemProperty $sr -Name Settings -ErrorAction SilentlyContinue).Settings
if ($bin) {
  $antes = 2; if ($estado -and $null -ne $estado.barra_antes) { $antes = [int]$estado.barra_antes }
  $bin[8] = [byte]$antes; Set-ItemProperty $sr -Name Settings -Value $bin
}
Stop-Process -Name explorer -Force; Start-Sleep 3
if (-not (Get-Process explorer -ErrorAction SilentlyContinue)) { Start-Process explorer.exe }
Info 'Ícones e barra de tarefas como estavam antes da instalação.'

Passo 'Claude Code'
$cfg = Join-Path $Casa '.claude\settings.json'
if (Test-Path $cfg) {
  $tmp = Join-Path $env:TEMP 'morg-keys-statusline-remove.py'
  [IO.File]::WriteAllText($tmp, @'
import json, pathlib, sys
p = pathlib.Path(sys.argv[1])
d = json.loads(p.read_text(encoding="utf-8-sig"))
if "statusline.py" in (d.get("statusLine") or {}).get("command", ""):
    del d["statusLine"]
    p.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("removida")
'@, (New-Object Text.UTF8Encoding $false))
  try { $r = & "$env:windir\py.exe" -I $tmp $cfg 2>&1 } catch { $r = "$_" }
  Remove-Item $tmp
  if ($r -eq 'removida') { Info 'statusLine removida do settings.json (o ficheiro statusline.py ficou).' } else { Info 'Nada a mudar.' }
}

Passo 'Ficheiros'
$juncao = Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'Guia de Atalhos'
if ((Test-Path $juncao) -and ((Get-Item $juncao -Force).Attributes -band [IO.FileAttributes]::ReparsePoint)) {
  cmd /c rmdir "$juncao" | Out-Null   # rmdir tira só o atalho; Remove-Item -Recurse apagaria o conteúdo
  Info 'Atalho Documentos\Guia de Atalhos removido.'
}
if (Test-Path $Glzr) {
  $destino = "$Glzr.removido-$(Get-Date -Format yyyyMMdd-HHmmss)"
  Rename-Item $Glzr $destino
  Info "Configuração movida para $destino"
}
if ($estado -and $estado.copia_anterior -and (Test-Path $estado.copia_anterior)) {
  Info "Havia uma configuração anterior em $($estado.copia_anterior) (pode renomeá-la para .glzr para a recuperar)."
}

Passo 'Concluído'
Info 'Programas e fonte continuam instalados: Definições > Aplicações > Aplicações instaladas (GlazeWM, Python 3.11, Visual C++).'
Info 'Termine a sessão e volte a entrar para ficar tudo como antes.'
