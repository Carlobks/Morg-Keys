# Instalador (scripts\instalar.ps1), 1.ª parte: registo, verificações, programas, fonte e escolhas do arranque.
# Preparação (bombas, pastas no TestDrive, funções excluídas da cobertura) em instalar.Comum.ps1.

BeforeAll { . (Join-Path $PSScriptRoot 'instalar.Comum.ps1') }

Describe 'Registo e paragem' {
  BeforeEach { Limpar }
  It 'Passo, Info e Aviso escrevem no registo' {
    Passo 'Um'; Info 'dois'; Aviso 'três'
    Get-Content $Registo -Encoding UTF8 | Should -Be @('==> Um', '    dois', '    ! três')
  }
  It 'Parar escreve o erro e sai' {
    { Parar 'falhou' } | Should -Throw 'Sair'
    Registado | Should -Match 'ERRO: falhou'
  }
}

Describe 'Verificar' {
  BeforeEach {
    Limpar
    Escrever (Join-Path $Pacote 'LEIA-ME.txt') 'x'
    Mock BuildDoWindows { 26100 }
    Mock TipoDaUnidade { [IO.DriveType]::Fixed }
    Mock EAdministrador { $false }
    Mock Unblock-File {}
  }
  It 'para no Windows 10' {
    Mock BuildDoWindows { 19045 }
    { Verificar } | Should -Throw 'Sair'
    Registado | Should -Match 'É preciso Windows 11 \(este é o build 19045\)\.'
  }
  It 'para com espaços na pasta do utilizador' {
    $Casa = 'C:\Users\Ana Maria'
    { Verificar } | Should -Throw 'Sair'
    Registado | Should -Match 'tem espaços'
  }
  It 'para numa partilha de rede (sem perguntar ao disco) e numa unidade de rede' {
    $Pacote = '\\servidor\pacote'
    { Verificar } | Should -Throw 'Sair'
    Should -Invoke TipoDaUnidade -Times 0 -Exactly
    $Pacote = Join-Path $TestDrive 'pacote'
    Mock TipoDaUnidade { [IO.DriveType]::Network }
    { Verificar } | Should -Throw 'Sair'
    Registado | Should -Match 'pasta de rede'
  }
  It 'como administrador só continua com S' {
    Mock EAdministrador { $true }
    Mock Read-Host { 'n' }
    { Verificar } | Should -Throw 'Sair'
    Registado | Should -Match 'Está a correr como administrador'
    Mock Read-Host { 'S' }
    Verificar
    Registado | Should -Match 'Windows build 26100'
  }
  It 'tira a marca da internet aos ficheiros do pacote' {
    Verificar
    Should -Invoke Unblock-File
    Should -Invoke Read-Host -Times 0 -Exactly
  }
}

Describe 'Programas em falta' {
  It 'tudo instalado' {
    Mock Get-ItemProperty { [pscustomobject]@{ Installed = 1 } }
    Mock Test-Path { $true }
    Mock PythonServe { $true }
    (ProgramasEmFalta).Count | Should -Be 0
  }
  It 'nada instalado (sem py.exe nem se pergunta a versão)' {
    Mock Get-ItemProperty {}
    Mock Test-Path { $false }
    Mock PythonServe { $true }
    $falta = ProgramasEmFalta
    $falta | Should -Be @('Visual C++', 'GlazeWM/Zebar', 'Python')
    Should -Invoke PythonServe -Times 0 -Exactly
  }
  It 'Visual C++ por instalar, Zebar em falta e Python antigo' {
    Mock Get-ItemProperty { [pscustomobject]@{ Installed = 0 } }
    Mock Test-Path { $Path -notlike '*zebar.exe' }
    Mock PythonServe { $false }
    $falta = ProgramasEmFalta
    $falta | Should -Be @('Visual C++', 'GlazeWM/Zebar', 'Python')
  }
}

Describe 'Instaladores' {
  BeforeAll {
    Escrever (Join-Path $TestDrive 'certo.bin') 'certo'
    $HashCerto = (Get-FileHash (Join-Path $TestDrive 'certo.bin') -Algorithm SHA256).Hash
  }
  BeforeEach {
    Limpar
    Mock AtivarTls12 {}
    $Instaladores = @{ 'Python' = @{ Ficheiro = 'py.exe'; Url = 'https://exemplo/py.exe'; Sha256 = $HashCerto } }
    $destino = Join-Path $dirInst 'py.exe'
  }
  It 'InstaladorValido pelo hash' {
    InstaladorValido (Join-Path $TestDrive 'nao-existe') @{ Sha256 = $HashCerto } | Should -BeFalse
    InstaladorValido (Join-Path $TestDrive 'certo.bin') @{ Sha256 = $HashCerto } | Should -BeTrue
    InstaladorValido (Join-Path $TestDrive 'certo.bin') @{ Sha256 = 'ABC' } | Should -BeFalse
  }
  It 'InstaladorValido pela assinatura (campo O= exato)' {
    $i = @{ Assinante = 'O=Microsoft Corporation' }
    $ficheiro = Join-Path $TestDrive 'certo.bin'
    Mock Get-AuthenticodeSignature { [pscustomobject]@{ Status = 'Valid'; SignerCertificate = [pscustomobject]@{ Subject = 'CN=Microsoft, O=Microsoft Corporation, L=Redmond' } } }
    InstaladorValido $ficheiro $i | Should -BeTrue
    Mock Get-AuthenticodeSignature { [pscustomobject]@{ Status = 'Valid'; SignerCertificate = [pscustomobject]@{ Subject = 'CN=X, O=Microsoft Corporation Falsa' } } }
    InstaladorValido $ficheiro $i | Should -BeFalse
    Mock Get-AuthenticodeSignature { [pscustomobject]@{ Status = 'NotSigned'; SignerCertificate = $null } }
    InstaladorValido $ficheiro $i | Should -BeFalse
  }
  It 'usa o que já está em 1-instaladores' {
    Escrever $destino 'certo'
    ObterInstaladores @('Python')
    Should -Invoke Invoke-WebRequest -Times 0 -Exactly
    Registado | Should -Match 'Python: instalador já presente\.'
  }
  It 'descarrega, verifica e só então põe no sítio' {
    Mock Invoke-WebRequest { Escrever $OutFile 'certo' }
    ObterInstaladores @('Python')
    Ler $destino | Should -Be 'certo'
    Test-Path "$destino.part" | Should -BeFalse
    Registado | Should -Match 'Python: descarregado e verificado\.'
  }
  It 'sem internet para e apaga o meio ficheiro' {
    Mock Invoke-WebRequest { Escrever $OutFile 'meio'; throw 'sem rede' }
    { ObterInstaladores @('Python') } | Should -Throw 'Sair'
    Test-Path "$destino.part" | Should -BeFalse
    Registado | Should -Match "Não consegui descarregar o instalador de Python \(https://exemplo/py.exe\): sem rede"
  }
  It 'um ficheiro que não passa na verificação nunca é usado' {
    Mock Invoke-WebRequest { Escrever $OutFile 'errado' }
    { ObterInstaladores @('Python') } | Should -Throw 'Sair'
    Test-Path "$destino.part" | Should -BeFalse
    Test-Path $destino | Should -BeFalse
    Registado | Should -Match 'não passou na verificação'
  }
}

Describe 'Instalar os programas que faltam' {
  BeforeEach { Limpar; Mock ObterInstaladores {}; Mock Start-Process {} }
  It 'nada em falta: não pede administrador' {
    Mock ProgramasEmFalta { return , @() }
    InstalarProgramas
    Should -Invoke Start-Process -Times 0 -Exactly
    Registado | Should -Match 'Já está tudo instalado\.'
  }
  It 'obtém os instaladores e corre o instalar-programas.ps1 com UAC' {
    $vezes = @{ n = 0 }
    Mock ProgramasEmFalta { $vezes.n++; if ($vezes.n -eq 1) { return , @('Python') } return , @() }
    InstalarProgramas
    Should -Invoke ObterInstaladores -ParameterFilter { $nomes -contains 'Python' }
    Should -Invoke Start-Process -ParameterFilter { $Verb -eq 'RunAs' -and $Wait -and $ArgumentList -contains '-Pacote' -and
      ($ArgumentList -join ' ') -match 'instalar-programas\.ps1' }
    Registado | Should -Match 'Em falta: Python\.'
    Registado | Should -Match 'Programas instalados\.'
  }
  It 'UAC cancelado ou programa que continua em falta param' {
    Mock ProgramasEmFalta { return , @('Python') }
    Mock Start-Process { throw 'cancelado' }
    { InstalarProgramas } | Should -Throw 'Sair'
    Registado | Should -Match 'O pedido de administrador foi cancelado'
    Mock Start-Process {}
    { InstalarProgramas } | Should -Throw 'Sair'
    Registado | Should -Match 'Não ficou instalado: Python\.'
  }
}

Describe 'Fonte JetBrainsMono' {
  BeforeEach {
    Limpar
    $origem = Join-Path $Pacote '1-instaladores\fonte-JetBrainsMono-NF'
    Escrever (Join-Path $origem 'JetBrainsMonoNerdFont-Regular.ttf') 'a'
    Escrever (Join-Path $origem 'JetBrainsMonoNerdFont-Bold.ttf') 'b'
    Escrever (Join-Path $origem 'JetBrainsMonoNerdFont-Italic.ttf') 'c'
    Escrever (Join-Path $DirFontes 'JetBrainsMonoNerdFont-Regular.ttf') 'a'
    Escrever (Join-Path $DirFontes 'JetBrainsMonoNerdFont-Bold.ttf') 'antiga'
    Mock CarregarGdi {}
    Mock RegistarFonteNoWindows {}
    Mock AvisarMudancaDeFontes {}
    Mock New-ItemProperty {}
    Mock Copy-Item { [IO.File]::Copy(@($Path)[0], $Destination, $true) }  # no Pester 6 sem filtro que bata não há o real
    Mock Copy-Item { throw 'em uso' } -ParameterFilter { $Path -like '*Italic.ttf' }
  }
  It 'copia só as diferentes, regista cada uma e avisa as que estão em uso' {
    InstalarFontes
    Ler (Join-Path $DirFontes 'JetBrainsMonoNerdFont-Bold.ttf') | Should -Be 'b'
    Should -Invoke New-ItemProperty -Times 2 -Exactly
    Should -Invoke New-ItemProperty -ParameterFilter { $Name -eq 'JetBrainsMono NF Regular (TrueType)' -and $PropertyType -eq 'String' }
    Should -Invoke RegistarFonteNoWindows -Times 2 -Exactly
    Should -Invoke AvisarMudancaDeFontes -Times 1 -Exactly
    Registado | Should -Match 'JetBrainsMonoNerdFont-Italic\.ttf está em uso e não foi atualizada'
  }
}

Describe 'Escolhas do arranque' {
  BeforeEach {
    Limpar
    $ficheiroBat = Join-Path $TestDrive 'pacote\servidor.bat'
    Escrever $ficheiroBat "@echo off`r`nnpm run dev`r`n"
    Mock Get-Command {}
  }
  It 'PessoalAntigo: estrutura atual, antiga ou nenhuma' {
    PessoalAntigo $Glzr 'apps.txt' | Should -BeNullOrEmpty
    Escrever (Join-Path $Glzr 'zebar\guia-atalhos\apps.txt') 'x'
    PessoalAntigo $Glzr 'apps.txt' | Should -Be (Join-Path $Glzr 'zebar\guia-atalhos\apps.txt')
    Escrever (Join-Path $Glzr "$Pack\guia\apps.txt") 'x'
    PessoalAntigo $Glzr 'apps.txt' | Should -Be (Join-Path $Glzr "$Pack\guia\apps.txt")
  }
  It 'ValidarBat recusa o que não é um .bat existente' {
    ValidarBat (Join-Path $TestDrive 'nao.bat') '' '' | Should -BeNullOrEmpty
    Escrever (Join-Path $TestDrive 'pacote\x.txt') 'x'
    ValidarBat (Join-Path $TestDrive 'pacote\x.txt') '' '' | Should -BeNullOrEmpty
    Registado | Should -Match 'Não é um \.bat existente'
  }
  It 'ValidarBat: endereço inválido ignorado, nome do ficheiro, aviso do Node.js' {
    ValidarBat " `"$ficheiroBat`" " 'ftp://x' ' ' | Should -Be "bat = $ficheiroBat |  | servidor"
    Registado | Should -Match "Endereço inválido 'ftp://x'"
    Registado | Should -Match 'servidor usa Node.js, que não está instalado'
  }
  It 'ValidarBat: com endereço e nome, e com o Node.js instalado' {
    Mock Get-Command { 'npm' }
    ValidarBat $ficheiroBat ' http://localhost:3000 ' 'Site' | Should -Be "bat = $ficheiroBat | http://localhost:3000 | Site"
    Registado | Should -Not -Match 'Node.js'
    Registado | Should -Match 'em http://localhost:3000'
  }
  It 'reinstalação sem opções mantém o arranque.txt' {
    Escrever (Join-Path $Glzr "$Pack\guia\arranque.txt") 'animacao = cafe'
    $r = EscolherArranque
    $r.Manter | Should -BeTrue
    $r.Animacao | Should -BeNullOrEmpty
    @($r.Linhas).Count | Should -Be 0
  }
  It '-Bat: vários separados por ; e os que não existem ficam de fora' {
    Escrever (Join-Path $Glzr "$Pack\guia\arranque.txt") 'animacao = cafe'
    $Bat = @("$ficheiroBat|http://localhost:3000|S1;$TestDrive\nao.bat", '  ')
    $r = EscolherArranque
    $r.Manter | Should -BeFalse
    $r.Animacao | Should -Be 'cafe'
    $r.Linhas | Should -Be @("bat = $ficheiroBat | http://localhost:3000 | S1")
    Should -Invoke Read-Host -Times 0 -Exactly
  }
  It 'pergunta os .bat até um Enter vazio' {
    $respostas = [System.Collections.Generic.Queue[string]]::new([string[]]@($ficheiroBat, '', 'Meu', '   '))
    Mock Read-Host { $respostas.Dequeue() }
    $r = EscolherArranque
    $r.Linhas | Should -Be @("bat = $ficheiroBat |  | Meu")
  }
  It 'sem perguntas e sem .bat; com -Animacao não mantém o antigo' {
    Escrever (Join-Path $Glzr "$Pack\guia\arranque.txt") 'animacao = cafe'
    $SemPerguntas = $true
    $Animacao = 'cafe'
    $r = EscolherArranque
    $r.Manter | Should -BeFalse
    Registado | Should -Match 'Sem programas \.bat ao iniciar\.'
  }
}
