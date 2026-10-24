# Preparação comum dos testes do desinstalador (tests\desinstalar.Tests.ps1), como o instalar.Comum.ps1.
# Nunca desinstala nada: o ficheiro é carregado com ". desinstalar.ps1", as pastas apontam para o TestDrive
# e a cola com o Windows ($FuncoesExcluidas) e os cmdlets que mexem no sistema são bombas.
# O scripts\testar.ps1 lê $FuncoesExcluidas daqui e exige 100 % de cobertura no resto do desinstalar.ps1.

# Funções de cola fora da cobertura: nome -> motivo (também em docs\validacao-manual.md).
$FuncoesExcluidas = @{
  'GlazeSair'                = 'corre o glazewm.exe real (wm-exit)'
  'MostrarJanelasEscondidas' = 'corre o uncloak.ps1 real: mostra janelas escondidas da sessão'
  'PastaDocumentos'          = '.NET GetFolderPath: a pasta Documentos real'
  'RemoverJuncao'            = 'cmd /c rmdir real da junction (A10)'
  'CorrerPython'             = 'corre o py.exe real (tira a statusLine do settings.json do Claude Code)'
}
. (Join-Path $PSScriptRoot '..\scripts\desinstalar.ps1')
foreach ($nome in $FuncoesExcluidas.Keys) {
  Mock $nome ([scriptblock]::Create("throw 'o teste tocou no Windows: $nome'"))
}
foreach ($cmdlet in 'Unregister-ScheduledTask', 'Get-ScheduledTask', 'Stop-Process', 'Start-Process', 'Set-ItemProperty',
                    'Get-ItemProperty', 'Get-CimInstance') {
  Mock $cmdlet ([scriptblock]::Create("throw 'o teste tocou no Windows: $cmdlet'"))
}
Mock Write-Host {}
Mock Start-Sleep {}
Mock Get-Process {}

$Casa = Join-Path $TestDrive 'casa'
$Glzr = Join-Path $Casa '.glzr'
$PastasDoZebar = @((Join-Path $Casa 'AppData\Roaming\zebar'), (Join-Path $Casa 'AppData\Local\com.glzr.zebar'))
$GlazeCli = Join-Path $TestDrive 'glazewm.exe'

function Escrever($caminho, $texto) {
  New-Item -ItemType Directory -Force (Split-Path $caminho) | Out-Null
  [IO.File]::WriteAllText($caminho, $texto, (New-Object Text.UTF8Encoding $false))
}
function Limpar {
  foreach ($p in $Casa, $GlazeCli, (Join-Path $TestDrive 'docs')) { Remove-Item $p -Recurse -Force -ErrorAction SilentlyContinue }
  New-Item -ItemType Directory -Force $Casa | Out-Null
}
