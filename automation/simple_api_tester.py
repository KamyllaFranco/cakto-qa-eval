import urllib.request
import urllib.parse
import urllib.error
import json
import time
from datetime import datetime

class SimpleAPITester:
    def __init__(self, base_url="https://cakto-qa-eval.launchify.com.br"):
        self.base_url = base_url
        self.bugs_found = []
        self.test_results = []
        
    def log_test(self, test_name, expected, actual, status, bug_description=None):
        result = {
            "test_name": test_name,
            "timestamp": datetime.now().isoformat(),
            "expected": expected,
            "actual": actual,
            "status": status,
            "bug_description": bug_description
        }
        self.test_results.append(result)
        
        if status == "BUG":
            self.bugs_found.append(result)
            print(f"🐛 BUG ENCONTRADO: {test_name}")
            print(f"   Esperado: {expected}")
            print(f"   Atual: {actual}")
            if bug_description:
                print(f"   Descrição: {bug_description}")
            print()
        else:
            print(f"✅ {test_name} - {status}")
    
    def make_request(self, method, endpoint, data=None, params=None):
        url = f"{self.base_url}{endpoint}"
        
        if params:
            query_string = urllib.parse.urlencode(params)
            url += f"?{query_string}"
        
        try:
            json_data = None
            if data and method.upper() in ["POST", "PUT"]:
                json_data = json.dumps(data).encode('utf-8')
            
            req = urllib.request.Request(url, data=json_data)
            req.add_header('Content-Type', 'application/json')
            
            if method.upper() == "GET":
                req.get_method = lambda: 'GET'
            elif method.upper() == "POST":
                req.get_method = lambda: 'POST'
            elif method.upper() == "PUT":
                req.get_method = lambda: 'PUT'
            elif method.upper() == "DELETE":
                req.get_method = lambda: 'DELETE'
            
            with urllib.request.urlopen(req) as response:
                response_data = response.read().decode('utf-8')
                return {
                    'status_code': response.getcode(),
                    'data': json.loads(response_data) if response_data else None
                }
                
        except urllib.error.HTTPError as e:
            try:
                error_data = e.read().decode('utf-8')
                return {
                    'status_code': e.code,
                    'data': json.loads(error_data) if error_data else None
                }
            except:
                return {
                    'status_code': e.code,
                    'data': None
                }
        except Exception as e:
            print(f"Erro na requisição {method} {endpoint}: {e}")
            return None
    
    def test_health_endpoint(self):
        print("🔍 Testando endpoint /health...")
        response = self.make_request("GET", "/health")
        
        if response:
            if response['status_code'] == 200:
                self.log_test("Health Check", "200 OK", f"{response['status_code']} OK", "PASS")
            else:
                self.log_test("Health Check", "200 OK", f"{response['status_code']}", "BUG", 
                            "Health check deveria retornar 200 OK")
        else:
            self.log_test("Health Check", "200 OK", "Erro na requisição", "BUG", "Falha na conexão")
    
    def test_root_endpoint(self):
        print("🔍 Testando endpoint raiz /...")
        response = self.make_request("GET", "/")
        
        if response:
            if response['status_code'] == 200:
                self.log_test("Root Endpoint", "200 OK", f"{response['status_code']} OK", "PASS")
            else:
                self.log_test("Root Endpoint", "200 OK", f"{response['status_code']}", "BUG",
                            "Endpoint raiz deveria retornar 200 OK")
        else:
            self.log_test("Root Endpoint", "200 OK", "Erro na requisição", "BUG", "Falha na conexão")
    
    def test_get_users(self):
        print("🔍 Testando GET /users...")
        response = self.make_request("GET", "/users")
        
        if response:
            if response['status_code'] == 200:
                data = response['data']
                if data and 'data' in data and isinstance(data['data'], list):
                    self.log_test("GET Users - Estrutura", "Lista de usuários", "Lista de usuários retornada", "PASS")
                    
                    if data['data']:
                        user = data['data'][0]
                        required_fields = ["id", "name", "email", "age", "status", "createdAt", "updatedAt"]
                        missing_fields = [field for field in required_fields if field not in user]
                        
                        if missing_fields:
                            self.log_test("GET Users - Campos obrigatórios", "Todos os campos presentes", 
                                        f"Campos ausentes: {missing_fields}", "BUG",
                                        "Usuários devem ter todos os campos obrigatórios")
                        else:
                            self.log_test("GET Users - Campos obrigatórios", "Todos os campos presentes", 
                                        "Todos os campos presentes", "PASS")
                else:
                    self.log_test("GET Users - Estrutura", "Campo 'data' com lista", 
                                "Estrutura inesperada", "BUG",
                                "Resposta deve ter campo 'data' com lista de usuários")
            else:
                self.log_test("GET Users - Status", "200 OK", f"{response['status_code']}", "BUG",
                            "Listagem de usuários deveria retornar 200 OK")
        else:
            self.log_test("GET Users", "200 OK", "Erro na requisição", "BUG", "Falha na conexão")
    
    def test_create_user_valid(self):
        print("🔍 Testando POST /users com dados válidos...")
        valid_user = {
            "name": "Teste Usuário",
            "email": "teste@email.com",
            "age": 25,
            "status": "active"
        }
        
        response = self.make_request("POST", "/users", data=valid_user)
        
        if response:
            if response['status_code'] == 201:
                data = response['data']
                if data and 'id' in data:
                    self.log_test("POST User - Status", "201 Created", f"{response['status_code']} Created", "PASS")
                    self.log_test("POST User - ID", "ID retornado", f"ID: {data['id']}", "PASS")
                    return data['id']
                else:
                    self.log_test("POST User - ID", "ID retornado", "ID não retornado", "BUG",
                                "Usuário criado deve retornar ID")
            else:
                self.log_test("POST User - Status", "201 Created", f"{response['status_code']}", "BUG",
                            "Criação de usuário válido deveria retornar 201 Created")
        else:
            self.log_test("POST User", "201 Created", "Erro na requisição", "BUG", "Falha na conexão")
        
        return None
    
    def test_create_user_invalid_email(self):
        print("🔍 Testando POST /users com email inválido...")
        invalid_user = {
            "name": "Teste Usuário",
            "email": "email-invalido",
            "age": 25,
            "status": "active"
        }
        
        response = self.make_request("POST", "/users", data=invalid_user)
        
        if response:
            if response['status_code'] == 400:
                self.log_test("POST User - Email inválido", "400 Bad Request", f"{response['status_code']} Bad Request", "PASS")
            else:
                self.log_test("POST User - Email inválido", "400 Bad Request", f"{response['status_code']}", "BUG",
                            "Email inválido deveria retornar 400 Bad Request")
        else:
            self.log_test("POST User - Email inválido", "400 Bad Request", "Erro na requisição", "BUG", "Falha na conexão")
    
    def test_create_user_empty_name(self):
        print("🔍 Testando POST /users com nome vazio...")
        invalid_user = {
            "name": "",
            "email": "teste@email.com",
            "age": 25,
            "status": "active"
        }
        
        response = self.make_request("POST", "/users", data=invalid_user)
        
        if response:
            if response['status_code'] == 400:
                self.log_test("POST User - Nome vazio", "400 Bad Request", f"{response['status_code']} Bad Request", "PASS")
            else:
                self.log_test("POST User - Nome vazio", "400 Bad Request", f"{response['status_code']}", "BUG",
                            "Nome vazio deveria retornar 400 Bad Request")
        else:
            self.log_test("POST User - Nome vazio", "400 Bad Request", "Erro na requisição", "BUG", "Falha na conexão")
    
    def test_create_user_negative_age(self):
        print("🔍 Testando POST /users com idade negativa...")
        invalid_user = {
            "name": "Teste Usuário",
            "email": "teste@email.com",
            "age": -5,
            "status": "active"
        }
        
        response = self.make_request("POST", "/users", data=invalid_user)
        
        if response:
            if response['status_code'] == 400:
                self.log_test("POST User - Idade negativa", "400 Bad Request", f"{response['status_code']} Bad Request", "PASS")
            else:
                self.log_test("POST User - Idade negativa", "400 Bad Request", f"{response['status_code']}", "BUG",
                            "Idade negativa deveria retornar 400 Bad Request")
        else:
            self.log_test("POST User - Idade negativa", "400 Bad Request", "Erro na requisição", "BUG", "Falha na conexão")
    
    def test_get_user_by_id(self, user_id):
        print(f"🔍 Testando GET /users/{user_id}...")
        response = self.make_request("GET", f"/users/{user_id}")
        
        if response:
            if response['status_code'] == 200:
                data = response['data']
                if data and 'id' in data and data['id'] == user_id:
                    self.log_test("GET User by ID", "200 OK com dados do usuário", f"{response['status_code']} OK", "PASS")
                else:
                    self.log_test("GET User by ID", "Dados do usuário correto", "Dados incorretos", "BUG",
                                "Dados do usuário retornado não correspondem ao ID solicitado")
            else:
                self.log_test("GET User by ID", "200 OK", f"{response['status_code']}", "BUG",
                            "Busca de usuário válido deveria retornar 200 OK")
        else:
            self.log_test("GET User by ID", "200 OK", "Erro na requisição", "BUG", "Falha na conexão")
    
    def test_get_user_invalid_id(self):
        print("🔍 Testando GET /users/99999 (ID inexistente)...")
        response = self.make_request("GET", "/users/99999")
        
        if response:
            if response['status_code'] == 404:
                self.log_test("GET User - ID inexistente", "404 Not Found", f"{response['status_code']} Not Found", "PASS")
            else:
                self.log_test("GET User - ID inexistente", "404 Not Found", f"{response['status_code']}", "BUG",
                            "ID inexistente deveria retornar 404 Not Found")
        else:
            self.log_test("GET User - ID inexistente", "404 Not Found", "Erro na requisição", "BUG", "Falha na conexão")
    
    def test_update_user(self, user_id):
        print(f"🔍 Testando PUT /users/{user_id}...")
        updated_user = {
            "name": "Usuário Atualizado",
            "email": "atualizado@email.com",
            "age": 30,
            "status": "inactive"
        }
        
        response = self.make_request("PUT", f"/users/{user_id}", data=updated_user)
        
        if response:
            if response['status_code'] == 200:
                data = response['data']
                if data and 'updatedAt' in data:
                    self.log_test("PUT User - Status", "200 OK", f"{response['status_code']} OK", "PASS")
                    self.log_test("PUT User - updatedAt", "Campo updatedAt atualizado", "Campo updatedAt presente", "PASS")
                else:
                    self.log_test("PUT User - updatedAt", "Campo updatedAt atualizado", "Campo updatedAt ausente", "BUG",
                                "Campo updatedAt deve ser atualizado após modificação")
            else:
                self.log_test("PUT User - Status", "200 OK", f"{response['status_code']}", "BUG",
                            "Atualização de usuário deveria retornar 200 OK")
        else:
            self.log_test("PUT User", "200 OK", "Erro na requisição", "BUG", "Falha na conexão")
    
    def test_delete_user(self, user_id):
        print(f"🔍 Testando DELETE /users/{user_id}...")
        response = self.make_request("DELETE", f"/users/{user_id}")
        
        if response:
            if response['status_code'] == 200:
                self.log_test("DELETE User - Status", "200 OK", f"{response['status_code']} OK", "PASS")
                
                get_response = self.make_request("GET", f"/users/{user_id}")
                if get_response and get_response['status_code'] == 404:
                    self.log_test("DELETE User - Verificação", "Usuário deletado", "Usuário não encontrado", "PASS")
                else:
                    self.log_test("DELETE User - Verificação", "Usuário deletado", "Usuário ainda existe", "BUG",
                                "Usuário deveria ser deletado permanentemente")
            else:
                self.log_test("DELETE User - Status", "200 OK", f"{response['status_code']}", "BUG",
                            "Exclusão de usuário deveria retornar 200 OK")
        else:
            self.log_test("DELETE User", "200 OK", "Erro na requisição", "BUG", "Falha na conexão")
    
    def test_pagination(self):
        print("🔍 Testando paginação...")
        
        response = self.make_request("GET", "/users", params={"page": 1, "limit": 5})
        if response and response['status_code'] == 200:
            self.log_test("Pagination - Página 1", "200 OK", f"{response['status_code']} OK", "PASS")
        
        response = self.make_request("GET", "/users", params={"page": -1, "limit": 5})
        if response:
            if response['status_code'] == 400:
                self.log_test("Pagination - Página negativa", "400 Bad Request", f"{response['status_code']} Bad Request", "PASS")
            else:
                self.log_test("Pagination - Página negativa", "400 Bad Request", f"{response['status_code']}", "BUG",
                            "Página negativa deveria retornar 400 Bad Request")
        
        response = self.make_request("GET", "/users", params={"page": 1, "limit": 10000})
        if response:
            if response['status_code'] == 400:
                self.log_test("Pagination - Limite excessivo", "400 Bad Request", f"{response['status_code']} Bad Request", "PASS")
            else:
                self.log_test("Pagination - Limite excessivo", "400 Bad Request", f"{response['status_code']}", "BUG",
                            "Limite excessivo deveria retornar 400 Bad Request")
    
    def test_performance_endpoints(self):
        print("🔍 Testando endpoints de performance...")
        
        start_time = time.time()
        response = self.make_request("GET", "/slow-endpoint")
        end_time = time.time()
        
        if response:
            response_time = end_time - start_time
            if response_time > 5:
                self.log_test("Performance - Slow Endpoint", "Resposta lenta", f"{response_time:.2f}s", "PASS")
            else:
                self.log_test("Performance - Slow Endpoint", "Resposta lenta", f"{response_time:.2f}s", "BUG",
                            "Endpoint deveria ser lento (>5s)")
        
        response = self.make_request("GET", "/memory-leak")
        if response:
            if response['status_code'] == 200:
                self.log_test("Performance - Memory Leak", "200 OK", f"{response['status_code']} OK", "PASS")
            else:
                self.log_test("Performance - Memory Leak", "200 OK", f"{response['status_code']}", "BUG",
                            "Memory leak endpoint deveria retornar 200 OK")
    
    def run_all_tests(self):
        print("🚀 Iniciando testes da API de usuários...")
        print("=" * 50)
        
        self.test_health_endpoint()
        self.test_root_endpoint()
        self.test_get_users()
        
        user_id = self.test_create_user_valid()
        self.test_create_user_invalid_email()
        self.test_create_user_empty_name()
        self.test_create_user_negative_age()
        
        if user_id:
            self.test_get_user_by_id(user_id)
        self.test_get_user_invalid_id()
        
        if user_id:
            self.test_update_user(user_id)
        
        self.test_pagination()
        self.test_performance_endpoints()
        
        if user_id:
            self.test_delete_user(user_id)
        
        print("=" * 50)
        print(f"✅ Testes concluídos!")
        print(f"📊 Total de testes: {len(self.test_results)}")
        print(f"🐛 Bugs encontrados: {len(self.bugs_found)}")
        print(f"✅ Testes passaram: {len([t for t in self.test_results if t['status'] == 'PASS'])}")
        print(f"❌ Testes falharam: {len([t for t in self.test_results if t['status'] == 'BUG'])}")
    
    def save_results(self):
        with open("../test-cases/test-results.json", "w", encoding="utf-8") as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        
        with open("../test-cases/bugs-found.json", "w", encoding="utf-8") as f:
            json.dump(self.bugs_found, f, indent=2, ensure_ascii=False)
        
        print("💾 Resultados salvos em test-cases/")

if __name__ == "__main__":
    tester = SimpleAPITester()
    tester.run_all_tests()
    tester.save_results()
