import urllib.request
import urllib.parse
import urllib.error
import json
import time
from datetime import datetime

class TestesBasicosAPI:
    def __init__(self, url_base="https://cakto-qa-eval.launchify.com.br"):
        self.url_base = url_base
        self.resultados_teste = []
        self.bugs_encontrados = []
        
    def registrar_teste(self, nome_teste, esperado, atual, status, descricao_bug=None):
        resultado = {
            "nome_teste": nome_teste,
            "timestamp": datetime.now().isoformat(),
            "esperado": esperado,
            "atual": atual,
            "status": status,
            "descricao_bug": descricao_bug
        }
        self.resultados_teste.append(resultado)
        
        if status == "BUG":
            self.bugs_encontrados.append(resultado)
            print(f"🐛 BUG: {nome_teste}")
            print(f"   Esperado: {esperado}")
            print(f"   Atual: {atual}")
            if descricao_bug:
                print(f"   Descrição: {descricao_bug}")
        else:
            print(f"✅ PASSOU: {nome_teste}")
    
    def fazer_requisicao(self, metodo, endpoint, dados=None, parametros=None):
        url = f"{self.url_base}{endpoint}"
        
        if parametros:
            string_query = urllib.parse.urlencode(parametros)
            url += f"?{string_query}"
        
        try:
            dados_json = None
            if dados and metodo.upper() in ["POST", "PUT"]:
                dados_json = json.dumps(dados).encode('utf-8')
            
            requisicao = urllib.request.Request(url, data=dados_json)
            requisicao.add_header('Content-Type', 'application/json')
            
            if metodo.upper() == "GET":
                requisicao.get_method = lambda: 'GET'
            elif metodo.upper() == "POST":
                requisicao.get_method = lambda: 'POST'
            elif metodo.upper() == "PUT":
                requisicao.get_method = lambda: 'PUT'
            elif metodo.upper() == "DELETE":
                requisicao.get_method = lambda: 'DELETE'
            
            with urllib.request.urlopen(requisicao) as resposta:
                dados_resposta = resposta.read().decode('utf-8')
                return {
                    'codigo_status': resposta.getcode(),
                    'dados': json.loads(dados_resposta) if dados_resposta else None
                }
                
        except urllib.error.HTTPError as erro:
            try:
                dados_erro = erro.read().decode('utf-8')
                return {
                    'codigo_status': erro.code,
                    'dados': json.loads(dados_erro) if dados_erro else None
                }
            except:
                return {
                    'codigo_status': erro.code,
                    'dados': None
                }
        except Exception as erro:
            return None
    
    def testar_health_check(self):
        resposta = self.fazer_requisicao("GET", "/health")
        
        if resposta and resposta['codigo_status'] == 200:
            self.registrar_teste("Health Check", "200 OK", f"{resposta['codigo_status']} OK", "PASS")
        else:
            status = resposta['codigo_status'] if resposta else "Erro de conexão"
            self.registrar_teste("Health Check", "200 OK", str(status), "BUG", 
                        "Health check deveria retornar 200 OK")
    
    def testar_estrutura_usuarios(self):
        resposta = self.fazer_requisicao("GET", "/users")
        
        if resposta and resposta['codigo_status'] == 200:
            dados = resposta['dados']
            if dados and 'data' in dados and isinstance(dados['data'], list):
                self.registrar_teste("GET Usuários - Estrutura", "Lista de usuários", "Lista retornada", "PASS")
                
                if dados['data']:
                    usuario = dados['data'][0]
                    campos_obrigatorios = ["id", "name", "email", "age", "status", "createdAt", "updatedAt"]
                    campos_ausentes = [campo for campo in campos_obrigatorios if campo not in usuario]
                    
                    if campos_ausentes:
                        self.registrar_teste("GET Usuários - Campos", "Todos os campos", f"Faltando: {campos_ausentes}", "BUG",
                                    "Usuários devem ter todos os campos obrigatórios")
                    else:
                        self.registrar_teste("GET Usuários - Campos", "Todos os campos", "Todos presentes", "PASS")
            else:
                self.registrar_teste("GET Usuários - Estrutura", "Campo 'data'", "Estrutura incorreta", "BUG",
                            "Resposta deve ter campo 'data' com lista")
        else:
            status = resposta['codigo_status'] if resposta else "Erro de conexão"
            self.registrar_teste("GET Usuários", "200 OK", str(status), "BUG", "Deveria retornar 200 OK")
    
    def testar_emails_duplicados(self):
        resposta = self.fazer_requisicao("GET", "/users")
        
        if resposta and resposta['codigo_status'] == 200:
            dados = resposta['dados']
            if dados and 'data' in dados:
                emails = [usuario['email'] for usuario in dados['data']]
                emails_unicos = set(emails)
                
                if len(emails) != len(emails_unicos):
                    duplicados = [email for email in emails if emails.count(email) > 1]
                    self.registrar_teste("Emails Duplicados", "Emails únicos", f"Duplicados: {set(duplicados)}", "BUG",
                                "Não deve haver emails duplicados")
                else:
                    self.registrar_teste("Emails Duplicados", "Emails únicos", "Todos únicos", "PASS")
    
    def testar_tipos_idade(self):
        resposta = self.fazer_requisicao("GET", "/users")
        
        if resposta and resposta['codigo_status'] == 200:
            dados = resposta['dados']
            if dados and 'data' in dados:
                idades_invalidas = []
                for usuario in dados['data']:
                    if not isinstance(usuario['age'], int):
                        idades_invalidas.append(f"ID {usuario['id']}: {usuario['age']} ({type(usuario['age']).__name__})")
                
                if idades_invalidas:
                    self.registrar_teste("Tipos de Idade", "Todos números", f"Inválidos: {idades_invalidas}", "BUG",
                                "Campo age deve ser sempre número")
                else:
                    self.registrar_teste("Tipos de Idade", "Todos números", "Todos válidos", "PASS")
    
    def testar_paginacao_pagina_negativa(self):
        resposta = self.fazer_requisicao("GET", "/users", parametros={"page": -1})
        
        if resposta:
            if resposta['codigo_status'] == 400:
                self.registrar_teste("Paginação - Página Negativa", "400 Bad Request", f"{resposta['codigo_status']}", "PASS")
            else:
                self.registrar_teste("Paginação - Página Negativa", "400 Bad Request", f"{resposta['codigo_status']}", "BUG",
                            "Página negativa deveria retornar 400")
        else:
            self.registrar_teste("Paginação - Página Negativa", "400 Bad Request", "Erro de conexão", "BUG")
    
    def testar_paginacao_limite_excessivo(self):
        resposta = self.fazer_requisicao("GET", "/users", parametros={"limit": 10000})
        
        if resposta:
            if resposta['codigo_status'] == 400:
                self.registrar_teste("Paginação - Limite Excessivo", "400 Bad Request", f"{resposta['codigo_status']}", "PASS")
            else:
                self.registrar_teste("Paginação - Limite Excessivo", "400 Bad Request", f"{resposta['codigo_status']}", "BUG",
                            "Limite excessivo deveria retornar 400")
        else:
            self.registrar_teste("Paginação - Limite Excessivo", "400 Bad Request", "Erro de conexão", "BUG")
    
    def testar_id_usuario_invalido(self):
        resposta = self.fazer_requisicao("GET", "/users/99999")
        
        if resposta:
            if resposta['codigo_status'] == 404:
                self.registrar_teste("ID Inexistente", "404 Not Found", f"{resposta['codigo_status']}", "PASS")
            else:
                self.registrar_teste("ID Inexistente", "404 Not Found", f"{resposta['codigo_status']}", "BUG",
                            "ID inexistente deveria retornar 404")
        else:
            self.registrar_teste("ID Inexistente", "404 Not Found", "Erro de conexão", "BUG")
    
    def testar_endpoint_memory_leak(self):
        resposta = self.fazer_requisicao("GET", "/memory-leak")
        
        if resposta and resposta['codigo_status'] == 200:
            self.registrar_teste("Memory Leak Endpoint", "200 OK", f"{resposta['codigo_status']} OK", "PASS")
        else:
            status = resposta['codigo_status'] if resposta else "Erro de conexão"
            self.registrar_teste("Memory Leak Endpoint", "200 OK", str(status), "BUG",
                        "Memory leak endpoint deveria retornar 200 OK")
    
    def executar_todos_testes(self):
        print("🚀 Executando testes automatizados...")
        print("=" * 50)
        
        self.testar_health_check()
        self.testar_estrutura_usuarios()
        self.testar_emails_duplicados()
        self.testar_tipos_idade()
        self.testar_paginacao_pagina_negativa()
        self.testar_paginacao_limite_excessivo()
        self.testar_id_usuario_invalido()
        self.testar_endpoint_memory_leak()
        
        print("=" * 50)
        print(f"📊 Total de testes: {len(self.resultados_teste)}")
        print(f"🐛 Bugs encontrados: {len(self.bugs_encontrados)}")
        print(f"✅ Testes passaram: {len([t for t in self.resultados_teste if t['status'] == 'PASS'])}")
        print(f"❌ Testes falharam: {len([t for t in self.resultados_teste if t['status'] == 'BUG'])}")
    
    def salvar_resultados(self):
        with open("../../test-cases/resultados-testes-automatizados.json", "w", encoding="utf-8") as arquivo:
            json.dump(self.resultados_teste, arquivo, indent=2, ensure_ascii=False)
        
        with open("../../test-cases/bugs-automatizados.json", "w", encoding="utf-8") as arquivo:
            json.dump(self.bugs_encontrados, arquivo, indent=2, ensure_ascii=False)
        
        print("💾 Resultados salvos em test-cases/")

if __name__ == "__main__":
    testador = TestesBasicosAPI()
    testador.executar_todos_testes()
    testador.salvar_resultados()
