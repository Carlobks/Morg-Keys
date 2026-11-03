<#
  Fecha o ambiente que estiver a correr antes de a reinstalação trocar os ficheiros do ~\.glzr, sem deixar janelas
  escondidas (P6). Carregado pelo instalar.ps1 com ". instalar-ambiente-antigo.ps1" (só define variáveis e funções).
  Testes em tests\instalar-ambiente-antigo.Tests.ps1 e tests\instalar-configuracao.Tests.ps1; preparação em
  tests\instalar-ambiente-antigo.Preparacao.ps1.
#>

$GlazeCli = "$env:ProgramFiles\glzr.io\GlazeWM\cli\glazewm.exe"
# Tempo que o ajudante "after-exit" pode levar: até 20 s à espera de o GlazeWM sair (after_exit, no
# morg_acoes_windows.py) e, no uncloak.ps1, até 20 s pelo GlazeWM e pelo vigia, mais 2 s; o resto é folga.
$EsperaDoAfterExit = 45

# Cola com o Windows (fora da cobertura, em tests\instalar-ambiente-antigo.Preparacao.ps1).
function GlazeSair { try { & $GlazeCli command wm-exit 2>$null | Out-Null } catch {} }
function MatarArvore($id) { taskkill /PID $id /T /F 2>$null | Out-Null }
function MostrarJanelasEscondidas($uncloak) {
  powershell -NoProfile -ExecutionPolicy Bypass -File $uncloak -WaitForGlazeExit | Out-Null
}

function FecharAmbienteAntigo {
  $glazeCorria = $false
  if (Test-Path $GlazeCli) {
    # Reinstalação: fecha o que estiver a correr antes de trocar os ficheiros.
    if (Get-Process glazewm -ErrorAction SilentlyContinue) { $glazeCorria = $true; GlazeSair; Start-Sleep 2 }
    Get-Process zebar -ErrorAction SilentlyContinue | Stop-Process -Force
  }
  # Ajudantes ainda a correr (café, ícones dos .bat com os seus programas): fecham-se com os
  # filhos, senão a tarefa lança outra cópia de cada .bat e a pasta pode não se deixar renomear.
  # O "after-exit" fica: é ele que volta a mostrar as janelas que o GlazeWM deixou escondidas (A54).
  $ajudantes = @(Get-CimInstance Win32_Process -Filter "Name='pythonw.exe' OR Name='python.exe'" |
    Where-Object { $_.CommandLine -match '\.glzr' })
  $ajudantes | Where-Object { $_.CommandLine -notmatch 'after-exit' } | ForEach-Object { MatarArvore $_.ProcessId }
  ReporJanelasEscondidas @($ajudantes | Where-Object { $_.CommandLine -match 'after-exit' }) $glazeCorria
}

# Espera que o after-exit acabe (ele corre o uncloak.ps1); se não houver ou não acabar a tempo, o instalador corre
# o uncloak.ps1. O registo da instalação diz qual dos caminhos correu.
function ReporJanelasEscondidas($afterExit, $glazeCorria) {
  if ($afterExit.Count -gt 0) {
    if (EsperarQueAcabem $afterExit.ProcessId $EsperaDoAfterExit) {
      Info 'Janelas escondidas repostas pelo ajudante after-exit.'
      return
    }
    Aviso "O ajudante after-exit não acabou em $EsperaDoAfterExit s: fecha-se e o instalador corre o uncloak.ps1."
    $afterExit | ForEach-Object { MatarArvore $_.ProcessId }
  }
  $uncloak = Join-Path $Glzr 'zebar\omarchy-catppuccin\uncloak.ps1'
  if (($glazeCorria -or $afterExit.Count -gt 0) -and (Test-Path $uncloak)) {
    MostrarJanelasEscondidas $uncloak
    Info 'Janelas escondidas repostas pelo instalador (uncloak.ps1).'
  }
}
function EsperarQueAcabem($ids, $segundos) {
  for ($i = 0; $i -lt $segundos * 2; $i++) {
    if (-not (Get-Process -Id $ids -ErrorAction SilentlyContinue)) { return $true }
    Start-Sleep -Milliseconds 500
  }
  return $false
}
