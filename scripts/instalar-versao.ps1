<#
  Versão do Morg Keys que o instalador grava no ~\.glzr\instalacao.json, lida pelo relatório de erros (ADR 0011).
  SemVer: a versão do VERSION e, depois do +, o ramo e o commit de onde se instalou (ex.: 0.1.0+exp-a.c3b57e3).
  Carregado pelo instalar.ps1 com ". instalar-versao.ps1" (só define funções); testes em tests\instalar-versao.Tests.ps1.
#>

# Cola com o git real (fora da cobertura, em tests\instalar-versao.Preparacao.ps1): o ramo e o commit, ou $null sem
# git ou fora de um clone (instalação a partir de um ZIP).
function GitDoPacote($pasta) {
  if (-not (Get-Command git -ErrorAction SilentlyContinue)) { return $null }
  $ramo = & git -C $pasta rev-parse --abbrev-ref HEAD 2>$null
  $commit = & git -C $pasta rev-parse --short HEAD 2>$null
  if ($LASTEXITCODE -ne 0 -or -not $commit) { return $null }
  return @($ramo, $commit)
}

function VersaoDoPacote($pasta) {
  $ficheiro = Join-Path $pasta 'VERSION'
  $versao = if (Test-Path $ficheiro) { (Get-Content $ficheiro -Raw -Encoding UTF8).Trim() } else { '' }
  if ($versao -notmatch '^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$') { $versao = 'desconhecida' }
  $git = GitDoPacote $pasta
  if (-not $git) { return $versao }
  # Nos metadados do SemVer só entram [0-9A-Za-z-]: o "/" do ramo (exp/a) passa a "-".
  return "$versao+$($git[0] -replace '[^0-9A-Za-z-]', '-').$($git[1])"
}
