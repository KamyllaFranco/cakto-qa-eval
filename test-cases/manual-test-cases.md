# Casos de Teste Manuais - Avaliação QA Cakto

## Informações Gerais
- **API:** Avaliação QA Cakto - API de Usuários
- **URL Base:** https://cakto-qa-eval.launchify.com.br
- **Data de Execução:** 17/09/2025
- **Testador:** Analista de Testes

## Casos de Teste Executados

### CT001 - Health Check
**Objetivo:** Verificar se o endpoint de health check está funcionando

**Pré-condições:**
- API deve estar disponível

**Passos:**
1. Fazer GET /health
2. Verificar status code da resposta

**Resultado Esperado:**
- Status Code: 200 OK
- Resposta contendo informações de saúde da API

**Resultado Atual:**
- ✅ Status Code: 200 OK
- ✅ Endpoint funcionando corretamente

**Status:** PASS

---

### CT002 - Root Endpoint
**Objetivo:** Verificar se o endpoint raiz retorna informações da API

**Pré-condições:**
- API deve estar disponível

**Passos:**
1. Fazer GET /
2. Verificar estrutura da resposta

**Resultado Esperado:**
- Status Code: 200 OK
- JSON com informações da API (nome, versão, endpoints)

**Resultado Atual:**
- ✅ Status Code: 200 OK
- ✅ Resposta: {"message": "Cakto QA Evaluation API", "version": "1.0.0", "endpoints": {...}}

**Status:** PASS

---

### CT003 - Listar Usuários
**Objetivo:** Verificar se a listagem de usuários funciona corretamente

**Pré-condições:**
- API deve estar disponível
- Deve haver usuários cadastrados

**Passos:**
1. Fazer GET /users
2. Verificar estrutura da resposta
3. Verificar campos obrigatórios dos usuários

**Resultado Esperado:**
- Status Code: 200 OK
- Estrutura: {"data": [...], "pagination": {...}}
- Campos obrigatórios: id, name, email, age, status, createdAt, updatedAt

**Resultado Atual:**
- ✅ Status Code: 200 OK
- ✅ Estrutura correta
- ✅ Campos obrigatórios presentes
- 🐛 **BUG:** Emails duplicados (maria@email.com)
- 🐛 **BUG:** Campo age com string "thirty" (ID 7)

**Status:** BUG

---

### CT004 - Criar Usuário Válido
**Objetivo:** Verificar se é possível criar um usuário com dados válidos

**Pré-condições:**
- API deve estar disponível

**Passos:**
1. Fazer POST /users com dados válidos
2. Verificar status code e resposta

**Dados de Teste:**
```json
{
  "name": "Teste Usuário",
  "email": "teste@email.com",
  "age": 25,
  "status": "active"
}
```

**Resultado Esperado:**
- Status Code: 201 Created
- Resposta contendo ID do usuário criado

**Resultado Atual:**
- 🐛 **BUG:** Erro 500 - "Request body size did not match Content-Length"

**Status:** BUG

---

### CT005 - Buscar Usuário por ID Válido
**Objetivo:** Verificar se é possível buscar um usuário existente por ID

**Pré-condições:**
- Usuário com ID 1 deve existir

**Passos:**
1. Fazer GET /users/1
2. Verificar resposta

**Resultado Esperado:**
- Status Code: 200 OK
- Dados do usuário com ID 1

**Resultado Atual:**
- ✅ Status Code: 200 OK
- ✅ Dados do usuário retornados corretamente

**Status:** PASS

---

### CT006 - Buscar Usuário por ID Inexistente
**Objetivo:** Verificar comportamento ao buscar usuário inexistente

**Pré-condições:**
- Usuário com ID 99999 não deve existir

**Passos:**
1. Fazer GET /users/99999
2. Verificar status code

**Resultado Esperado:**
- Status Code: 404 Not Found

**Resultado Atual:**
- ✅ Status Code: 404 Not Found

**Status:** PASS

---

### CT007 - Paginação com Página Negativa
**Objetivo:** Verificar validação de página negativa

**Pré-condições:**
- API deve estar disponível

**Passos:**
1. Fazer GET /users?page=-1
2. Verificar status code

**Resultado Esperado:**
- Status Code: 400 Bad Request

**Resultado Atual:**
- 🐛 **BUG:** Status Code: 200 OK (deveria ser 400)

**Status:** BUG

---

### CT008 - Paginação com Limite Excessivo
**Objetivo:** Verificar validação de limite excessivo

**Pré-condições:**
- API deve estar disponível

**Passos:**
1. Fazer GET /users?limit=10000
2. Verificar status code

**Resultado Esperado:**
- Status Code: 400 Bad Request ou limite automático

**Resultado Atual:**
- 🐛 **BUG:** Status Code: 200 OK (deveria validar limite)

**Status:** BUG

---

### CT009 - Endpoint de Performance - Slow Endpoint
**Objetivo:** Verificar se o endpoint lento funciona

**Pré-condições:**
- API deve estar disponível

**Passos:**
1. Fazer GET /slow-endpoint
2. Medir tempo de resposta
3. Verificar se é > 5 segundos

**Resultado Esperado:**
- Tempo de resposta > 5 segundos
- Status Code: 200 OK

**Resultado Atual:**
- 🐛 **BUG:** Endpoint não responde ou falha

**Status:** BUG

---

### CT010 - Endpoint de Performance - Memory Leak
**Objetivo:** Verificar se o endpoint de memory leak funciona

**Pré-condições:**
- API deve estar disponível

**Passos:**
1. Fazer GET /memory-leak
2. Verificar resposta

**Resultado Esperado:**
- Status Code: 200 OK
- Resposta indicando teste de memory leak

**Resultado Atual:**
- ✅ Status Code: 200 OK
- ✅ Resposta: {"message": "Memory leak test completed", "size": 100000}

**Status:** PASS

---

## Resumo dos Resultados

| Caso de Teste | Status | Observações |
|---------------|--------|-------------|
| CT001 - Health Check | ✅ PASS | Funcionando corretamente |
| CT002 - Root Endpoint | ✅ PASS | Funcionando corretamente |
| CT003 - Listar Usuários | 🐛 BUG | Emails duplicados e tipo incorreto |
| CT004 - Criar Usuário | 🐛 BUG | Erro de Content-Length |
| CT005 - Buscar por ID | ✅ PASS | Funcionando corretamente |
| CT006 - ID Inexistente | ✅ PASS | Funcionando corretamente |
| CT007 - Página Negativa | 🐛 BUG | Falta validação |
| CT008 - Limite Excessivo | 🐛 BUG | Falta validação |
| CT009 - Slow Endpoint | 🐛 BUG | Endpoint não funciona |
| CT010 - Memory Leak | ✅ PASS | Funcionando corretamente |

## Estatísticas
- **Total de Testes:** 10
- **Passou:** 5 (50%)
- **Falhou (Bugs):** 5 (50%)
- **Bugs Críticos:** 2
- **Bugs de Validação:** 2
- **Bugs de Performance:** 1

## Observações Gerais

1. **Problemas de Validação:** A API não valida adequadamente parâmetros de entrada
2. **Inconsistência de Dados:** Existem problemas de integridade no banco de dados
3. **Problemas de Configuração:** Erro de Content-Length indica problema de configuração do servidor
4. **Endpoints de Performance:** Um dos endpoints de teste não está funcionando

## Recomendações

1. Implementar validação robusta em todos os endpoints
2. Corrigir problemas de integridade de dados
3. Revisar configuração do servidor
4. Implementar testes automatizados para regressão
5. Adicionar logging para monitoramento
