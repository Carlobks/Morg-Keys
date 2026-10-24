<#
  Desfaz o instalar.ps1 para o utilizador atual. Não apaga nada de forma definitiva:
  a pasta ~\.glzr é movida para ~\.glzr.removido-<data> (pode apagá-la depois à mão), e as pastas
  do próprio Zebar (definições e cache do WebView2) da mesma forma.
  Os programas (GlazeWM, Python, Visual C++) e a fonte ficam instalados;
  para os remover: Definições > Aplicações > Aplicações instaladas.

  Estrutura (como o instalar.ps1): cada passo é uma função e a desinstalação é a função Desinstalar,
  chamada na última linha só quando o ficheiro é corrido (DESINSTALAR.cmd). Carregado com
  ". desinstalar.ps1" (testes em tests\desinstalar.Tests.ps1) só define as funções.
#>
$Casa = $env:USERPROFILE
$Glzr = Join-Path $Casa '.glzr'
# Pastas que o próprio Zebar cria (definições e a cache do WebView2): saem com o resto.
$PastasDoZebar = @((Join-Path $env:APPDATA 'zebar'), (Join-Path $env:LOCALAPPDATA 'com.glzr.zebar'))
$GlazeCli = "$env:ProgramFiles\glzr.io\GlazeWM\cli\glazewm.exe"
$py = Join-Path $env:windir 'py.exe'
function Passo($m) { Write-Host ""; Write-Host "==> $m" -ForegroundColor Cyan }
function Info($m)  { Write-Host "    $m" }
function Aviso($m) { Write-Host "    ! $m" -ForegroundColor Yellow }

# --- Cola com o Windows: funções finas, fora da cobertura (motivos em tests\desinstalar.Tests.ps1) ---
function GlazeSair { try { & $GlazeCli command wm-exit 2>$null | Out-Null } catch {} }
function MostrarJanelasEscondidas($uncloak) { powershell -NoProfile -ExecutionPolicy Bypass -File $uncloak | Out-Null }
function PastaDocumentos { [Environment]::GetFolderPath('MyDocuments') }
function RemoverJuncao($caminho) { cmd /c rmdir "$caminho" | Out-Null }  # A10: nunca Remove-Item numa junction
function CorrerPython($script, $argumentos) {
  try { return (& $py -I $script @argumentos 2>&1 | Out-String).Trim() } catch { return "$_" }
}

# ---------------------------------------------------------------------------
function LerEstado {
  # -ErrorAction Stop: sem o ficheiro, o erro cai no catch (antes aparecia a vermelho no ecrã).
  try { return Get-Content (Join-Path $Glzr 'instalacao.json') -Raw -Encoding UTF8 -ErrorAction Stop | ConvertFrom-Json }
  catch { return $null }
}

function RemoverTarefa {
  # A do ecrã preto ao entrar (protetor "Em branco"), registada pelo instalar.ps1 com o mesmo nome.
  Unregister-ScheduledTask -TaskName 'Morg Keys (ecrã preto)' -Confirm:$false -ErrorAction SilentlyContinue
  Unregister-ScheduledTask -TaskName 'GlazeWM (arranque)' -Confirm:$false -ErrorAction SilentlyContinue
  if (Get-ScheduledTask -TaskName 'GlazeWM (arranque)' -ErrorAction SilentlyContinue) {
    # Criada com privilégios de administrador: só sai com eles. Sem a configuração
    # (~\.glzr), a tarefa arranca e não faz nada, mas convém tirá-la.
    Aviso 'Não consegui remover a tarefa "GlazeWM (arranque)" (foi criada como administrador).'
    Info 'Para a remover: PowerShell como administrador e  schtasks /Delete /TN "GlazeWM (arranque)" /F'
  } else {
    Info 'Tarefa "GlazeWM (arranque)" removida.'
  }
}

function FecharAmbiente {
  if ((Get-Process glazewm -ErrorAction SilentlyContinue) -and (Test-Path $GlazeCli)) { GlazeSair; Start-Sleep 2 }
  Get-Process glazewm, zebar -ErrorAction SilentlyContinue | Stop-Process -Force
  # pythonw do "café" (impede a suspensão) e dos ícones dos programas .bat; e o WebView2 do Zebar,
  # que ficaria a prender a pasta da cache (com.glzr.zebar).
  Get-CimInstance Win32_Process -Filter "Name='pythonw.exe' OR Name='python.exe' OR Name='msedgewebview2.exe'" |
    Where-Object { $_.CommandLine -match '\.glzr|com\.glzr\.zebar' } |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
  # Janelas que o GlazeWM tenha deixado escondidas ("cloaked") voltam a aparecer.
  $uncloak = Join-Path $Glzr 'zebar\omarchy-catppuccin\uncloak.ps1'
  if (Test-Path $uncloak) { MostrarJanelasEscondidas $uncloak; Info 'Janelas escondidas repostas.' }
  Info 'Os programas .bat de arranque.txt que estavam a correr continuam; feche-os pelo Gestor de Tarefas se quiser.'
}

function ReporAmbienteDeTrabalho($estado) {
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
}

function TirarStatusLine {
  $cfg = Join-Path $Casa '.claude\settings.json'
  if (-not (Test-Path $cfg)) { return }
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
  $r = CorrerPython $tmp @($cfg)
  Remove-Item $tmp
  if ($r -eq 'removida') { Info 'statusLine removida do settings.json (o ficheiro statusline.py ficou).' } else { Info 'Nada a mudar.' }
}

# Move uma pasta para <pasta>.removido-<data> (nada se apaga). Uma pasta ainda em uso fica, com aviso.
function MoverParaRemovido($pasta, $data) {
  if (-not (Test-Path $pasta)) { return }
  $destino = "$pasta.removido-$data"
  try { Rename-Item $pasta $destino -ErrorAction Stop; Info "$pasta movida para $destino" }
  catch { Aviso "Não consegui mover $pasta (em uso?): apague-a à mão depois de reiniciar." }
}

function MoverFicheiros($estado) {
  $juncao = Join-Path (PastaDocumentos) 'Guia de Atalhos'
  if ((Test-Path $juncao) -and ((Get-Item $juncao -Force).Attributes -band [IO.FileAttributes]::ReparsePoint)) {
    RemoverJuncao $juncao   # rmdir tira só o atalho; Remove-Item -Recurse apagaria o conteúdo
    Info 'Atalho Documentos\Guia de Atalhos removido.'
  }
  $data = Get-Date -Format yyyyMMdd-HHmmss
  foreach ($pasta in @($Glzr) + $PastasDoZebar) { MoverParaRemovido $pasta $data }
  if ($estado -and $estado.copia_anterior -and (Test-Path $estado.copia_anterior)) {
    Info "Havia uma configuração anterior em $($estado.copia_anterior) (pode renomeá-la para .glzr para a recuperar)."
  }
}

# ---------------------------------------------------------------------------
function Desinstalar {
  $ErrorActionPreference = 'Continue'
  $estado = LerEstado
  Passo 'Arranque automático'
  RemoverTarefa
  Passo 'A fechar GlazeWM, Zebar e os ajudantes'
  FecharAmbiente
  Passo 'Ambiente de trabalho do Windows'
  ReporAmbienteDeTrabalho $estado
  Passo 'Claude Code'
  TirarStatusLine
  Passo 'Ficheiros'
  MoverFicheiros $estado
  Passo 'Concluído'
  Info 'Programas e fonte continuam instalados: Definições > Aplicações > Aplicações instaladas (GlazeWM, Python 3.11, Visual C++).'
  Info 'Termine a sessão e volte a entrar para ficar tudo como antes.'
}

# Ponto de entrada: corrido pelo DESINSTALAR.cmd desinstala; carregado com ". desinstalar.ps1" (testes) só define as funções.
if ($MyInvocation.InvocationName -ne '.') { Desinstalar }
