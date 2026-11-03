<#
  Instalador do Morg Keys (Windows ao estilo Omarchy).
  Corre como o UTILIZADOR que vai usar o PC (duplo clique em INSTALAR.cmd).
  Só pede administrador (UAC) para instalar os programas que faltem.
  Os instaladores dos programas não vêm no repositório: se faltarem em
  1-instaladores\, são descarregados dos sites oficiais e verificados
  (SHA-256 fixo para GlazeWM e Python; assinatura da Microsoft para o Visual C++).

  Faz só uma pergunta (com Enter = nenhum), que fica gravada em
  Documentos\Guia de Atalhos\arranque.txt e se muda lá a qualquer altura:
    - programas .bat a correr escondidos ao iniciar (ex.: um servidor local).
  Numa reinstalação mantém o arranque.txt que já existia e não pergunta.

  Opções (todas opcionais):
    -Animacao cafe                           animação do ecrã de arranque (uma das que têm .bmp em
                                             2-configuracao\glzr\zebar\omarchy-catppuccin\arranque\)
    -Bat "C:\x\iniciar.bat|http://localhost:3000|Nome"   .bat ao iniciar (vários: separe por ;);
                                             endereço e nome são opcionais
    -SemPerguntas                            não pergunta nada (sem .bat, salvo -Bat)
    -ManterIcones                            não esconde os ícones do ambiente de trabalho
    -ManterBarraWindows                      não põe a barra de tarefas a esconder-se sozinha
    -NaoIniciar                              instala mas não arranca já (arranca no próximo início de sessão)
#>
param(
  [string]$Animacao,
  [string[]]$Bat,
  [switch]$SemPerguntas,
  [switch]$ManterIcones,
  [switch]$ManterBarraWindows,
  [switch]$NaoIniciar
)
$ErrorActionPreference = 'Stop'
$Pacote = Split-Path $PSScriptRoot -Parent
$Casa = $env:USERPROFILE
$Glzr = Join-Path $Casa '.glzr'
$Registo = Join-Path $env:TEMP 'morg-keys-instalacao.log'
$Pack = 'zebar\omarchy-catppuccin'   # o único pack do Zebar (barra, guia\, arranque\)
$utf8 = New-Object Text.UTF8Encoding $false
Set-Content -Path $Registo -Value "Instalação $(Get-Date -Format s) por $env:USERDOMAIN\$env:USERNAME" -Encoding UTF8

function Passo($m) { Write-Host ""; Write-Host "==> $m" -ForegroundColor Cyan; Add-Content $Registo "==> $m" -Encoding UTF8 }
function Info($m)  { Write-Host "    $m"; Add-Content $Registo "    $m" -Encoding UTF8 }
function Aviso($m) { Write-Host "    ! $m" -ForegroundColor Yellow; Add-Content $Registo "    ! $m" -Encoding UTF8 }
function Parar($m) { Write-Host ""; Write-Host "ERRO: $m" -ForegroundColor Red; Add-Content $Registo "ERRO: $m" -Encoding UTF8; exit 1 }

# ---------------------------------------------------------------------------
Passo 'Verificações'
$build = [Environment]::OSVersion.Version.Build
if ($build -lt 22000) { Parar "É preciso Windows 11 (este é o build $build)." }
if ($Casa -match '\s') {
  Parar "A pasta do utilizador ($Casa) tem espaços. O GlazeWM corta os comandos nos espaços e os atalhos do terminal falhariam."
}
if ($Pacote.StartsWith('\\') -or ([IO.DriveInfo]([IO.Path]::GetPathRoot($Pacote))).DriveType -eq 'Network') {
  Parar "O pacote está numa pasta de rede. Copie a pasta inteira para este PC (ex.: Transferências) e corra de lá."
}
$admin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
  [Security.Principal.WindowsBuiltInRole]::Administrator)
if ($admin) {
  Aviso "Está a correr como administrador. Tudo será instalado para a conta $env:USERNAME."
  Aviso 'Se esta não é a conta de quem vai usar o PC, feche e corra o INSTALAR.cmd com duplo clique, sem "Executar como administrador".'
  if ((Read-Host '    Continuar? (S/N)') -notmatch '^[sS]') { exit 1 }
}
Info "Windows build $build, utilizador $env:USERNAME, pasta $Casa"
# Ficheiros vindos de outro PC/da internet trazem a marca "Mark of the Web": tira-a.
Get-ChildItem -Recurse -File $Pacote | Unblock-File

# ---------------------------------------------------------------------------
Passo 'Programas (GlazeWM + Zebar, Python, Visual C++)'
$py  = Join-Path $env:windir 'py.exe'
$pyw = Join-Path $env:windir 'pyw.exe'
function ProgramasEmFalta {
  $falta = @()
  $vc = Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64' -ErrorAction SilentlyContinue
  if (-not ($vc -and $vc.Installed -eq 1)) { $falta += 'Visual C++' }
  if (-not (Test-Path "$env:ProgramFiles\glzr.io\GlazeWM\glazewm.exe") -or -not (Test-Path "$env:ProgramFiles\glzr.io\Zebar\zebar.exe")) { $falta += 'GlazeWM/Zebar' }
  $ok = $false
  if (Test-Path $py) {
    try { & $py -3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" 2>$null; $ok = ($LASTEXITCODE -eq 0) } catch { $ok = $false }
  }
  if (-not $ok) { $falta += 'Python' }
  return ,$falta
}
# Instaladores: usa os de 1-instaladores\ se lá estiverem e forem os certos; senão descarrega
# dos sites oficiais. Nunca corre um ficheiro que não passe na verificação.
$dirInst = Join-Path $Pacote '1-instaladores'
$Instaladores = @{
  'GlazeWM/Zebar' = @{ Ficheiro = 'GlazeWM-3.10.1-com-Zebar.exe'
    Url = 'https://github.com/glzr-io/glazewm/releases/download/v3.10.1/glazewm-v3.10.1.exe'
    Sha256 = '469F8675F5AD1353BDA9CEDE7CBB0E320E1B9A1D5657DA709B60A51D86E95020' }
  'Python' = @{ Ficheiro = 'Python-3.11.9-amd64.exe'
    Url = 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe'
    Sha256 = '5EE42C4EEE1E6B4464BB23722F90B45303F79442DF63083F05322F1785F5FDDE' }
  # A Microsoft atualiza este ficheiro no mesmo endereço: verifica-se a assinatura, não o hash.
  'Visual C++' = @{ Ficheiro = 'VisualC++-Redistribuivel-x64.exe'
    Url = 'https://aka.ms/vs/17/release/vc_redist.x64.exe'
    Assinante = 'O=Microsoft Corporation' }
}
function InstaladorValido($caminho, $i) {
  if (-not (Test-Path $caminho)) { return $false }
  if ($i.Sha256) { return (Get-FileHash $caminho -Algorithm SHA256).Hash -eq $i.Sha256 }
  $s = Get-AuthenticodeSignature $caminho
  # Campo O= exato (não basta aparecer em qualquer parte do nome do certificado).
  return $s.Status -eq 'Valid' -and $s.SignerCertificate.Subject -match "(^|, )$([regex]::Escape($i.Assinante))(,|$)"
}
function ObterInstaladores($nomes) {
  New-Item -ItemType Directory -Force $dirInst | Out-Null
  [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
  foreach ($n in $nomes) {
    $i = $Instaladores[$n]; $dest = Join-Path $dirInst $i.Ficheiro
    if (InstaladorValido $dest $i) { Info "$n`: instalador já presente."; continue }
    Info "$n`: a descarregar de $($i.Url) ..."
    $tmp = "$dest.part"
    $pp = $ProgressPreference; $ProgressPreference = 'SilentlyContinue'   # sem isto o download é muito lento
    try { Invoke-WebRequest -Uri $i.Url -OutFile $tmp -UseBasicParsing }
    catch { Remove-Item $tmp -Force -ErrorAction SilentlyContinue; Parar "Não consegui descarregar o instalador de $n ($($i.Url)): $_. Sem internet? Ponha o ficheiro '$($i.Ficheiro)' em $dirInst e volte a correr." }
    finally { $ProgressPreference = $pp }
    if (-not (InstaladorValido $tmp $i)) {
      Remove-Item $tmp -Force
      Parar "O instalador descarregado de $n não passou na verificação (hash ou assinatura). Não foi usado."
    }
    Move-Item $tmp $dest -Force
    Info "$n`: descarregado e verificado."
  }
}

$falta = ProgramasEmFalta
if ($falta.Count -eq 0) { Info 'Já está tudo instalado.' }
else {
  Info "Em falta: $($falta -join ', ')."
  ObterInstaladores $falta
  Info 'Vai aparecer o pedido de administrador (UAC).'
  $script = Join-Path $PSScriptRoot 'instalar-programas.ps1'
  try {
    Start-Process powershell.exe -Verb RunAs -Wait -ArgumentList @(
      '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', "`"$script`"", '-Pacote', "`"$Pacote`"", '-Registo', "`"$Registo`"")
  } catch { Parar 'O pedido de administrador foi cancelado. Sem ele não é possível instalar os programas.' }
  $falta = ProgramasEmFalta
  if ($falta.Count -gt 0) { Parar "Não ficou instalado: $($falta -join ', '). Veja o registo: $Registo" }
  Info 'Programas instalados.'
}
$GlazeCli = "$env:ProgramFiles\glzr.io\GlazeWM\cli\glazewm.exe"

# ---------------------------------------------------------------------------
Passo 'Fonte JetBrainsMono Nerd Font (só para este utilizador)'
$dirFontes = Join-Path $env:LOCALAPPDATA 'Microsoft\Windows\Fonts'
New-Item -ItemType Directory -Force $dirFontes | Out-Null
Add-Type -Namespace MorgInst -Name Gdi -MemberDefinition @'
[DllImport("gdi32.dll", CharSet = CharSet.Unicode)] public static extern int AddFontResourceW(string f);
[DllImport("user32.dll")] public static extern IntPtr SendMessageTimeoutW(IntPtr h, uint m, IntPtr w, IntPtr l, uint f, uint t, out IntPtr r);
'@
foreach ($ttf in Get-ChildItem (Join-Path $Pacote '1-instaladores\fonte-JetBrainsMono-NF') -Filter *.ttf) {
  $dest = Join-Path $dirFontes $ttf.Name
  # Reinstalação: a fonte já instalada está aberta pelo Windows e não se deixa
  # substituir. Se for igual, não há nada a copiar; se for diferente, avisa e segue.
  if (-not ((Test-Path $dest) -and (Get-FileHash $dest).Hash -eq (Get-FileHash $ttf.FullName).Hash)) {
    try { Copy-Item $ttf.FullName $dest -Force -ErrorAction Stop }
    catch { Aviso "$($ttf.Name) está em uso e não foi atualizada (fica a versão já instalada)."; continue }
  }
  $estilo = $ttf.BaseName -replace '^JetBrainsMonoNerdFont-', ''
  New-ItemProperty 'HKCU:\Software\Microsoft\Windows NT\CurrentVersion\Fonts' -Name "JetBrainsMono NF $estilo (TrueType)" `
    -Value $dest -PropertyType String -Force | Out-Null
  [void][MorgInst.Gdi]::AddFontResourceW($dest)
  Info $ttf.Name
}
$r = [IntPtr]::Zero
[void][MorgInst.Gdi]::SendMessageTimeoutW([IntPtr]0xffff, 0x001D, [IntPtr]::Zero, [IntPtr]::Zero, 2, 1000, [ref]$r)  # WM_FONTCHANGE

# ---------------------------------------------------------------------------
Passo 'Ecrã de arranque e programas ao iniciar'
# Tudo isto fica em arranque.txt (Documentos\Guia de Atalhos), que o "boot" lê em cada arranque.
# Ficheiros pessoais numa instalação anterior: na estrutura atual (um só pack) ou na
# antiga (versões com o guia num pack separado, guia-atalhos). Devolve o 1.º que existir.
function PessoalAntigo($base, $nome) {
  foreach ($rel in "$Pack\guia\$nome", "zebar\guia-atalhos\$nome") {
    $c = Join-Path $base $rel; if (Test-Path $c) { return $c }
  }
  return $null
}
# Animações do pacote = os BMP da cortina em arranque\ (cada animação tem o seu: receita 5b).
$Animacoes = @(Get-ChildItem (Join-Path $Pacote "2-configuracao\glzr\$Pack\arranque") -Filter *.bmp | ForEach-Object BaseName)
if ($Animacao -and $Animacoes -notcontains $Animacao) { Parar "Animação '$Animacao' não existe no pacote (há: $($Animacoes -join ', '))." }
$arranqueAntigo = PessoalAntigo $Glzr 'arranque.txt'
$manterArranque = $arranqueAntigo -and -not $Animacao -and -not $Bat
$linhasBat = @()
if ($manterArranque) {
  Info 'Reinstalação: mantém o arranque.txt atual (animação e programas). Mude-o lá se quiser.'
} else {
  if (-not $Animacao) { $Animacao = 'cafe' }
  Info "Animação: $Animacao"

  function ValidarBat($caminho, $endereco, $nome) {
    $caminho = $caminho.Trim().Trim('"')
    if (-not (Test-Path $caminho -PathType Leaf) -or [IO.Path]::GetExtension($caminho) -notin '.bat', '.cmd') {
      Aviso "Não é um .bat existente: $caminho — ignorado."; return $null
    }
    $caminho = (Resolve-Path $caminho).Path
    $endereco = "$endereco".Trim()
    if ($endereco -and $endereco -notmatch '^https?://') { Aviso "Endereço inválido '$endereco' — ignorado."; $endereco = '' }
    $nome = "$nome".Trim(); if (-not $nome) { $nome = [IO.Path]::GetFileNameWithoutExtension($caminho) }
    if ((Get-Content $caminho -Raw) -match '\b(npm|npx|node)\b' -and -not (Get-Command npm -ErrorAction SilentlyContinue)) {
      Aviso "$nome usa Node.js, que não está instalado: o ícone aparece, mas o programa só arranca depois de instalar o Node.js."
    }
    Info ".bat ao iniciar: $nome ($caminho)$(if ($endereco) { " em $endereco" })"
    return "bat = $caminho | $endereco | $nome"
  }
  foreach ($b in (($Bat -join ';').Split(';') | Where-Object { $_.Trim() })) {
    $p = "$b".Split('|') + @('', '')
    $l = ValidarBat $p[0] $p[1] $p[2]; if ($l) { $linhasBat += $l }
  }
  if (-not $Bat -and -not $SemPerguntas) {
    Info 'Programas .bat a correr escondidos ao iniciar o PC (ex.: um servidor local). Ficam com um ícone junto ao relógio.'
    while ($true) {
      $c = Read-Host '    Caminho do .bat (Enter = nenhum / terminar)'
      if (-not $c.Trim()) { break }
      $e = Read-Host '    Endereço que ele serve, ex. http://localhost:3000 (Enter = nenhum)'
      $n = Read-Host '    Nome a mostrar (Enter = nome do ficheiro)'
      $l = ValidarBat $c $e $n; if ($l) { $linhasBat += $l }
    }
  }
  if (-not $linhasBat) { Info 'Sem programas .bat ao iniciar.' }
}

# ---------------------------------------------------------------------------
Passo 'Configuração (~\.glzr)'
if (Test-Path $GlazeCli) {
  # Reinstalação: fecha o que estiver a correr antes de trocar os ficheiros.
  if (Get-Process glazewm -ErrorAction SilentlyContinue) { try { & $GlazeCli command wm-exit 2>$null | Out-Null } catch {}; Start-Sleep 2 }
  Get-Process zebar -ErrorAction SilentlyContinue | Stop-Process -Force
}
# Ajudantes ainda a correr (café, ícones dos .bat com os seus programas): fecham-se com os
# filhos, senão a tarefa lança outra cópia de cada .bat e a pasta pode não se deixar renomear.
Get-CimInstance Win32_Process -Filter "Name='pythonw.exe' OR Name='python.exe'" |
  Where-Object { $_.CommandLine -match '\.glzr' } |
  ForEach-Object { taskkill /PID $_.ProcessId /T /F 2>$null | Out-Null }
$copia = $null
if (Test-Path $Glzr) {
  $copia = "$Glzr.copia-$(Get-Date -Format yyyyMMdd-HHmmss)"
  # Um programa ainda a usar ~\.glzr (ex.: um .bat de arranque.txt cujo ícone já fechou, como um
  # servidor local) impede guardá-la. Não se fecha nada sozinho: avisa e espera que o utilizador o feche.
  while ($true) {
    try { Rename-Item $Glzr $copia -ErrorAction Stop; break } catch {}
    Start-Sleep 2  # os ajudantes fechados acima podem demorar a largar os ficheiros
    try { Rename-Item $Glzr $copia -ErrorAction Stop; break } catch {}
    Aviso "Não consigo guardar $Glzr : um programa ainda a está a usar."
    Get-CimInstance Win32_Process -Filter "Name='cmd.exe'" | Where-Object { $_.CommandLine -match '\.glzr' } |
      ForEach-Object { Aviso "Programa de arranque.txt ainda aberto: $($_.CommandLine -replace '^.*?\s/c\s+', '') (PID $($_.ProcessId))" }
    Info 'Feche-o: Gestor de Tarefas > Detalhes > botão direito em cmd.exe > Terminar árvore de processos.'
    Info 'Também conta uma janela do Explorador ou um terminal aberto dentro dessa pasta. Ou termine a sessão e volte a entrar.'
    if ($SemPerguntas) { Parar 'Feche-o e corra o INSTALAR.cmd outra vez. Nada foi alterado na configuração.' }
    if ((Read-Host '    Enter = tentar outra vez · S = sair') -match '^[sS]') { Parar 'Instalação cancelada. Nada foi alterado na configuração.' }
  }
  Info "A configuração anterior ficou guardada em $copia"
}
$homeFwd = $Casa -replace '\\', '/'
$homeRe  = [regex]::Escape($homeFwd) -replace '\\', '\\'      # dentro de JSON: cada \ vira \\
$modelos = Join-Path $Pacote '2-configuracao\glzr'
foreach ($f in Get-ChildItem -Recurse -File $modelos) {
  $rel = $f.FullName.Substring($modelos.Length + 1)
  $dest = Join-Path $Glzr $rel
  New-Item -ItemType Directory -Force (Split-Path $dest) | Out-Null
  if ($f.Extension -notin '.yaml', '.json', '.html', '.css', '.py', '.ps1', '.txt') { Copy-Item $f.FullName $dest; continue }
  $t = [IO.File]::ReadAllText($f.FullName, $utf8).Replace('{{HOME_RE}}', $homeRe).Replace('{{HOME}}', $homeFwd)
  if ($rel -eq "$Pack\guia\arranque.txt") {
    $t = $t.Replace('{{ANIMACAO}}', $(if ($Animacao) { $Animacao } else { 'cafe' }))
    if ($linhasBat) { $t = $t.TrimEnd() + "`n" + ($linhasBat -join "`n") + "`n" }
  }
  [IO.File]::WriteAllText($dest, $t, $utf8)
}
# Reinstalação: mantém as personalizações de quem já usava (apps, arranque e disposição das janelas).
if ($copia) {
  if (Test-Path (Join-Path $copia 'arranque')) {  # registos e .bat que o utilizador lá tenha posto
    Copy-Item (Join-Path $copia 'arranque') (Join-Path $Glzr 'arranque') -Recurse -Force
  }
  if (Test-Path (Join-Path $copia 'layout.json')) { Copy-Item (Join-Path $copia 'layout.json') (Join-Path $Glzr 'layout.json') -Force; Info 'mantido layout.json' }
  $nomes = @('apps.txt'); if ($manterArranque) { $nomes += 'arranque.txt' }
  foreach ($nome in $nomes) {
    $de = PessoalAntigo $copia $nome
    if ($de) { Copy-Item $de (Join-Path $Glzr "$Pack\guia\$nome") -Force; Info "mantido $nome" }
  }
  # Um arranque.txt antigo pode ter uma animação que já não existe (ex.: de outra versão): passa a cafe.
  $arr = Join-Path $Glzr "$Pack\guia\arranque.txt"
  if (Test-Path $arr) {
    $t = [IO.File]::ReadAllText($arr, $utf8)
    $conhecidas = ($Animacoes | ForEach-Object { [regex]::Escape($_) }) -join '|'
    $novo = [regex]::Replace($t, '(?m)^(\s*anima(c|ç)(a|ã)o\s*=\s*)(?!\s*(' + $conhecidas + ')\s*$).*$', '${1}cafe')
    if ($novo -ne $t) { [IO.File]::WriteAllText($arr, $novo, $utf8); Info 'arranque.txt: animação antiga trocada por cafe.' }
  }
}
# Só os ficheiros vindos dos modelos (os .log copiados podem ter "{{" legítimos).
$falhas = Get-ChildItem -Recurse -File $Glzr -Include *.yaml, *.json, *.html, *.css, *.py, *.ps1, *.txt |
  Where-Object { $_.FullName -notlike "$Glzr\arranque\*" } | Select-String -SimpleMatch '{{' -List
if ($falhas) { Parar "Ficaram marcadores por substituir: $($falhas.Path -join ', ')" }
Info "Configuração copiada para $Glzr"

# Atalho em Documentos para o guia (onde se editam as apps).
$docs = [Environment]::GetFolderPath('MyDocuments')
$juncao = Join-Path $docs 'Guia de Atalhos'
# Get-Item (e não Test-Path): também apanha uma junction antiga cujo destino já não existe.
$j = Get-Item $juncao -Force -ErrorAction SilentlyContinue
if ($j) {
  if ($j.Attributes -band [IO.FileAttributes]::ReparsePoint) { cmd /c rmdir "$juncao" | Out-Null }
  else { Aviso "Já existe uma pasta normal '$juncao': não a substituí." }
}
if (-not (Get-Item $juncao -Force -ErrorAction SilentlyContinue)) {
  New-Item -ItemType Junction -Path $juncao -Target (Join-Path $Glzr "$Pack\guia") | Out-Null
  Info "Documentos\Guia de Atalhos -> $Glzr\$Pack\guia"
}

# ---------------------------------------------------------------------------
Passo 'Atalhos das apps (a partir de apps.txt)'
$helper = Join-Path $Glzr "$Pack\bar_helper.py"
try { & $py -I $helper apps-apply --skip-missing 2>&1 | ForEach-Object { Add-Content $Registo "    $_" -Encoding UTF8 } } catch { Aviso "apps-apply: $_" }
$naoHa = Select-String -Path (Join-Path $Glzr "$Pack\guia\apps.txt") -SimpleMatch '(não encontrada neste PC)'
if ($naoHa) { $naoHa | ForEach-Object { Aviso "sem a app: $($_.Line -replace '^# \(não encontrada neste PC\) ', '')" }; Info 'Instale-as e tire o # em apps.txt (Alt+Esc, C; depois Alt+Shift+R).' }
else { Info 'Todas as apps de apps.txt foram encontradas.' }

# ---------------------------------------------------------------------------
Passo 'Claude Code: uso do plano na barra (opcional)'
$claudeDir = Join-Path $Casa '.claude'
$statusAplicado = $false
if ((Test-Path $claudeDir) -or (Test-Path (Join-Path $Casa '.local\bin\claude.exe'))) {
  New-Item -ItemType Directory -Force $claudeDir | Out-Null
  $sl = Join-Path $claudeDir 'statusline.py'
  if ((Test-Path $sl) -and ((Get-FileHash $sl).Hash -ne (Get-FileHash (Join-Path $Pacote '2-configuracao\claude\statusline.py')).Hash)) {
    Copy-Item $sl "$sl.bak" -Force; Info 'statusline.py anterior guardado como statusline.py.bak'
  }
  Copy-Item (Join-Path $Pacote '2-configuracao\claude\statusline.py') $sl -Force
  $merge = Join-Path $env:TEMP 'morg-keys-statusline-merge.py'
  [IO.File]::WriteAllText($merge, @'
import json, pathlib, sys
p, cmd = pathlib.Path(sys.argv[1]), sys.argv[2]
d = json.loads(p.read_text(encoding="utf-8-sig")) if p.exists() else {}
cur = d.get("statusLine") or {}
if cur and "statusline.py" not in cur.get("command", ""):
    print("mantido"); sys.exit(0)
d["statusLine"] = {"type": "command", "command": cmd}
p.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("ok")
'@, $utf8)
  try { $res = (& $py -I $merge (Join-Path $claudeDir 'settings.json') "C:/Windows/py.exe -I `"$homeFwd/.claude/statusline.py`"" 2>&1 | Out-String).Trim() } catch { $res = "$_" }
  Remove-Item $merge
  if ($res -eq 'ok') { $statusAplicado = $true; Info 'statusLine do Claude Code configurada (a barra mostra o uso depois da 1.ª resposta do Claude).' }
  elseif ($res -eq 'mantido') { Aviso 'O Claude Code já tem outra statusLine: não mexi. Veja o tutorial para a juntar.' }
  else { Aviso "Não consegui alterar ~\.claude\settings.json ($res)." }
} else { Info 'Claude Code não instalado: a barra mostra o uso quando o instalar e voltar a correr o instalador.' }

# ---------------------------------------------------------------------------
Passo 'Ambiente de trabalho do Windows'
$adv = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced'
$estado = [ordered]@{ instalado_em = (Get-Date -Format s); copia_anterior = $copia; statusline = $statusAplicado }
$estado.hideicons_antes = (Get-ItemProperty $adv -Name HideIcons -ErrorAction SilentlyContinue).HideIcons
$reiniciarExplorer = $false
if (-not $ManterIcones) { Set-ItemProperty $adv -Name HideIcons -Value 1 -Type DWord; $reiniciarExplorer = $true; Info 'Ícones do ambiente de trabalho escondidos.' }
$sr = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\StuckRects3'
$bin = (Get-ItemProperty $sr -Name Settings -ErrorAction SilentlyContinue).Settings
if ($bin) {
  $estado.barra_antes = [int]$bin[8]
  if (-not $ManterBarraWindows) { $bin[8] = 3; Set-ItemProperty $sr -Name Settings -Value $bin; $reiniciarExplorer = $true; Info 'Barra de tarefas do Windows a esconder-se sozinha.' }
}
[IO.File]::WriteAllText((Join-Path $Glzr 'instalacao.json'), ($estado | ConvertTo-Json), $utf8)
if ($reiniciarExplorer) { Stop-Process -Name explorer -Force; Start-Sleep 3; if (-not (Get-Process explorer -ErrorAction SilentlyContinue)) { Start-Process explorer.exe } }

# ---------------------------------------------------------------------------
Passo 'Arranque automático (tarefa agendada)'
$quem = "$env:USERDOMAIN\$env:USERNAME"
$acao = New-ScheduledTaskAction -Execute $pyw -Argument "-I `"$helper`" boot"
$gat  = New-ScheduledTaskTrigger -AtLogOn -User $quem
$pri  = New-ScheduledTaskPrincipal -UserId $quem -LogonType Interactive -RunLevel Limited
$def  = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable `
          -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances IgnoreNew -Priority 4
try {
  Register-ScheduledTask -TaskName 'GlazeWM (arranque)' -Action $acao -Trigger $gat -Principal $pri -Settings $def -Force `
    -Description 'Arranque do PC: ecrã de arranque + barra (Zebar) + GlazeWM + apps + programas .bat de arranque.txt. Orquestrado por bar_helper.py boot.' `
    -ErrorAction Stop | Out-Null
  Info "Tarefa 'GlazeWM (arranque)' registada para $quem."
} catch {
  $erro = $_
  # Uma tarefa antiga criada com privilégios de administrador não se deixa substituir
  # sem eles. Se já faz o mesmo (mesmo programa e argumentos) e com as opções de que a
  # rapidez do arranque depende (prioridade 4, sem atraso no gatilho), serve tal como está.
  # Com a prioridade por omissão das tarefas (7) ou um atraso, o fundo fica segundos à vista
  # antes da cortina (docs/pendentes.md, "Fundo à vista no arranque").
  $velha = Get-ScheduledTask -TaskName 'GlazeWM (arranque)' -ErrorAction SilentlyContinue
  $mesmaAcao = $velha -and $velha.Actions[0].Execute -ieq $pyw -and $velha.Actions[0].Arguments -eq "-I `"$helper`" boot"
  $atraso = @($velha.Triggers | Where-Object { $_.Delay } | ForEach-Object { $_.Delay }) -join ', '
  $apagar = "Abra o PowerShell como administrador, corra  schtasks /Delete /TN `"GlazeWM (arranque)`" /F  e volte a correr o INSTALAR.cmd."
  if ($mesmaAcao -and $velha.Settings.Priority -eq 4 -and -not $atraso) {
    Aviso 'A tarefa de arranque já existia (criada como administrador) e faz o mesmo: fica a que estava.'
  } elseif ($mesmaAcao) {
    Parar "A tarefa de arranque antiga (criada como administrador) tem prioridade $($velha.Settings.Priority)$(if ($atraso) { " e atraso $atraso" }) em vez de 4 sem atraso: o arranque ficaria lento. $apagar"
  } else {
    Parar "Não consegui criar a tarefa de arranque ($($erro.Exception.Message)). $apagar"
  }
}

Copy-Item $Registo (Join-Path $Glzr 'instalacao.log') -Force
if ($NaoIniciar) { Passo 'Concluído. Termine a sessão e volte a entrar para arrancar.' }
else {
  Passo 'Concluído. A arrancar agora (ecrã de arranque, depois a barra no topo).'
  Start-ScheduledTask -TaskName 'GlazeWM (arranque)'
}
Info 'Primeiros passos: Alt+K mostra todos os atalhos; Alt+Esc abre o painel do sistema.'
Info "Registo desta instalação: $Glzr\instalacao.log"
