# Preparação dos testes da versão do instalador (tests\instalar-versao.Tests.ps1). Nunca corre o git real.
# O scripts\testar.ps1 lê $FuncoesExcluidas daqui e exige 100 % de cobertura no resto do instalar-versao.ps1.

# Funções de cola fora da cobertura: nome -> motivo (também em docs\validacao-manual.md).
$FuncoesExcluidas = @{
  'GitDoPacote' = 'corre o git real (o ramo e o commit da pasta de onde se instala)'
}
. (Join-Path $PSScriptRoot '..\scripts\instalar-versao.ps1')
foreach ($funcao in $FuncoesExcluidas.Keys) { Mock $funcao ([scriptblock]::Create("throw 'o teste tocou no git real: $funcao'")) }

$Pacote = Join-Path $TestDrive 'pacote'
function EscreverVersao($texto) {
  New-Item -ItemType Directory -Force $Pacote | Out-Null
  [IO.File]::WriteAllText((Join-Path $Pacote 'VERSION'), $texto, (New-Object Text.UTF8Encoding $false))
}
