# Automação de Testes - Avaliação QA Cakto

## Visão Geral

Este diretório contém scripts de automação para testar a API de usuários da Avaliação QA Cakto. Os testes foram desenvolvidos para identificar bugs propositais na API.

## Estrutura de Arquivos

```
automation/
├── README.md                    # Este arquivo
├── requirements.txt             # Dependências Python (opcional)
├── api_tester.py               # Script completo de testes (requer requests)
├── simple_api_tester.py        # Script simplificado (só urllib)
├── api_tester.ps1              # Script PowerShell
└── tests/
    └── test_api_basic.py       # Testes básicos automatizados
```

## Scripts Disponíveis

### 1. teste_api_basico.py (Recomendado)
**Linguagem:** Python  
**Dependências:** Apenas bibliotecas padrão do Python  
**Uso:** `python teste_api_basico.py`

**Testes Incluídos:**
- Health Check
- Estrutura da resposta GET /users
- Verificação de emails duplicados
- Validação de tipos de dados (campo age)
- Paginação com página negativa
- Paginação com limite excessivo
- Busca de usuário inexistente
- Endpoint de memory leak

### 2. testador_api.ps1
**Linguagem:** PowerShell  
**Dependências:** Apenas PowerShell nativo  
**Uso:** `PowerShell -ExecutionPolicy Bypass -File testador_api.ps1`

**Funcionalidades:**
- Testes completos de CRUD
- Testes de validação
- Testes de performance
- Geração de relatórios JSON

### 3. simple_api_tester.py
**Linguagem:** Python  
**Dependências:** Apenas bibliotecas padrão do Python  
**Uso:** `python simple_api_tester.py`

**Funcionalidades:**
- Testes completos da API
- Usa urllib em vez de requests
- Geração de relatórios detalhados

## Como Executar

### Opção 1: Testes Básicos (Recomendado)
```bash
cd automation/tests
python teste_api_basico.py
```

### Opção 2: PowerShell
```bash
PowerShell -ExecutionPolicy Bypass -File automation/testador_api.ps1
```

### Opção 3: Python Completo
```bash
cd automation
python simple_api_tester.py
```

## Resultados

Os scripts geram os seguintes arquivos de resultado:

- `test-cases/automated-test-results.json` - Resultados completos dos testes
- `test-cases/automated-bugs.json` - Apenas os bugs encontrados
- `test-cases/test-results.json` - Resultados do PowerShell
- `test-cases/bugs-found.json` - Bugs do PowerShell

## Bugs Identificados pelos Testes Automatizados

### 1. Emails Duplicados
- **Descrição:** Usuários com emails duplicados no banco
- **Exemplo:** "maria@email.com" aparece em múltiplos usuários
- **Severidade:** Alta

### 2. Tipo de Dados Incorreto
- **Descrição:** Campo `age` contém string em vez de número
- **Exemplo:** ID 7 tem age = "thirty"
- **Severidade:** Alta

### 3. Falta de Validação de Paginação
- **Descrição:** API aceita página negativa e limite excessivo
- **Exemplo:** page=-1 e limit=10000 não retornam erro
- **Severidade:** Média

### 4. Problemas de Performance
- **Descrição:** Endpoint /slow-endpoint não funciona
- **Severidade:** Baixa

## Configuração

### Python
Se você quiser usar o script completo com requests:
```bash
pip install requests
```

### PowerShell
Nenhuma configuração adicional necessária.

## Personalização

### Adicionar Novos Testes
1. Abra o arquivo de teste desejado
2. Adicione um novo método de teste
3. Chame o método em `run_all_tests()`

### Modificar URL Base
```python
tester = BasicAPITests("https://sua-api.com")
```

### Adicionar Timeouts
```python
# No método make_request, adicione:
req.timeout = 30
```

## Troubleshooting

### Erro de Execução de Scripts PowerShell
```bash
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Erro de Python não encontrado
- Instale Python do site oficial
- Adicione Python ao PATH do sistema
- Use `py` em vez de `python` no Windows

### Erro de Conexão
- Verifique se a API está online
- Teste manualmente: `curl https://cakto-qa-eval.launchify.com.br/health`

## Contribuição

Para adicionar novos testes:

1. Identifique o cenário de teste
2. Implemente o método de teste
3. Adicione validações apropriadas
4. Documente o bug encontrado
5. Atualize este README

## Próximos Passos

1. **Integração Contínua:** Adicionar os testes ao pipeline de CI/CD
2. **Cobertura:** Expandir testes para cobrir mais cenários
3. **Relatórios:** Implementar relatórios HTML mais detalhados
4. **Performance:** Adicionar testes de carga e stress
5. **Segurança:** Implementar testes de segurança básicos
