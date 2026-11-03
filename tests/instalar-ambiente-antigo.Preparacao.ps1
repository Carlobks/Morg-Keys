# Preparação do fecho do ambiente antigo (scripts\instalar-ambiente-antigo.ps1), carregada pelo
# tests\instalar.Preparacao.ps1 depois do instalador: troca esta cola por bombas. Os testes estão em
# tests\instalar-configuracao.Tests.ps1. O scripts\testar.ps1 lê $FuncoesExcluidas daqui e exige 100 % de
# cobertura no resto do ficheiro.

# Funções de cola fora da cobertura: nome -> motivo (também em docs\validacao-manual.md).
$FuncoesExcluidas = @{
  'GlazeSair'   = 'corre o glazewm.exe real (wm-exit)'
  'MatarArvore' = 'taskkill real de um processo e dos filhos'
}
foreach ($funcao in $FuncoesExcluidas.Keys) { Mock $funcao ([scriptblock]::Create("throw 'o teste tocou no Windows: $funcao'")) }
