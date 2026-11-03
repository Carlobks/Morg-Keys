# Reinstalar sem esconder as janelas (scripts\instalar-ambiente-antigo.ps1, P6): o ajudante "after-exit" volta a
# mostrar as janelas que o GlazeWM deixou escondidas depois de ele sair; o instalador espera por ele em vez de o
# fechar e, sem ele, corre o uncloak.ps1. Preparação em instalar.Preparacao.ps1 (carrega o instalador inteiro).

BeforeAll { . (Join-Path $PSScriptRoot 'instalar.Preparacao.ps1') }

Describe 'Reinstalar sem esconder as janelas' {
  BeforeEach {
    Limpar
    Escrever $GlazeCli ''
    $script:Uncloak = Join-Path $Glzr 'zebar\omarchy-catppuccin\uncloak.ps1'
    Escrever $script:Uncloak ''
    Mock GlazeSair {}
    Mock MatarArvore {}
    Mock MostrarJanelasEscondidas {}
    Mock Get-Process { 'glazewm' } -ParameterFilter { $Name -eq 'glazewm' }
    Mock Get-CimInstance {
      [pscustomobject]@{ CommandLine = 'pythonw.exe -I C:\u\.glzr\zebar\omarchy-catppuccin\bar_helper.py after-exit'; ProcessId = 21 },
      [pscustomobject]@{ CommandLine = 'pythonw.exe -I C:\u\.glzr\x\bat_tray.py a.bat'; ProcessId = 11 }
    }
  }
  It 'não fecha o after-exit: espera que ele acabe e fecha os outros ajudantes' {
    $script:Voltas = 0
    Mock Get-Process { $script:Voltas++; if ($script:Voltas -le 3) { 'pythonw' } } -ParameterFilter { $Id -contains 21 }
    FecharAmbienteAntigo
    Should -Invoke MatarArvore -Times 0 -Exactly -ParameterFilter { $id -eq 21 }
    Should -Invoke MatarArvore -Times 1 -Exactly -ParameterFilter { $id -eq 11 }
    Should -Invoke Get-Process -Times 4 -Exactly -ParameterFilter { $Id -contains 21 }
    Should -Invoke MostrarJanelasEscondidas -Times 0 -Exactly
    Registado | Should -Match 'repostas pelo ajudante after-exit'
  }
  It 'sem o after-exit, o instalador corre o uncloak.ps1' {
    Mock Get-CimInstance { [pscustomobject]@{ CommandLine = 'pythonw.exe -I C:\u\.glzr\x\bat_tray.py a.bat'; ProcessId = 11 } }
    FecharAmbienteAntigo
    Should -Invoke MostrarJanelasEscondidas -Times 1 -Exactly -ParameterFilter { $uncloak -eq $script:Uncloak }
    Registado | Should -Match 'repostas pelo instalador \(uncloak\.ps1\)'
  }
  It 'o after-exit não acaba a tempo: fecha-o e corre o uncloak.ps1' {
    Mock Get-Process { 'pythonw' } -ParameterFilter { $Id -contains 21 }
    FecharAmbienteAntigo
    Should -Invoke Get-Process -Times 90 -Exactly -ParameterFilter { $Id -contains 21 }
    Should -Invoke MatarArvore -Times 1 -Exactly -ParameterFilter { $id -eq 21 }
    Should -Invoke MostrarJanelasEscondidas -Times 1 -Exactly
    Registado | Should -Match 'after-exit não acabou em 45 s'
  }
  It 'com o GlazeWM fechado, ou sem o uncloak.ps1, não mostra janelas' {
    Mock Get-Process {} -ParameterFilter { $Name -eq 'glazewm' }
    Mock Get-CimInstance {}
    FecharAmbienteAntigo
    Remove-Item $script:Uncloak
    Mock Get-Process { 'glazewm' } -ParameterFilter { $Name -eq 'glazewm' }
    FecharAmbienteAntigo
    Should -Invoke MostrarJanelasEscondidas -Times 0 -Exactly
  }
}
