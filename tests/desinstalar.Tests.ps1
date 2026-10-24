# Desinstalador (scripts\desinstalar.ps1): tarefa, fechar o ambiente, ambiente de trabalho, statusLine e ficheiros.
# Preparação (bombas, pastas no TestDrive, funções excluídas da cobertura) em desinstalar.Comum.ps1.

BeforeAll { . (Join-Path $PSScriptRoot 'desinstalar.Comum.ps1') }

Describe 'Estado da instalação' {
  BeforeEach { Limpar }
  It 'lê o instalacao.json; sem ele, nada' {
    LerEstado | Should -BeNullOrEmpty
    Escrever (Join-Path $Glzr 'instalacao.json') '{"hideicons_antes": 0, "barra_antes": 2}'
    (LerEstado).barra_antes | Should -Be 2
  }
}

Describe 'Tarefa de arranque' {
  BeforeEach { Mock Unregister-ScheduledTask {} }
  It 'removida' {
    Mock Get-ScheduledTask {}
    RemoverTarefa
    Should -Invoke Unregister-ScheduledTask -ParameterFilter { $TaskName -eq 'GlazeWM (arranque)' }
    Should -Invoke Unregister-ScheduledTask -ParameterFilter { $TaskName -eq 'Morg Keys (ecrã preto)' }
    Should -Invoke Write-Host -ParameterFilter { $Object -eq '    Tarefa "GlazeWM (arranque)" removida.' }
  }
  It 'criada como administrador: avisa e diz como a tirar' {
    Mock Get-ScheduledTask { 'tarefa' }
    RemoverTarefa
    Should -Invoke Write-Host -ParameterFilter { $Object -match '! Não consegui remover a tarefa' }
    Should -Invoke Write-Host -ParameterFilter { $Object -match 'schtasks /Delete /TN "GlazeWM \(arranque\)" /F' }
  }
}

Describe 'Fechar o ambiente' {
  BeforeEach {
    Limpar
    Mock Stop-Process {}
    Mock GlazeSair {}
    Mock MostrarJanelasEscondidas {}
    Mock Get-CimInstance { @(
        [pscustomobject]@{ ProcessId = 11; CommandLine = 'pythonw.exe -I C:\Users\u\.glzr\x\bar_helper.py awake-hold' }
        [pscustomobject]@{ ProcessId = 22; CommandLine = 'msedgewebview2.exe --user-data-dir=C:\u\AppData\Local\com.glzr.zebar\EBWebView' }
        [pscustomobject]@{ ProcessId = 33; CommandLine = 'msedgewebview2.exe --user-data-dir=C:\u\Raycast\EBWebView' }) }
  }
  It 'pede ao GlazeWM para sair, fecha o Zebar, os ajudantes e o WebView2 do Zebar (só esses)' {
    Mock Get-Process { New-Object System.Diagnostics.Process }   # um processo vazio (o Stop-Process é falso)
    Escrever $GlazeCli ''
    Escrever (Join-Path $Glzr 'zebar\omarchy-catppuccin\uncloak.ps1') ''
    FecharAmbiente
    Should -Invoke GlazeSair -Times 1
    Should -Invoke Stop-Process -ParameterFilter { $Id -eq 11 } -Times 1
    Should -Invoke Stop-Process -ParameterFilter { $Id -eq 22 } -Times 1
    Should -Invoke Stop-Process -ParameterFilter { $Id -eq 33 } -Times 0
    Should -Invoke MostrarJanelasEscondidas -ParameterFilter { $uncloak -like '*uncloak.ps1' } -Times 1
  }
  It 'sem GlazeWM a correr nem uncloak.ps1 não os chama' {
    FecharAmbiente
    Should -Invoke GlazeSair -Times 0
    Should -Invoke MostrarJanelasEscondidas -Times 0
  }
}

Describe 'Ambiente de trabalho' {
  BeforeEach {
    Mock Set-ItemProperty {}
    Mock Stop-Process {}
    Mock Start-Process {}
  }
  It 'repõe os ícones e a barra como estavam e reabre o Explorador se não voltou sozinho' {
    Mock Get-ItemProperty { [pscustomobject]@{ Settings = [byte[]](0..15) } }
    ReporAmbienteDeTrabalho ([pscustomobject]@{ hideicons_antes = 1; barra_antes = 3 })
    Should -Invoke Set-ItemProperty -ParameterFilter { $Name -eq 'HideIcons' -and $Value -eq 1 }
    Should -Invoke Set-ItemProperty -ParameterFilter { $Name -eq 'Settings' -and $Value[8] -eq 3 }
    Should -Invoke Stop-Process -ParameterFilter { $Name -eq 'explorer' }
    Should -Invoke Start-Process -ParameterFilter { $FilePath -eq 'explorer.exe' } -Times 1
  }
  It 'sem estado: ícones à vista e barra fixa (os valores do Windows); sem StuckRects3 não mexe na barra' {
    Mock Get-ItemProperty { [pscustomobject]@{ Settings = [byte[]](0..15) } }
    ReporAmbienteDeTrabalho $null
    Should -Invoke Set-ItemProperty -ParameterFilter { $Name -eq 'HideIcons' -and $Value -eq 0 }
    Should -Invoke Set-ItemProperty -ParameterFilter { $Name -eq 'Settings' -and $Value[8] -eq 2 }
    Mock Get-ItemProperty {}
    Mock Get-Process { New-Object System.Diagnostics.Process }
    ReporAmbienteDeTrabalho $null
    Should -Invoke Set-ItemProperty -ParameterFilter { $Name -eq 'Settings' } -Times 1 -Exactly -Scope It
    Should -Invoke Start-Process -Times 1 -Exactly -Scope It
  }
}

Describe 'statusLine do Claude Code' {
  BeforeEach { Limpar }
  It 'sem settings.json não faz nada' {
    Mock CorrerPython { throw 'não devia correr' }
    TirarStatusLine
  }
  It 'tira a statusLine do Morg Keys; se não for a dele, nada a mudar' {
    Escrever (Join-Path $Casa '.claude\settings.json') '{}'
    Mock CorrerPython { 'removida' }
    TirarStatusLine
    Should -Invoke CorrerPython -ParameterFilter { $argumentos[0] -eq (Join-Path $Casa '.claude\settings.json') }
    Should -Invoke Write-Host -ParameterFilter { $Object -match 'statusLine removida' }
    Mock CorrerPython { '' }
    TirarStatusLine
    Should -Invoke Write-Host -ParameterFilter { $Object -eq '    Nada a mudar.' }
    Test-Path (Join-Path $env:TEMP 'morg-keys-statusline-remove.py') | Should -BeFalse
  }
}

Describe 'Ficheiros' {
  BeforeEach {
    Limpar
    $docs = Join-Path $TestDrive 'docs'
    New-Item -ItemType Directory -Force $docs | Out-Null
    Mock PastaDocumentos { Join-Path $TestDrive 'docs' }
    Mock RemoverJuncao {}
  }
  It 'tira a junction dos Documentos e move a ~\.glzr e as pastas do Zebar para .removido-<data>' {
    Escrever (Join-Path $Glzr 'x.txt') 'x'
    foreach ($p in $PastasDoZebar) { Escrever (Join-Path $p 'y.txt') 'y' }
    New-Item -ItemType Junction -Path (Join-Path $TestDrive 'docs\Guia de Atalhos') -Target $Casa | Out-Null
    $copia = Join-Path $TestDrive 'copia'
    New-Item -ItemType Directory -Force $copia | Out-Null
    MoverFicheiros ([pscustomobject]@{ copia_anterior = $copia })
    Should -Invoke RemoverJuncao -ParameterFilter { $caminho -eq (Join-Path $TestDrive 'docs\Guia de Atalhos') }
    foreach ($p in @($Glzr) + $PastasDoZebar) {
      Test-Path $p | Should -BeFalse
      @(Get-Item "$p.removido-*").Count | Should -Be 1
    }
    Should -Invoke Write-Host -ParameterFilter { $Object -match 'Havia uma configuração anterior' }
  }
  It 'uma pasta normal nos Documentos fica; o que não existe não se move' {
    New-Item -ItemType Directory -Force (Join-Path $TestDrive 'docs\Guia de Atalhos') | Out-Null
    MoverFicheiros $null
    Should -Invoke RemoverJuncao -Times 0
    @(Get-ChildItem $Casa -Filter '*.removido-*').Count | Should -Be 0
  }
  It 'uma pasta em uso fica, com aviso' {
    Escrever (Join-Path $Glzr 'x.txt') 'x'
    Mock Rename-Item { throw 'em uso' }
    MoverParaRemovido $Glzr '20261024-120000'
    Test-Path $Glzr | Should -BeTrue
    Should -Invoke Write-Host -ParameterFilter { $Object -match '! Não consegui mover .*\.glzr \(em uso\?\)' }
  }
}

Describe 'Desinstalar (a sequência)' {
  It 'corre os passos por ordem, com o estado lido no início' {
    $ordem = New-Object System.Collections.Generic.List[string]
    Mock LerEstado { 'estado' }
    Mock RemoverTarefa { $ordem.Add('RemoverTarefa') }
    Mock FecharAmbiente { $ordem.Add('FecharAmbiente') }
    Mock ReporAmbienteDeTrabalho { $ordem.Add("ReporAmbienteDeTrabalho $estado") }
    Mock TirarStatusLine { $ordem.Add('TirarStatusLine') }
    Mock MoverFicheiros { $ordem.Add("MoverFicheiros $estado") }
    Desinstalar
    $ordem | Should -Be @('RemoverTarefa', 'FecharAmbiente', 'ReporAmbienteDeTrabalho estado', 'TirarStatusLine',
      'MoverFicheiros estado')
    Should -Invoke Write-Host -ParameterFilter { $Object -match 'Programas e fonte continuam instalados' }
  }
}
