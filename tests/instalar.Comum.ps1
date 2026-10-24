# Preparação comum dos testes do instalador (tests\instalar*.Tests.ps1), carregada no BeforeAll de cada um.
# Nunca instala nada:
#  - o instalador é carregado com ". instalar.ps1" (a última linha só chama Instalar quando é corrido);
#  - todas as pastas (perfil, pacote, fontes, registo, programas) apontam para o TestDrive;
#  - a cola com o Windows ($FuncoesExcluidas) e os cmdlets que mexem no sistema são trocados por
#    bombas: um teste que lá chegue sem o prever rebenta em vez de mexer no PC (como o sistema_falso.py).
# O scripts\testar.ps1 lê $FuncoesExcluidas daqui e exige 100 % de cobertura no resto do instalar.ps1.

# Funções de cola fora da cobertura: nome -> motivo (também em docs\validacao-manual.md).
$FuncoesExcluidas = @{
  'Sair'                   = 'exit 1: terminaria o próprio Pester; nos testes lança o erro "Sair"'
  'BuildDoWindows'         = '.NET [Environment]::OSVersion: o build do Windows real'
  'EAdministrador'         = '.NET WindowsPrincipal: se a sessão real é de administrador'
  'TipoDaUnidade'          = '.NET DriveInfo: o tipo do disco real (rede ou local)'
  'PythonServe'            = 'corre o py.exe real para ver a versão do Python'
  'AtivarTls12'            = '.NET ServicePointManager: muda o TLS do processo'
  'CarregarGdi'            = 'Add-Type com DllImport do gdi32 e do user32'
  'RegistarFonteNoWindows' = 'gdi32 AddFontResourceW: instala a fonte na sessão real'
  'AvisarMudancaDeFontes'  = 'user32 SendMessageTimeoutW(WM_FONTCHANGE) a todas as janelas'
  'GlazeSair'              = 'corre o glazewm.exe real (wm-exit)'
  'MatarArvore'            = 'taskkill real de um processo e dos filhos'
  'PastaDocumentos'        = '.NET GetFolderPath: a pasta Documentos real'
  'RemoverJuncao'          = 'cmd /c rmdir real da junction (A10)'
  'CorrerAppsApply'        = 'corre o py.exe real com o bar_helper.py apps-apply'
  'CorrerPython'           = 'corre o py.exe real (junta a statusLine ao settings.json do Claude Code)'
}
. (Join-Path $PSScriptRoot '..\scripts\instalar.ps1')
foreach ($nome in $FuncoesExcluidas.Keys) {
  if ($nome -ne 'Sair') { Mock $nome ([scriptblock]::Create("throw 'o teste tocou no Windows: $nome'")) }
}
Mock Sair { throw 'Sair' }
foreach ($cmdlet in 'Read-Host', 'Start-Process', 'Stop-Process', 'Set-ItemProperty', 'New-ItemProperty', 'Get-ItemProperty',
                    'Register-ScheduledTask', 'Start-ScheduledTask', 'Get-ScheduledTask', 'Invoke-WebRequest', 'Unblock-File',
                    'Get-CimInstance', 'Get-AuthenticodeSignature') {
  Mock $cmdlet ([scriptblock]::Create("throw 'o teste tocou no Windows: $cmdlet'"))
}
Mock Write-Host {}
Mock Start-Sleep {}
Mock Get-Process {}

$Casa = Join-Path $TestDrive 'casa'
$Glzr = Join-Path $Casa '.glzr'
$Registo = Join-Path $TestDrive 'instalacao.log'
$Pacote = Join-Path $TestDrive 'pacote'
$dirInst = Join-Path $Pacote '1-instaladores'
$DirFontes = Join-Path $TestDrive 'fontes'
$GlazeCli = Join-Path $TestDrive 'glazewm.exe'
$py = Join-Path $TestDrive 'py.exe'
$pyw = Join-Path $TestDrive 'pyw.exe'

function Escrever($caminho, $texto) {
  New-Item -ItemType Directory -Force (Split-Path $caminho) | Out-Null
  [IO.File]::WriteAllText($caminho, $texto, (New-Object Text.UTF8Encoding $false))
}
function Ler($caminho) { [IO.File]::ReadAllText($caminho) }
function Registado { if (Test-Path $Registo) { [IO.File]::ReadAllText($Registo) } else { '' } }
function Limpar {
  foreach ($p in $Casa, $Pacote, $DirFontes, $Registo, $GlazeCli, $py, (Join-Path $TestDrive 'docs')) {
    Remove-Item $p -Recurse -Force -ErrorAction SilentlyContinue
  }
}
