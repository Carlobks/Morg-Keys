# Versão que o instalador grava no instalacao.json (scripts\instalar-versao.ps1, ADR 0011): a do VERSION e,
# depois do +, o ramo e o commit (metadados do SemVer). Preparação em instalar-versao.Preparacao.ps1.

BeforeAll { . (Join-Path $PSScriptRoot 'instalar-versao.Preparacao.ps1') }

Describe 'VersaoDoPacote' {
  BeforeEach { Remove-Item $Pacote -Recurse -Force -ErrorAction SilentlyContinue }
  It 'junta a versão do VERSION, o ramo (sem a barra) e o commit' {
    EscreverVersao "0.1.0`n"
    Mock GitDoPacote { 'exp/a', 'c3b57e3' }
    VersaoDoPacote $Pacote | Should -Be '0.1.0+exp-a.c3b57e3'
    Should -Invoke GitDoPacote -ParameterFilter { $pasta -eq $Pacote }
  }
  It 'sem git (instalação a partir de um ZIP) fica só a versão' {
    EscreverVersao '2.3.4'
    Mock GitDoPacote { $null }
    VersaoDoPacote $Pacote | Should -Be '2.3.4'
  }
  It 'sem VERSION ou com um VERSION mal escrito diz desconhecida' {
    Mock GitDoPacote { $null }
    VersaoDoPacote $Pacote | Should -Be 'desconhecida'
    EscreverVersao 'v1.0'
    VersaoDoPacote $Pacote | Should -Be 'desconhecida'
    Mock GitDoPacote { 'main', '5f1ee68' }
    VersaoDoPacote $Pacote | Should -Be 'desconhecida+main.5f1ee68'
  }
}
