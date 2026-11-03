<#
  Fecha o ambiente que estiver a correr antes de a reinstalação trocar os ficheiros do ~\.glzr.
  Carregado pelo instalar.ps1 com ". instalar-ambiente-antigo.ps1" (só define o $GlazeCli e funções).
  Testes em tests\instalar-configuracao.Tests.ps1; preparação em tests\instalar-ambiente-antigo.Preparacao.ps1.
#>

$GlazeCli = "$env:ProgramFiles\glzr.io\GlazeWM\cli\glazewm.exe"

# Cola com o Windows (fora da cobertura, em tests\instalar-ambiente-antigo.Preparacao.ps1).
function GlazeSair { try { & $GlazeCli command wm-exit 2>$null | Out-Null } catch {} }
function MatarArvore($id) { taskkill /PID $id /T /F 2>$null | Out-Null }

function FecharAmbienteAntigo {
  if (Test-Path $GlazeCli) {
    # Reinstalação: fecha o que estiver a correr antes de trocar os ficheiros.
    if (Get-Process glazewm -ErrorAction SilentlyContinue) { GlazeSair; Start-Sleep 2 }
    Get-Process zebar -ErrorAction SilentlyContinue | Stop-Process -Force
  }
  # Ajudantes ainda a correr (café, ícones dos .bat com os seus programas): fecham-se com os
  # filhos, senão a tarefa lança outra cópia de cada .bat e a pasta pode não se deixar renomear.
  Get-CimInstance Win32_Process -Filter "Name='pythonw.exe' OR Name='python.exe'" |
    Where-Object { $_.CommandLine -match '\.glzr' } |
    ForEach-Object { MatarArvore $_.ProcessId }
}
