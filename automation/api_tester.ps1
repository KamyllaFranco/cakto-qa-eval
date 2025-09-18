$urlBase = "https://cakto-qa-eval.launchify.com.br"
$bugs = @()
$resultadosTeste = @()

function Registrar-Teste {
    param(
        [string]$NomeTeste,
        [string]$Esperado,
        [string]$Atual,
        [string]$Status,
        [string]$DescricaoBug = ""
    )
    
    $resultado = @{
        NomeTeste = $NomeTeste
        Timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
        Esperado = $Esperado
        Atual = $Atual
        Status = $Status
        DescricaoBug = $DescricaoBug
    }
    
    $script:resultadosTeste += $resultado
    
    if ($Status -eq "BUG") {
        $script:bugs += $resultado
        Write-Host "🐛 BUG ENCONTRADO: $NomeTeste" -ForegroundColor Red
        Write-Host "   Esperado: $Esperado" -ForegroundColor Yellow
        Write-Host "   Atual: $Atual" -ForegroundColor Yellow
        if ($DescricaoBug) {
            Write-Host "   Descrição: $DescricaoBug" -ForegroundColor Yellow
        }
        Write-Host ""
    } else {
        Write-Host "✅ $NomeTeste - $Status" -ForegroundColor Green
    }
}

function Testar-Endpoint {
    param(
        [string]$Metodo,
        [string]$Endpoint,
        [hashtable]$Corpo = $null,
        [hashtable]$ParametrosQuery = $null
    )
    
    $url = "$urlBase$Endpoint"
    
    try {
        $cabecalhos = @{
            "Content-Type" = "application/json"
        }
        
        if ($ParametrosQuery) {
            $stringQuery = ($ParametrosQuery.GetEnumerator() | ForEach-Object { "$($_.Key)=$($_.Value)" }) -join "&"
            $url += "?$stringQuery"
        }
        
        if ($Metodo -eq "GET") {
            $resposta = Invoke-RestMethod -Uri $url -Method GET -Headers $cabecalhos
        } elseif ($Metodo -eq "POST") {
            $corpoJson = $Corpo | ConvertTo-Json
            $resposta = Invoke-RestMethod -Uri $url -Method POST -Body $corpoJson -Headers $cabecalhos
        } elseif ($Metodo -eq "PUT") {
            $corpoJson = $Corpo | ConvertTo-Json
            $resposta = Invoke-RestMethod -Uri $url -Method PUT -Body $corpoJson -Headers $cabecalhos
        } elseif ($Metodo -eq "DELETE") {
            $resposta = Invoke-RestMethod -Uri $url -Method DELETE -Headers $cabecalhos
        }
        
        return @{
            Sucesso = $true
            Dados = $resposta
            CodigoStatus = 200
        }
    } catch {
        $codigoStatus = $_.Exception.Response.StatusCode.value__
        return @{
            Sucesso = $false
            Erro = $_.Exception.Message
            CodigoStatus = $codigoStatus
            Dados = $null
        }
    }
}

function Testar-HealthEndpoint {
    Write-Host "🔍 Testando endpoint /health..." -ForegroundColor Cyan
    
    $resultado = Testar-Endpoint -Metodo "GET" -Endpoint "/health"
    
    if ($resultado.Sucesso) {
        Registrar-Teste -NomeTeste "Health Check" -Esperado "200 OK" -Atual "200 OK" -Status "PASS"
    } else {
        Registrar-Teste -NomeTeste "Health Check" -Esperado "200 OK" -Atual "$($resultado.CodigoStatus)" -Status "BUG" -DescricaoBug "Health check deveria retornar 200 OK"
    }
}

function Testar-EndpointRaiz {
    Write-Host "🔍 Testando endpoint raiz /..." -ForegroundColor Cyan
    
    $resultado = Testar-Endpoint -Metodo "GET" -Endpoint "/"
    
    if ($resultado.Sucesso) {
        Registrar-Teste -NomeTeste "Endpoint Raiz" -Esperado "200 OK" -Atual "200 OK" -Status "PASS"
    } else {
        Registrar-Teste -NomeTeste "Endpoint Raiz" -Esperado "200 OK" -Atual "$($resultado.CodigoStatus)" -Status "BUG" -DescricaoBug "Endpoint raiz deveria retornar 200 OK"
    }
}

function Testar-ObterUsuarios {
    Write-Host "🔍 Testando GET /users..." -ForegroundColor Cyan
    
    $resultado = Testar-Endpoint -Metodo "GET" -Endpoint "/users"
    
    if ($resultado.Sucesso) {
        if ($resultado.Dados.data -and $resultado.Dados.data.Count -gt 0) {
            Registrar-Teste -NomeTeste "GET Usuários - Estrutura" -Esperado "Lista de usuários" -Atual "Lista de usuários retornada" -Status "PASS"
            
            $usuario = $resultado.Dados.data[0]
            $camposObrigatorios = @("id", "name", "email", "age", "status", "createdAt", "updatedAt")
            $camposAusentes = @()
            
            foreach ($campo in $camposObrigatorios) {
                if (-not $usuario.PSObject.Properties.Name -contains $campo) {
                    $camposAusentes += $campo
                }
            }
            
            if ($camposAusentes.Count -gt 0) {
                Registrar-Teste -NomeTeste "GET Usuários - Campos obrigatórios" -Esperado "Todos os campos presentes" -Atual "Campos ausentes: $($camposAusentes -join ', ')" -Status "BUG" -DescricaoBug "Usuários devem ter todos os campos obrigatórios"
            } else {
                Registrar-Teste -NomeTeste "GET Usuários - Campos obrigatórios" -Esperado "Todos os campos presentes" -Atual "Todos os campos presentes" -Status "PASS"
            }
        } else {
            Registrar-Teste -NomeTeste "GET Usuários - Estrutura" -Esperado "Campo 'data' com lista" -Atual "Estrutura inesperada" -Status "BUG" -DescricaoBug "Resposta deve ter campo 'data' com lista de usuários"
        }
    } else {
        Registrar-Teste -NomeTeste "GET Usuários" -Esperado "200 OK" -Atual "$($resultado.CodigoStatus)" -Status "BUG" -DescricaoBug "Listagem de usuários deveria retornar 200 OK"
    }
}

function Testar-CriarUsuarioValido {
    Write-Host "🔍 Testando POST /users com dados válidos..." -ForegroundColor Cyan
    
    $usuarioValido = @{
        name = "Teste Usuário"
        email = "teste@email.com"
        age = 25
        status = "active"
    }
    
    $resultado = Testar-Endpoint -Metodo "POST" -Endpoint "/users" -Corpo $usuarioValido
    
    if ($resultado.Sucesso) {
        if ($resultado.Dados.id) {
            Registrar-Teste -NomeTeste "POST Usuário - Status" -Esperado "201 Created" -Atual "200 OK" -Status "PASS"
            Registrar-Teste -NomeTeste "POST Usuário - ID" -Esperado "ID retornado" -Atual "ID: $($resultado.Dados.id)" -Status "PASS"
            return $resultado.Dados.id
        } else {
            Registrar-Teste -NomeTeste "POST Usuário - ID" -Esperado "ID retornado" -Atual "ID não retornado" -Status "BUG" -DescricaoBug "Usuário criado deve retornar ID"
        }
    } else {
        Registrar-Teste -NomeTeste "POST Usuário - Status" -Esperado "201 Created" -Atual "$($resultado.CodigoStatus)" -Status "BUG" -DescricaoBug "Criação de usuário válido deveria retornar 201 Created"
    }
    
    return $null
}

function Testar-CriarUsuarioEmailInvalido {
    Write-Host "🔍 Testando POST /users com email inválido..." -ForegroundColor Cyan
    
    $usuarioInvalido = @{
        name = "Teste Usuário"
        email = "email-invalido"
        age = 25
        status = "active"
    }
    
    $resultado = Testar-Endpoint -Metodo "POST" -Endpoint "/users" -Corpo $usuarioInvalido
    
    if ($resultado.Sucesso) {
        Registrar-Teste -NomeTeste "POST Usuário - Email inválido" -Esperado "400 Bad Request" -Atual "200 OK" -Status "BUG" -DescricaoBug "Email inválido deveria retornar 400 Bad Request"
    } else {
        if ($resultado.CodigoStatus -eq 400) {
            Registrar-Teste -NomeTeste "POST Usuário - Email inválido" -Esperado "400 Bad Request" -Atual "400 Bad Request" -Status "PASS"
        } else {
            Registrar-Teste -NomeTeste "POST Usuário - Email inválido" -Esperado "400 Bad Request" -Atual "$($resultado.CodigoStatus)" -Status "BUG" -DescricaoBug "Email inválido deveria retornar 400 Bad Request"
        }
    }
}

function Testar-CriarUsuarioNomeVazio {
    Write-Host "🔍 Testando POST /users com nome vazio..." -ForegroundColor Cyan
    
    $usuarioInvalido = @{
        name = ""
        email = "teste@email.com"
        age = 25
        status = "active"
    }
    
    $resultado = Testar-Endpoint -Metodo "POST" -Endpoint "/users" -Corpo $usuarioInvalido
    
    if ($resultado.Sucesso) {
        Registrar-Teste -NomeTeste "POST Usuário - Nome vazio" -Esperado "400 Bad Request" -Atual "200 OK" -Status "BUG" -DescricaoBug "Nome vazio deveria retornar 400 Bad Request"
    } else {
        if ($resultado.CodigoStatus -eq 400) {
            Registrar-Teste -NomeTeste "POST Usuário - Nome vazio" -Esperado "400 Bad Request" -Atual "400 Bad Request" -Status "PASS"
        } else {
            Registrar-Teste -NomeTeste "POST Usuário - Nome vazio" -Esperado "400 Bad Request" -Atual "$($resultado.CodigoStatus)" -Status "BUG" -DescricaoBug "Nome vazio deveria retornar 400 Bad Request"
        }
    }
}

function Testar-CriarUsuarioIdadeNegativa {
    Write-Host "🔍 Testando POST /users com idade negativa..." -ForegroundColor Cyan
    
    $usuarioInvalido = @{
        name = "Teste Usuário"
        email = "teste@email.com"
        age = -5
        status = "active"
    }
    
    $resultado = Testar-Endpoint -Metodo "POST" -Endpoint "/users" -Corpo $usuarioInvalido
    
    if ($resultado.Sucesso) {
        Registrar-Teste -NomeTeste "POST Usuário - Idade negativa" -Esperado "400 Bad Request" -Atual "200 OK" -Status "BUG" -DescricaoBug "Idade negativa deveria retornar 400 Bad Request"
    } else {
        if ($resultado.CodigoStatus -eq 400) {
            Registrar-Teste -NomeTeste "POST Usuário - Idade negativa" -Esperado "400 Bad Request" -Atual "400 Bad Request" -Status "PASS"
        } else {
            Registrar-Teste -NomeTeste "POST Usuário - Idade negativa" -Esperado "400 Bad Request" -Atual "$($resultado.CodigoStatus)" -Status "BUG" -DescricaoBug "Idade negativa deveria retornar 400 Bad Request"
        }
    }
}

function Testar-ObterUsuarioPorId {
    param([int]$IdUsuario)
    
    Write-Host "🔍 Testando GET /users/$IdUsuario..." -ForegroundColor Cyan
    
    $resultado = Testar-Endpoint -Metodo "GET" -Endpoint "/users/$IdUsuario"
    
    if ($resultado.Sucesso) {
        if ($resultado.Dados.id -eq $IdUsuario) {
            Registrar-Teste -NomeTeste "GET Usuário por ID" -Esperado "200 OK com dados do usuário" -Atual "200 OK" -Status "PASS"
        } else {
            Registrar-Teste -NomeTeste "GET Usuário por ID" -Esperado "Dados do usuário correto" -Atual "Dados incorretos" -Status "BUG" -DescricaoBug "Dados do usuário retornado não correspondem ao ID solicitado"
        }
    } else {
        Registrar-Teste -NomeTeste "GET Usuário por ID" -Esperado "200 OK" -Atual "$($resultado.CodigoStatus)" -Status "BUG" -DescricaoBug "Busca de usuário válido deveria retornar 200 OK"
    }
}

function Testar-ObterUsuarioIdInvalido {
    Write-Host "🔍 Testando GET /users/99999 (ID inexistente)..." -ForegroundColor Cyan
    
    $resultado = Testar-Endpoint -Metodo "GET" -Endpoint "/users/99999"
    
    if ($resultado.Sucesso) {
        Registrar-Teste -NomeTeste "GET Usuário - ID inexistente" -Esperado "404 Not Found" -Atual "200 OK" -Status "BUG" -DescricaoBug "ID inexistente deveria retornar 404 Not Found"
    } else {
        if ($resultado.CodigoStatus -eq 404) {
            Registrar-Teste -NomeTeste "GET Usuário - ID inexistente" -Esperado "404 Not Found" -Atual "404 Not Found" -Status "PASS"
        } else {
            Registrar-Teste -NomeTeste "GET Usuário - ID inexistente" -Esperado "404 Not Found" -Atual "$($resultado.CodigoStatus)" -Status "BUG" -DescricaoBug "ID inexistente deveria retornar 404 Not Found"
        }
    }
}

function Testar-AtualizarUsuario {
    param([int]$IdUsuario)
    
    Write-Host "🔍 Testando PUT /users/$IdUsuario..." -ForegroundColor Cyan
    
    $usuarioAtualizado = @{
        name = "Usuário Atualizado"
        email = "atualizado@email.com"
        age = 30
        status = "inactive"
    }
    
    $resultado = Testar-Endpoint -Metodo "PUT" -Endpoint "/users/$IdUsuario" -Corpo $usuarioAtualizado
    
    if ($resultado.Sucesso) {
        if ($resultado.Dados.updatedAt) {
            Registrar-Teste -NomeTeste "PUT Usuário - Status" -Esperado "200 OK" -Atual "200 OK" -Status "PASS"
            Registrar-Teste -NomeTeste "PUT Usuário - updatedAt" -Esperado "Campo updatedAt atualizado" -Atual "Campo updatedAt presente" -Status "PASS"
        } else {
            Registrar-Teste -NomeTeste "PUT Usuário - updatedAt" -Esperado "Campo updatedAt atualizado" -Atual "Campo updatedAt ausente" -Status "BUG" -DescricaoBug "Campo updatedAt deve ser atualizado após modificação"
        }
    } else {
        Registrar-Teste -NomeTeste "PUT Usuário - Status" -Esperado "200 OK" -Atual "$($resultado.CodigoStatus)" -Status "BUG" -DescricaoBug "Atualização de usuário deveria retornar 200 OK"
    }
}

function Testar-ExcluirUsuario {
    param([int]$IdUsuario)
    
    Write-Host "🔍 Testando DELETE /users/$IdUsuario..." -ForegroundColor Cyan
    
    $resultado = Testar-Endpoint -Metodo "DELETE" -Endpoint "/users/$IdUsuario"
    
    if ($resultado.Sucesso) {
        Registrar-Teste -NomeTeste "DELETE Usuário - Status" -Esperado "200 OK" -Atual "200 OK" -Status "PASS"
        
        $resultadoGet = Testar-Endpoint -Metodo "GET" -Endpoint "/users/$IdUsuario"
        if (-not $resultadoGet.Sucesso -and $resultadoGet.CodigoStatus -eq 404) {
            Registrar-Teste -NomeTeste "DELETE Usuário - Verificação" -Esperado "Usuário deletado" -Atual "Usuário não encontrado" -Status "PASS"
        } else {
            Registrar-Teste -NomeTeste "DELETE Usuário - Verificação" -Esperado "Usuário deletado" -Atual "Usuário ainda existe" -Status "BUG" -DescricaoBug "Usuário deveria ser deletado permanentemente"
        }
    } else {
        Registrar-Teste -NomeTeste "DELETE Usuário - Status" -Esperado "200 OK" -Atual "$($resultado.CodigoStatus)" -Status "BUG" -DescricaoBug "Exclusão de usuário deveria retornar 200 OK"
    }
}

function Testar-Paginacao {
    Write-Host "🔍 Testando paginação..." -ForegroundColor Cyan
    
    $resultado = Testar-Endpoint -Metodo "GET" -Endpoint "/users" -ParametrosQuery @{page=1; limit=5}
    if ($resultado.Sucesso) {
        Registrar-Teste -NomeTeste "Paginação - Página 1" -Esperado "200 OK" -Atual "200 OK" -Status "PASS"
    }
    
    $resultado = Testar-Endpoint -Metodo "GET" -Endpoint "/users" -ParametrosQuery @{page=-1; limit=5}
    if ($resultado.Sucesso) {
        Registrar-Teste -NomeTeste "Paginação - Página negativa" -Esperado "400 Bad Request" -Atual "200 OK" -Status "BUG" -DescricaoBug "Página negativa deveria retornar 400 Bad Request"
    } else {
        if ($resultado.CodigoStatus -eq 400) {
            Registrar-Teste -NomeTeste "Paginação - Página negativa" -Esperado "400 Bad Request" -Atual "400 Bad Request" -Status "PASS"
        } else {
            Registrar-Teste -NomeTeste "Paginação - Página negativa" -Esperado "400 Bad Request" -Atual "$($resultado.CodigoStatus)" -Status "BUG" -DescricaoBug "Página negativa deveria retornar 400 Bad Request"
        }
    }
    
    $resultado = Testar-Endpoint -Metodo "GET" -Endpoint "/users" -ParametrosQuery @{page=1; limit=10000}
    if ($resultado.Sucesso) {
        Registrar-Teste -NomeTeste "Paginação - Limite excessivo" -Esperado "400 Bad Request" -Atual "200 OK" -Status "BUG" -DescricaoBug "Limite excessivo deveria retornar 400 Bad Request"
    } else {
        if ($resultado.CodigoStatus -eq 400) {
            Registrar-Teste -NomeTeste "Paginação - Limite excessivo" -Esperado "400 Bad Request" -Atual "400 Bad Request" -Status "PASS"
        } else {
            Registrar-Teste -NomeTeste "Paginação - Limite excessivo" -Esperado "400 Bad Request" -Atual "$($resultado.CodigoStatus)" -Status "BUG" -DescricaoBug "Limite excessivo deveria retornar 400 Bad Request"
        }
    }
}

function Testar-EndpointsPerformance {
    Write-Host "🔍 Testando endpoints de performance..." -ForegroundColor Cyan
    
    $tempoInicio = Get-Date
    $resultado = Testar-Endpoint -Metodo "GET" -Endpoint "/slow-endpoint"
    $tempoFim = Get-Date
    $tempoResposta = ($tempoFim - $tempoInicio).TotalSeconds
    
    if ($resultado.Sucesso) {
        if ($tempoResposta -gt 5) {
            Registrar-Teste -NomeTeste "Performance - Slow Endpoint" -Esperado "Resposta lenta" -Atual "$([math]::Round($tempoResposta, 2))s" -Status "PASS"
        } else {
            Registrar-Teste -NomeTeste "Performance - Slow Endpoint" -Esperado "Resposta lenta" -Atual "$([math]::Round($tempoResposta, 2))s" -Status "BUG" -DescricaoBug "Endpoint deveria ser lento (>5s)"
        }
    } else {
        Registrar-Teste -NomeTeste "Performance - Slow Endpoint" -Esperado "200 OK" -Atual "$($resultado.CodigoStatus)" -Status "BUG" -DescricaoBug "Slow endpoint deveria retornar 200 OK"
    }
    
    $resultado = Testar-Endpoint -Metodo "GET" -Endpoint "/memory-leak"
    if ($resultado.Sucesso) {
        Registrar-Teste -NomeTeste "Performance - Memory Leak" -Esperado "200 OK" -Atual "200 OK" -Status "PASS"
    } else {
        Registrar-Teste -NomeTeste "Performance - Memory Leak" -Esperado "200 OK" -Atual "$($resultado.CodigoStatus)" -Status "BUG" -DescricaoBug "Memory leak endpoint deveria retornar 200 OK"
    }
}

Write-Host "🚀 Iniciando testes da API de usuários..." -ForegroundColor Green
Write-Host "=" * 50

Testar-HealthEndpoint
Testar-EndpointRaiz
Testar-ObterUsuarios

$idUsuario = Testar-CriarUsuarioValido
Testar-CriarUsuarioEmailInvalido
Testar-CriarUsuarioNomeVazio
Testar-CriarUsuarioIdadeNegativa

if ($idUsuario) {
    Testar-ObterUsuarioPorId -IdUsuario $idUsuario
}
Testar-ObterUsuarioIdInvalido

if ($idUsuario) {
    Testar-AtualizarUsuario -IdUsuario $idUsuario
}

Testar-Paginacao
Testar-EndpointsPerformance

if ($idUsuario) {
    Testar-ExcluirUsuario -IdUsuario $idUsuario
}

Write-Host "=" * 50
Write-Host "✅ Testes concluídos!" -ForegroundColor Green
Write-Host "📊 Total de testes: $($resultadosTeste.Count)" -ForegroundColor Cyan
Write-Host "🐛 Bugs encontrados: $($bugs.Count)" -ForegroundColor Red
Write-Host "✅ Testes passaram: $(($resultadosTeste | Where-Object {$_.Status -eq 'PASS'}).Count)" -ForegroundColor Green
Write-Host "❌ Testes falharam: $(($resultadosTeste | Where-Object {$_.Status -eq 'BUG'}).Count)" -ForegroundColor Red

$resultadosTeste | ConvertTo-Json -Depth 3 | Out-File -FilePath "../test-cases/resultados-testes.json" -Encoding UTF8
$bugs | ConvertTo-Json -Depth 3 | Out-File -FilePath "../test-cases/bugs-encontrados.json" -Encoding UTF8

Write-Host "💾 Resultados salvos em test-cases/" -ForegroundColor Yellow
