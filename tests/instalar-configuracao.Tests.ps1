# Instalador (scripts\instalar.ps1), 2.ª parte: cópia para o perfil (no TestDrive), personalizações,
# atalho em Documentos, apps, statusLine, ambiente de trabalho, tarefa agendada e a ordem dos passos.
# Preparação (bombas, pastas no TestDrive, funções excluídas da cobertura) em instalar.Comum.ps1.

BeforeAll { . (Join-Path $PSScriptRoot 'instalar.Comum.ps1') }

Describe 'Fechar o ambiente antigo e guardar a cópia' {
  BeforeEach {
    Limpar
    Mock GlazeSair {}
    Mock MatarArvore {}
    Mock Stop-Process {}
    Mock Get-CimInstance { [pscustomobject]@{ CommandLine = 'pythonw.exe -I C:\u\.glzr\x\bat_tray.py a.bat'; ProcessId = 11 },
                           [pscustomobject]@{ CommandLine = 'python.exe outro.py'; ProcessId = 12 } }
  }
  It 'fecha o GlazeWM, o Zebar e os ajudantes de ~\.glzr' {
    Escrever $GlazeCli ''
    Mock Get-Process { 'glazewm' } -ParameterFilter { $Name -eq 'glazewm' }
    Mock Get-Process { [pscustomobject]@{ Name = 'zebar' } } -ParameterFilter { $Name -eq 'zebar' }
    FecharAmbienteAntigo
    Should -Invoke GlazeSair -Times 1 -Exactly
    Should -Invoke Start-Sleep -Times 1 -Exactly
    Should -Invoke Stop-Process -Times 1 -Exactly
    Should -Invoke MatarArvore -Times 1 -Exactly -ParameterFilter { $id -eq 11 }
  }
  It 'sem o GlazeWM instalado ou sem ele a correr só fecha os ajudantes' {
    FecharAmbienteAntigo
    Should -Invoke Get-Process -Times 0 -Exactly
    Escrever $GlazeCli ''
    FecharAmbienteAntigo
    Should -Invoke GlazeSair -Times 0 -Exactly
    Should -Invoke MatarArvore -Times 2 -Exactly
  }
  It 'guarda a configuração anterior com a data' {
    GuardarCopiaAnterior | Should -BeNullOrEmpty
    Escrever (Join-Path $Glzr 'layout.json') '{}'
    $copia = GuardarCopiaAnterior
    $copia | Should -BeLike "$Glzr.copia-*"
    Test-Path $Glzr | Should -BeFalse
    Ler (Join-Path $copia 'layout.json') | Should -Be '{}'
  }
}

Describe 'Modelos copiados para o perfil' {
  BeforeEach { Limpar }
  It 'TextoDoModelo troca {{HOME}} e {{HOME_RE}} (com \ dobrado para o JSON)' {
    $Casa = 'C:\Users\a.b'
    TextoDoModelo 'glazewm\config.yaml' '{{HOME}}/x {{HOME_RE}} {{ANIMACAO}}' 'lua' @() |
      Should -Be 'C:/Users/a.b/x C:/Users/a\\.b {{ANIMACAO}}'
  }
  It 'no arranque.txt põe a animação (cafe por omissão) e acrescenta os .bat' {
    $rel = "$Pack\guia\arranque.txt"
    TextoDoModelo $rel "animacao = {{ANIMACAO}}`n`n" 'lua' @('bat = a', 'bat = b') | Should -Be "animacao = lua`nbat = a`nbat = b`n"
    TextoDoModelo $rel "animacao = {{ANIMACAO}}`n" $null @() | Should -Be "animacao = cafe`n"
  }
  It 'copia os modelos: texto com os marcadores trocados, binários tal como estão' {
    $modelos = Join-Path $Pacote '2-configuracao\glzr'
    Escrever (Join-Path $modelos 'glazewm\config.yaml') 'casa: {{HOME}}'
    Escrever (Join-Path $modelos "$Pack\guia\arranque.txt") 'animacao = {{ANIMACAO}}'
    Escrever (Join-Path $modelos "$Pack\arranque\cafe.bmp") 'BM {{HOME}}'
    CopiarModelos 'cafe' @('bat = x')
    Ler (Join-Path $Glzr 'glazewm\config.yaml') | Should -Be "casa: $($Casa -replace '\\', '/')"
    Ler (Join-Path $Glzr "$Pack\guia\arranque.txt") | Should -Be "animacao = cafe`nbat = x`n"
    Ler (Join-Path $Glzr "$Pack\arranque\cafe.bmp") | Should -Be 'BM {{HOME}}'
  }
  It 'VerificarMarcadores para se ficou algum {{ (menos nos registos de arranque\)' {
    Escrever (Join-Path $Glzr 'arranque\servidor.txt') 'log com {{ legítimo'
    Escrever (Join-Path $Glzr 'glazewm\config.yaml') 'ok'
    VerificarMarcadores
    Registado | Should -Match 'Configuração copiada para'
    Escrever (Join-Path $Glzr 'zebar\x.json') '{{HOME}}'
    { VerificarMarcadores } | Should -Throw 'Sair'
    Registado | Should -Match 'Ficaram marcadores por substituir: .*x\.json'
  }
}

Describe 'Personalizações da instalação anterior' {
  BeforeEach {
    Limpar
    $copia = "$Glzr.copia-1"
    New-Item -ItemType Directory -Force (Join-Path $Glzr "$Pack\guia") | Out-Null
  }
  It 'sem cópia não faz nada' {
    ManterPersonalizacoes $null $true
    Registado | Should -Be ''
  }
  It 'mantém registos, layout.json, apps.txt (estrutura antiga) e o arranque.txt, trocando a animação antiga' {
    Escrever (Join-Path $copia 'arranque\servidor.log') 'registo'
    Escrever (Join-Path $copia 'layout.json') '{"windows": []}'
    Escrever (Join-Path $copia 'zebar\guia-atalhos\apps.txt') 'Alt+B = Brave'
    Escrever (Join-Path $copia "$Pack\guia\arranque.txt") "# x`nanimação = lua`nbat = y`n"
    ManterPersonalizacoes $copia $true
    Ler (Join-Path $Glzr 'arranque\servidor.log') | Should -Be 'registo'
    Ler (Join-Path $Glzr 'layout.json') | Should -Be '{"windows": []}'
    Ler (Join-Path $Glzr "$Pack\guia\apps.txt") | Should -Be 'Alt+B = Brave'
    Ler (Join-Path $Glzr "$Pack\guia\arranque.txt") | Should -Be "# x`nanimação = cafe`nbat = y`n"
    Registado | Should -Match 'arranque.txt: animação antiga trocada por cafe\.'
  }
  It 'sem manter o arranque, com a animação certa ou sem arranque.txt não troca nada' {
    Escrever (Join-Path $copia "$Pack\guia\arranque.txt") 'animacao = lua'
    Escrever (Join-Path $Glzr "$Pack\guia\arranque.txt") 'animacao = cafe'
    ManterPersonalizacoes $copia $false
    Ler (Join-Path $Glzr "$Pack\guia\arranque.txt") | Should -Be 'animacao = cafe'
    Remove-Item (Join-Path $Glzr "$Pack\guia\arranque.txt")
    ManterPersonalizacoes $copia $false
    Registado | Should -Not -Match 'trocada|mantido'
  }
}

Describe 'Atalho em Documentos' {
  BeforeEach {
    Limpar
    $docs = Join-Path $TestDrive 'docs'
    New-Item -ItemType Directory -Force $docs, (Join-Path $Glzr "$Pack\guia") | Out-Null
    $juncao = Join-Path $docs 'Guia de Atalhos'
    Mock PastaDocumentos { Join-Path $TestDrive 'docs' }
    Mock RemoverJuncao { [IO.Directory]::Delete($caminho) }
  }
  AfterEach { if (Test-Path $juncao) { [IO.Directory]::Delete($juncao) } }
  It 'cria a junction para a pasta do guia' {
    CriarAtalhoNosDocumentos
    (Get-Item $juncao -Force).Attributes -band [IO.FileAttributes]::ReparsePoint | Should -BeTrue
    Should -Invoke RemoverJuncao -Times 0 -Exactly
  }
  It 'troca uma junction antiga' {
    CriarAtalhoNosDocumentos
    CriarAtalhoNosDocumentos
    Should -Invoke RemoverJuncao -Times 1 -Exactly
    Test-Path $juncao | Should -BeTrue
  }
  It 'não mexe numa pasta normal com o mesmo nome' {
    New-Item -ItemType Directory $juncao | Out-Null
    CriarAtalhoNosDocumentos
    Registado | Should -Match 'Já existe uma pasta normal'
    (Get-Item $juncao -Force).Attributes -band [IO.FileAttributes]::ReparsePoint | Should -BeFalse
  }
}

Describe 'Apps e statusLine do Claude Code' {
  BeforeEach {
    Limpar
    Mock CorrerAppsApply {}
    Escrever (Join-Path $Pacote '2-configuracao\claude\statusline.py') 'novo'
  }
  It 'avisa as apps que não existem neste PC' {
    Escrever (Join-Path $Glzr "$Pack\guia\apps.txt") "# (não encontrada neste PC) Alt+B = Brave`nAlt+O = Obsidian`n"
    AplicarApps
    Should -Invoke CorrerAppsApply -ParameterFilter { $helper -eq (Join-Path $Glzr "$Pack\bar_helper.py") }
    Registado | Should -Match '! sem a app: Alt\+B = Brave'
    Registado | Should -Match 'Instale-as e tire o #'
    Escrever (Join-Path $Glzr "$Pack\guia\apps.txt") "Alt+O = Obsidian`n"
    AplicarApps
    Registado | Should -Match 'Todas as apps de apps.txt foram encontradas\.'
  }
  It 'sem o Claude Code não mexe' {
    ConfigurarStatusLine | Should -BeFalse
    Registado | Should -Match 'Claude Code não instalado'
  }
  It 'guarda a statusline.py diferente e junta a statusLine ao settings.json' {
    Escrever (Join-Path $Casa '.claude\statusline.py') 'velho'
    Mock CorrerPython { 'ok' }
    ConfigurarStatusLine | Should -BeTrue
    Ler (Join-Path $Casa '.claude\statusline.py.bak') | Should -Be 'velho'
    Ler (Join-Path $Casa '.claude\statusline.py') | Should -Be 'novo'
    $esperado = "C:/Windows/py.exe -I `"$($Casa -replace '\\', '/')/.claude/statusline.py`""
    Should -Invoke CorrerPython -ParameterFilter { $argumentos[0] -eq (Join-Path $Casa '.claude\settings.json') -and $argumentos[1] -eq $esperado }
  }
  It 'só com o claude.exe; outra statusLine ou erro não se tocam' {
    Escrever (Join-Path $Casa '.local\bin\claude.exe') ''
    Mock CorrerPython { 'mantido' }
    ConfigurarStatusLine | Should -BeFalse
    Test-Path (Join-Path $Casa '.claude\statusline.py.bak') | Should -BeFalse
    Registado | Should -Match 'já tem outra statusLine'
    Mock CorrerPython { 'Traceback' }
    ConfigurarStatusLine | Should -BeFalse
    Test-Path (Join-Path $Casa '.claude\statusline.py.bak') | Should -BeFalse  # igual ao novo: não guarda
    Registado | Should -Match 'Não consegui alterar ~\\\.claude\\settings\.json \(Traceback\)'
  }
}

Describe 'Ambiente de trabalho do Windows' {
  BeforeEach {
    Limpar
    New-Item -ItemType Directory -Force $Glzr | Out-Null
    Mock Get-ItemProperty { [pscustomobject]@{ HideIcons = 0 } } -ParameterFilter { $Name -eq 'HideIcons' }
    Mock Get-ItemProperty { [pscustomobject]@{ Settings = [byte[]](0..15) } } -ParameterFilter { $Name -eq 'Settings' }
    Mock Set-ItemProperty {}
    Mock Stop-Process {}
    Mock Start-Process {}
  }
  It 'esconde os ícones e a barra, guarda o estado de antes e reinicia o Explorador' {
    AjustarAmbienteDeTrabalho 'C:\copia' $true
    Should -Invoke Set-ItemProperty -ParameterFilter { $Name -eq 'HideIcons' -and $Value -eq 1 }
    Should -Invoke Set-ItemProperty -ParameterFilter { $Name -eq 'Settings' -and $Value[8] -eq 3 }
    Should -Invoke Stop-Process -ParameterFilter { $Name -eq 'explorer' }
    Should -Invoke Start-Process -ParameterFilter { $FilePath -eq 'explorer.exe' }
    $estado = Get-Content (Join-Path $Glzr 'instalacao.json') -Raw | ConvertFrom-Json
    ($estado.copia_anterior, $estado.statusline, $estado.hideicons_antes, $estado.barra_antes) | Should -Be @('C:\copia', $true, 0, 8)
  }
  It 'com -ManterIcones e -ManterBarraWindows não muda nada' {
    $ManterIcones = $true
    $ManterBarraWindows = $true
    AjustarAmbienteDeTrabalho $null $false
    Should -Invoke Set-ItemProperty -Times 0 -Exactly
    Should -Invoke Stop-Process -Times 0 -Exactly
  }
  It 'sem a chave da barra; o Explorador que volta sozinho não se abre outra vez' {
    Mock Get-ItemProperty {} -ParameterFilter { $Name -eq 'Settings' }
    Mock Get-Process { 'explorer' } -ParameterFilter { $Name -eq 'explorer' }
    AjustarAmbienteDeTrabalho $null $false
    Should -Invoke Set-ItemProperty -Times 1 -Exactly
    Should -Invoke Start-Process -Times 0 -Exactly
    (Get-Content (Join-Path $Glzr 'instalacao.json') -Raw | ConvertFrom-Json).PSObject.Properties.Name | Should -Not -Contain 'barra_antes'
  }
}

Describe 'Tarefa agendada e fim' {
  BeforeEach {
    Limpar
    New-Item -ItemType Directory -Force $Glzr | Out-Null
    $argumentos = "-I `"$(Join-Path $Glzr "$Pack\bar_helper.py")`" boot"
  }
  It 'regista a tarefa do boot' {
    Mock Register-ScheduledTask {}
    RegistarTarefa  # as New-ScheduledTask* só criam os objetos (não mexem no Agendador)
    Should -Invoke Register-ScheduledTask -ParameterFilter { $TaskName -eq 'GlazeWM (arranque)' -and $Force -and
      $Action.Execute -eq $pyw -and $Action.Arguments -eq $argumentos -and $Settings.Priority -eq 4 -and
      $Principal.RunLevel -eq 'Limited' -and $Trigger.UserId -eq "$env:USERDOMAIN\$env:USERNAME" }
    Registado | Should -Match "Tarefa 'GlazeWM \(arranque\)' registada"
  }
  It 'sem poder substituir: serve a antiga se fizer o mesmo; senão para' {
    Mock Register-ScheduledTask { throw 'Acesso negado' }
    Mock Get-ScheduledTask { [pscustomobject]@{ Actions = @([pscustomobject]@{ Execute = $pyw.ToUpper(); Arguments = $argumentos }) } }
    RegistarTarefa
    Registado | Should -Match 'já existia \(criada como administrador\) e faz o mesmo'
    Mock Get-ScheduledTask { [pscustomobject]@{ Actions = @([pscustomobject]@{ Execute = $pyw; Arguments = 'outro' }) } }
    { RegistarTarefa } | Should -Throw 'Sair'
    Mock Get-ScheduledTask {}
    { RegistarTarefa } | Should -Throw 'Sair'
    Registado | Should -Match 'Não consegui criar a tarefa de arranque \(Acesso negado\)'
  }
  It 'Concluir guarda o registo e arranca já (ou não, com -NaoIniciar)' {
    Escrever $Registo "Instalação`n"
    Mock Start-ScheduledTask {}
    Concluir
    Should -Invoke Start-ScheduledTask -Times 1 -Exactly -ParameterFilter { $TaskName -eq 'GlazeWM (arranque)' }
    Test-Path (Join-Path $Glzr 'instalacao.log') | Should -BeTrue
    $NaoIniciar = $true
    Concluir
    Should -Invoke Start-ScheduledTask -Times 1 -Exactly
    Registado | Should -Match 'Termine a sessão e volte a entrar'
  }
}

Describe 'Instalar (a ordem dos passos)' {
  It 'corre os passos pela ordem e passa o que cada um decide ao seguinte' {
    Limpar
    $ordem = [System.Collections.Generic.List[string]]::new()
    foreach ($f in 'Verificar', 'InstalarProgramas', 'InstalarFontes', 'FecharAmbienteAntigo', 'CopiarModelos',
                   'ManterPersonalizacoes', 'VerificarMarcadores', 'CriarAtalhoNosDocumentos', 'AplicarApps',
                   'AjustarAmbienteDeTrabalho', 'RegistarTarefa', 'Concluir') {
      Mock $f ([scriptblock]::Create("`$ordem.Add('$f')"))
    }
    Mock EscolherArranque { $ordem.Add('EscolherArranque'); @{ Manter = $true; Animacao = 'lua'; Linhas = @('bat = x') } }
    Mock GuardarCopiaAnterior { $ordem.Add('GuardarCopiaAnterior'); 'C:\copia' }
    Mock ConfigurarStatusLine { $ordem.Add('ConfigurarStatusLine'); $true }
    Instalar
    $ordem | Should -Be @('Verificar', 'InstalarProgramas', 'InstalarFontes', 'EscolherArranque', 'FecharAmbienteAntigo',
      'GuardarCopiaAnterior', 'CopiarModelos', 'ManterPersonalizacoes', 'VerificarMarcadores', 'CriarAtalhoNosDocumentos',
      'AplicarApps', 'ConfigurarStatusLine', 'AjustarAmbienteDeTrabalho', 'RegistarTarefa', 'Concluir')
    Should -Invoke CopiarModelos -ParameterFilter { $animacao -eq 'lua' -and $linhasBat -contains 'bat = x' }
    Should -Invoke ManterPersonalizacoes -ParameterFilter { $copia -eq 'C:\copia' -and $manterArranque }
    Should -Invoke AjustarAmbienteDeTrabalho -ParameterFilter { $copia -eq 'C:\copia' -and $statusAplicado }
    (Get-Content $Registo -Encoding UTF8)[0] | Should -Match '^Instalação \d{4}-\d\d-\d\dT'
    Registado | Should -Match '==> Arranque automático \(tarefa agendada\)'
  }
}
