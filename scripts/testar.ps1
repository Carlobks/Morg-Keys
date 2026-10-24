# Comando único de testes do Morg Keys (só lê o repositório; não arranca o GlazeWM nem o Zebar — A2).
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts\testar.ps1
# Sai com 0 se todos os testes passarem e 1 se algum falhar.
# O lint também bloqueia (fase 2d da experiência 0001): ruff (regras em ruff.toml), Biome com os avisos
# a contar como erros (regras em biome.jsonc) e PSScriptAnalyzer só nos erros (os avisos informam:
# o Write-Host do instalador é de propósito).

# Continue: no PowerShell 5.1 o stderr dos programas nativos vira erro e pararia o script; conta o $LASTEXITCODE.
$ErrorActionPreference = 'Continue'
$Raiz = Split-Path -Parent $PSScriptRoot
$Pack = Join-Path $Raiz '2-configuracao\glzr\zebar\omarchy-catppuccin'
$Py = 'C:\Windows\py.exe'
$Falhas = New-Object System.Collections.Generic.List[string]

function Write-Titulo([string]$Texto) { Write-Output ''; Write-Output "== $Texto" }

Push-Location $Raiz
try {
    # 1. Python: unittest com cobertura de linhas e ramos. Sem -I: o coverage está nos pacotes do utilizador.
    #    Só conta a lógica do pack (os testes não); abaixo de 100 % falha. A cola com o Windows que não se
    #    testa tem "# pragma: no cover" com o motivo (lista em docs/validacao-manual.md).
    Write-Titulo 'Python (unittest + coverage)'
    & $Py -m coverage run --branch "--source=$Pack" -m unittest discover -s tests
    if ($LASTEXITCODE -ne 0) { $Falhas.Add('Python') }
    & $Py -m coverage report --skip-empty --show-missing --fail-under=100
    if ($LASTEXITCODE -ne 0) { $Falhas.Add('Cobertura Python') }

    # 2. JavaScript: node --test, se houver testes, com cobertura de linhas e ramos dos .mjs do pack (fora
    #    do vendor/): abaixo de 100 % falha. A cola com o DOM e o Zebar fica entre
    #    /* node:coverage disable */ e /* node:coverage enable */, com o motivo (docs/validacao-manual.md).
    #    Uma falha de teste e uma cobertura abaixo do limite dão as duas um código de saída diferente de 0.
    $TestesJs = @(Get-ChildItem -Path (Join-Path $Raiz 'tests') -Recurse -Filter '*.test.mjs' -ErrorAction SilentlyContinue)
    if ($TestesJs.Count -gt 0) {
        Write-Titulo 'JavaScript (node --test + cobertura)'
        & node --test --experimental-test-coverage '--test-coverage-include=2-configuracao/**/*.mjs' `
            '--test-coverage-exclude=**/vendor/**' --test-coverage-lines=100 --test-coverage-branches=100 `
            ($TestesJs | ForEach-Object { $_.FullName })
        if ($LASTEXITCODE -ne 0) { $Falhas.Add('JavaScript (testes ou cobertura)') }
    }

    # 3. PowerShell: Pester 6, se houver testes, com cobertura do scripts\instalar.ps1. Abaixo de 100 % nas
    #    funções não excluídas falha. As excluídas (cola com o Windows) e o motivo de cada uma estão em
    #    $FuncoesExcluidas, no tests\instalar.Comum.ps1 (lido daqui sem o correr).
    $TestesPs = @(Get-ChildItem -Path (Join-Path $Raiz 'tests') -Recurse -Filter '*.Tests.ps1' -ErrorAction SilentlyContinue)
    if ($TestesPs.Count -gt 0) {
        Write-Titulo 'PowerShell (Pester + cobertura do instalar.ps1)'
        Import-Module Pester -MinimumVersion 6.0
        $Config = New-PesterConfiguration
        $Config.Run.Path = [string[]]($TestesPs | ForEach-Object { $_.FullName })
        $Config.Run.PassThru = $true
        $Config.Output.Verbosity = 'Normal'
        $Config.CodeCoverage.Enabled = $true
        $Config.CodeCoverage.Path = [string[]](Join-Path $Raiz 'scripts\instalar.ps1')
        $Config.CodeCoverage.OutputPath = Join-Path $env:TEMP 'morg-keys-cobertura-instalar.xml'
        $Resultado = Invoke-Pester -Configuration $Config
        if ($Resultado.FailedCount -gt 0) { $Falhas.Add('PowerShell') }

        $Arvore = [System.Management.Automation.Language.Parser]::ParseFile((Join-Path $Raiz 'tests\instalar.Comum.ps1'), [ref]$null, [ref]$null)
        $Lista = $Arvore.Find({ param($n) $n -is [System.Management.Automation.Language.AssignmentStatementAst] -and
                                $n.Left.VariablePath.UserPath -eq 'FuncoesExcluidas' }, $true)
        $Excluidas = $Lista.Right.Expression.SafeGetValue()
        # Conta só fora das funções excluídas. A última linha do instalar.ps1 (a chamada a Instalar, o ponto
        # de entrada) só corre pelo INSTALAR.cmd: os testes carregam o ficheiro com ". instalar.ps1".
        $Conta = { param($c) -not ($Excluidas.ContainsKey([string]$c.Function) -or (-not $c.Function -and $c.Command -eq 'Instalar')) }
        $Cobertura = $Resultado.CodeCoverage
        $EmFalta = @($Cobertura.CommandsMissed | Where-Object { & $Conta $_ })
        $Feitos = @($Cobertura.CommandsExecuted | Where-Object { & $Conta $_ })
        $Total = $EmFalta.Count + $Feitos.Count
        Write-Output ("Cobertura do instalar.ps1 fora das {0} funções excluídas: {1}/{2} comandos ({3:N1} %)" -f
            $Excluidas.Count, $Feitos.Count, $Total, (100 * $Feitos.Count / [Math]::Max($Total, 1)))
        $EmFalta | ForEach-Object { Write-Output "  falta: linha $($_.Line) [$($_.Function)] $($_.Command)" }
        if ($Total -eq 0 -or $EmFalta.Count -gt 0) { $Falhas.Add('Cobertura PowerShell') }
    }

    # 4. Lint.
    Write-Titulo 'Lint Python (ruff)'
    & $Py -m ruff check --output-format concise .
    if ($LASTEXITCODE -ne 0) { $Falhas.Add('Lint Python') }

    Write-Titulo 'Lint JavaScript, CSS e HTML (Biome)'
    cmd /c 'npx --no-install biome lint --error-on-warnings 2>&1'
    if ($LASTEXITCODE -ne 0) { $Falhas.Add('Lint JS/CSS') }

    Write-Titulo 'Lint PowerShell (PSScriptAnalyzer: só os erros bloqueiam)'
    Import-Module PSScriptAnalyzer
    $Achados = @(Get-ChildItem -Path $Raiz -Recurse -Include '*.ps1', '*.psm1' -File |
        Where-Object { $_.FullName -notmatch '\\node_modules\\' } |
        ForEach-Object { Invoke-ScriptAnalyzer -Path $_.FullName })
    $Achados | Group-Object Severity, RuleName | Select-Object Count, Name | Format-Table -AutoSize | Out-String -Width 200
    $Erros = @($Achados | Where-Object { $_.Severity -in 'Error', 'ParseError' })
    $Erros | ForEach-Object { Write-Output "$($_.ScriptName):$($_.Line) $($_.RuleName): $($_.Message)" }
    if ($Erros.Count -gt 0) { $Falhas.Add('Lint PowerShell') }
}
finally {
    Pop-Location
}

Write-Titulo 'Resultado'
if ($Falhas.Count -gt 0) {
    Write-Output ("FALHOU: " + ($Falhas -join ', '))
    exit 1
}
Write-Output 'OK: todos os testes passaram.'
exit 0
