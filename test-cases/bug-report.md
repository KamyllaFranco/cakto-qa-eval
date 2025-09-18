# Relatório de Bugs - Avaliação QA Cakto

## Resumo Executivo

Durante a análise da API de usuários, foram identificados **6 bugs críticos** que afetam a funcionalidade, validação de dados e performance da aplicação.

## Bugs Identificados

### 🐛 Bug #1: Emails Duplicados no Banco de Dados
**Severidade:** Alta  
**Categoria:** Inconsistência de Dados  
**Endpoint:** GET /users

**Descrição:**
A API retorna usuários com emails duplicados, violando a integridade dos dados.

**Dados Encontrados:**
- Usuário ID 2: "maria@email.com" 
- Usuário ID 6: "maria@email.com" (duplicado)

**Resultado Esperado:**
Cada usuário deve ter um email único no sistema.

**Resultado Atual:**
Sistema permite e retorna emails duplicados.

**Passos para Reproduzir:**
1. Fazer GET /users
2. Verificar emails dos usuários retornados
3. Observar duplicação do email "maria@email.com"

**Observação:** Este bug foi encontrado durante os testes manuais iniciais.

**Sugestão de Correção:**
- Implementar validação de unicidade no banco de dados
- Adicionar constraint UNIQUE na coluna email
- Validar duplicação antes de inserir novos usuários

---

### 🐛 Bug #2: Tipo de Dados Incorreto para Campo Age
**Severidade:** Alta  
**Categoria:** Inconsistência de Dados  
**Endpoint:** GET /users

**Descrição:**
O campo `age` do usuário ID 7 contém uma string "thirty" em vez de um número.

**Dados Encontrados:**
```json
{
  "id": 7,
  "name": "Roberto Lima",
  "email": "roberto@email.com",
  "age": "thirty",  // ❌ Deveria ser um número
  "status": "active"
}
```

**Resultado Esperado:**
Campo `age` deve sempre ser um número inteiro.

**Resultado Atual:**
Campo `age` contém string "thirty".

**Passos para Reproduzir:**
1. Fazer GET /users
2. Verificar o campo `age` do usuário ID 7
3. Observar que contém string em vez de número

**Nota:** Este é um bug interessante - o campo deveria ser sempre numérico.

**Sugestão de Correção:**
- Implementar validação de tipo no banco de dados
- Adicionar validação no backend para aceitar apenas números
- Converter strings numéricas para inteiros durante a inserção

---

### 🐛 Bug #3: Erro de Content-Length no POST
**Severidade:** Média  
**Categoria:** Problemas de Estado  
**Endpoint:** POST /users

**Descrição:**
Ao tentar criar um usuário via POST, a API retorna erro de Content-Length.

**Erro Retornado:**
```json
{
  "error": "Internal server error",
  "details": "Request body size did not match Content-Length",
  "stack": "FastifyError: Request body size did not match Content-Length"
}
```

**Resultado Esperado:**
POST /users deve criar usuário com sucesso retornando 201 Created.

**Resultado Atual:**
Erro 500 Internal Server Error com problema de Content-Length.

**Passos para Reproduzir:**
1. Fazer POST /users com dados válidos
2. Observar erro de Content-Length

**Sugestão de Correção:**
- Corrigir configuração do Fastify para Content-Length
- Verificar middleware de parsing de JSON
- Implementar tratamento adequado de Content-Length

---

### 🐛 Bug #4: Falta de Validação para Página Negativa
**Severidade:** Média  
**Categoria:** Validação Inconsistente  
**Endpoint:** GET /users?page=-1

**Descrição:**
A API aceita valores negativos para o parâmetro `page` sem retornar erro.

**Resultado Esperado:**
Página negativa deveria retornar 400 Bad Request.

**Resultado Atual:**
API processa página negativa sem erro.

**Passos para Reproduzir:**
1. Fazer GET /users?page=-1
2. Observar que não retorna erro 400

**Sugestão de Correção:**
- Implementar validação para page >= 1
- Retornar 400 Bad Request para valores inválidos
- Adicionar mensagem de erro descritiva

---

### 🐛 Bug #5: Falta de Validação para Limite Excessivo
**Severidade:** Média  
**Categoria:** Problemas de Performance  
**Endpoint:** GET /users?limit=10000

**Descrição:**
A API aceita valores excessivamente altos para o parâmetro `limit` sem validação.

**Resultado Esperado:**
Limite excessivo deveria retornar 400 Bad Request ou limitar automaticamente.

**Resultado Atual:**
API processa limite de 10000 sem validação.

**Passos para Reproduzir:**
1. Fazer GET /users?limit=10000
2. Observar que não retorna erro 400

**Sugestão de Correção:**
- Implementar limite máximo (ex: 100)
- Retornar 400 Bad Request para limites excessivos
- Adicionar validação de range para o parâmetro limit

---

### 🐛 Bug #6: Endpoint Slow-Endpoint Não Funciona
**Severidade:** Baixa  
**Categoria:** Problemas de Performance  
**Endpoint:** GET /slow-endpoint

**Descrição:**
O endpoint /slow-endpoint não responde ou não está implementado corretamente.

**Resultado Esperado:**
Endpoint deveria retornar resposta lenta (>5 segundos).

**Resultado Atual:**
Endpoint não responde ou falha.

**Passos para Reproduzir:**
1. Fazer GET /slow-endpoint
2. Observar que não retorna resposta

**Sugestão de Correção:**
- Implementar endpoint que simule operação lenta
- Adicionar delay artificial de 5+ segundos
- Retornar resposta válida após o delay

---

## Resumo por Categoria

| Categoria | Quantidade | Severidade |
|-----------|------------|------------|
| Inconsistência de Dados | 2 | Alta |
| Validação Inconsistente | 1 | Média |
| Problemas de Estado | 1 | Média |
| Problemas de Performance | 2 | Média/Baixa |

## Recomendações Gerais

1. **Implementar validação robusta** em todos os endpoints
2. **Adicionar constraints de banco de dados** para integridade
3. **Melhorar tratamento de erros** com mensagens descritivas
4. **Implementar testes automatizados** para regressão
5. **Adicionar logging** para monitoramento de problemas
6. **Revisar configuração do servidor** (Content-Length, etc.)

## Próximos Passos

1. Priorizar correção dos bugs de severidade Alta
2. Implementar testes automatizados para prevenir regressões
3. Adicionar validações de entrada em todos os endpoints
4. Revisar e corrigir configurações do servidor
5. Implementar monitoramento de performance
