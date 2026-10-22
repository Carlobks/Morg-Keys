# Gera 2-configuracao (modelos) a partir da configuração ativa DESTE PC (~\.glzr).
# Corra depois de mudar a configuração aqui, para o pacote levar as mudanças.
# Só funciona com a estrutura do Morg Keys (um só pack, com guia\ e arranque\);
# se ~\.glzr tiver outra estrutura, para sem tocar em nada.
param([string]$Pkg = (Split-Path $PSScriptRoot -Parent))
$ErrorActionPreference = 'Stop'
$src = "$env:USERPROFILE\.glzr"
$dst = Join-Path $Pkg '2-configuracao'
$utf8 = New-Object Text.UTF8Encoding $false
$homeFwd = ($env:USERPROFILE -replace '\\', '/')          # ex.: C:/Users/nome
$homeRe  = [regex]::Escape($homeFwd) -replace '\\', '\\'   # o mesmo, em regex dentro de JSON

$p = 'zebar\omarchy-catppuccin'
$files = @(
  'glazewm\config.yaml',
  'zebar\settings.json',
  "$p\zpack.json", "$p\bar.html", "$p\styles.css", "$p\icons.css",
  "$p\bar_helper.py", "$p\claude_usage.py", "$p\uncloak.ps1", "$p\bat_tray.py",
  "$p\vendor\zebar-3.3.1.mjs",
  "$p\guia\guia.html", "$p\guia\sistema.html", "$p\guia\apps.txt",
  "$p\arranque\splash.html", "$p\arranque\cafe.bmp",
  "$p\painel\apps.html"
)
# Verifica tudo ANTES de apagar os modelos atuais.
$falta = @($files | Where-Object { -not (Test-Path (Join-Path $src $_)) } | ForEach-Object { Join-Path $src $_ })
if (-not (Test-Path "$env:USERPROFILE\.claude\statusline.py")) { $falta += "$env:USERPROFILE\.claude\statusline.py" }
if ($falta) { throw "Não encontrei (nada foi alterado): $($falta -join ', ')" }

if (Test-Path $dst) { Remove-Item -Recurse -Force $dst }
$textExt = '.yaml', '.json', '.html', '.css', '.py', '.ps1', '.txt', '.bat'
foreach ($rel in $files) {
  $from = Join-Path $src $rel; $to = Join-Path "$dst\glzr" $rel
  New-Item -ItemType Directory -Force (Split-Path $to) | Out-Null
  if ($textExt -notcontains [IO.Path]::GetExtension($rel)) { Copy-Item $from $to; continue }
  $t = [IO.File]::ReadAllText($from)
  if ($rel -like '*zpack.json') { $t = $t.Replace($homeRe, '{{HOME_RE}}') }
  $t = $t.Replace($homeFwd, '{{HOME}}')
  if ($rel -eq 'glazewm\config.yaml') {
    # O bloco das apps é gerado de novo no PC de destino a partir de apps.txt (só as apps que lá existem).
    $t = [regex]::Replace($t, '(?s)(  # >>> apps:[^\n]*\n).*?(  # <<< apps <<<)', '$1$2')
    if ($t -notmatch '# >>> apps:[^\n]*\n  # <<< apps <<<') { throw 'marcadores do bloco das apps não encontrados' }
  }
  if ($t -match [regex]::Escape($env:USERNAME)) { Write-Warning "$rel ainda contém '$env:USERNAME'" }
  [IO.File]::WriteAllText($to, $t, $utf8)
}
# O arranque.txt deste PC tem os .bat pessoais: o pacote leva o modelo (animação {{ANIMACAO}}, sem .bat).
Copy-Item (Join-Path $PSScriptRoot 'arranque-modelo.txt') "$dst\glzr\$p\guia\arranque.txt"
New-Item -ItemType Directory -Force "$dst\claude" | Out-Null
Copy-Item "$env:USERPROFILE\.claude\statusline.py" "$dst\claude\statusline.py"
"ok: $((Get-ChildItem -Recurse -File $dst).Count) ficheiros"
