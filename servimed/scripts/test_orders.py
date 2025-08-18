"""
Script de teste para validar funcionalidades de pedidos - Fase 3
Sistema de pedidos integrado ao scraping Servimed
"""

import requests
import json
import time
from datetime import datetime

# Configurações
API_BASE_URL = "http://localhost:8000"
CALLBACK_URL = "https://httpbin.org/post"  # Serviço de teste para callback


def test_order_creation():
    """
    Testa criação de tarefa de pedido via API
    """
    print(" TESTE 1: Criação de Tarefa de Pedido")
    print("=" * 50)

    # Dados de teste para pedido
    order_data = {
        "usuario": "teste@servimed.com",
        "senha": "senha123",
        "id_pedido": "PEDIDO_001",
        "produtos": [
            {"gtin": "7899095203136", "codigo": "446231", "quantidade": 2},
            {"gtin": "7898636193493", "codigo": "444212", "quantidade": 1},
        ],
        "callback_url": CALLBACK_URL,
    }

    try:
        print(f"📤 Enviando pedido para: {API_BASE_URL}/scraping")
        print(f"📋 Dados do pedido: {json.dumps(order_data, indent=2)}")

        # Fazer POST para criar tarefa de pedido
        response = requests.post(
            f"{API_BASE_URL}/scraping",
            json=order_data,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )

        print(f" Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(" Tarefa de pedido criada com sucesso!")
            print(f" Task ID: {result.get('task_id')}")
            print(f" Status: {result.get('status')}")
            print(f" Mensagem: {result.get('message')}")

            return result.get("task_id")
        else:
            print(f" Erro ao criar tarefa: {response.status_code}")
            print(f" Resposta: {response.text}")
            return None

    except Exception as e:
        print(f" Erro na requisição: {str(e)}")
        return None


def test_task_status(task_id):
    """
    Testa consulta de status da tarefa
    """
    print("\n🧪 TESTE 2: Consulta de Status da Tarefa")
    print("=" * 50)

    if not task_id:
        print("❌ Task ID não disponível para consulta")
        return

    try:
        print(f"📤 Consultando status da tarefa: {task_id}")

        # Fazer GET para consultar status
        response = requests.get(f"{API_BASE_URL}/scraping/{task_id}", timeout=30)

        print(f"📊 Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✅ Status consultado com sucesso!")
            print(f"🆔 Task ID: {result.get('task_id')}")
            print(f"📝 Status: {result.get('status')}")
            print(f"📊 Progresso: {result.get('progress', 0)}%")
            print(f"💬 Mensagem: {result.get('message')}")

            return result
        else:
            print(f"❌ Erro ao consultar status: {response.status_code}")
            print(f"📄 Resposta: {response.text}")
            return None

    except Exception as e:
        print(f"❌ Erro na consulta: {str(e)}")
        return None


def test_api_health():
    """
    Testa endpoint de saúde da API
    """
    print("\n🧪 TESTE 3: Verificação de Saúde da API")
    print("=" * 50)

    try:
        print(f"📤 Consultando: {API_BASE_URL}/health")

        response = requests.get(f"{API_BASE_URL}/health", timeout=10)

        print(f"📊 Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✅ API funcionando perfeitamente!")
            print(f"📊 Status: {result.get('status')}")
            print(f"🕐 Timestamp: {result.get('timestamp')}")
            print(f"🔧 Serviço: {result.get('service')}")
            print(f"📋 Fases: {result.get('phases', [])}")
        else:
            print(f"❌ API com problemas: {response.status_code}")

    except Exception as e:
        print(f"❌ Erro ao verificar API: {str(e)}")


def test_api_root():
    """
    Testa endpoint raiz da API
    """
    print("\n🧪 TESTE 4: Endpoint Raiz da API")
    print("=" * 50)

    try:
        print(f"📤 Consultando: {API_BASE_URL}/")

        response = requests.get(f"{API_BASE_URL}/", timeout=10)

        print(f"📊 Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✅ Endpoint raiz funcionando!")
            print(f"📝 Mensagem: {result.get('message')}")
            print(f"🔢 Versão: {result.get('version')}")
            print(f"🔗 Endpoints: {result.get('endpoints', {})}")
            print(f"✅ Tarefas Suportadas: {result.get('supported_tasks', {})}")
        else:
            print(f"❌ Endpoint raiz com problemas: {response.status_code}")

    except Exception as e:
        print(f"❌ Erro ao verificar endpoint raiz: {str(e)}")


def test_order_processing_simulation():
    """
    Simula o processamento de pedido para validação
    """
    print("\n🧪 TESTE 5: Simulação de Processamento de Pedido")
    print("=" * 50)

    print("🔄 Simulando fluxo completo de pedido...")

    # Simular tempo de processamento
    print("⏳ Aguardando processamento...")
    time.sleep(3)

    print("✅ Simulação concluída!")
    print("📋 Fluxo simulado:")
    print("   1. Login no Servimed (simulado)")
    print("   2. Busca de produtos (simulado)")
    print("   3. Adição ao carrinho (simulado)")
    print("   4. Finalização da compra (simulado)")
    print("   5. Integração com API do desafio")
    print("   6. Atualização via PATCH")
    print("   7. Envio de callback")


def run_complete_test():
    """
    Executa todos os testes em sequência
    """
    print("🚀 INICIANDO TESTES COMPLETOS DA FASE 3")
    print("=" * 60)
    print(f"🕐 Início: {datetime.now().strftime('%H:%M:%S')}")
    print(f"🌐 API Base: {API_BASE_URL}")
    print(f"📞 Callback: {CALLBACK_URL}")
    print("=" * 60)

    # Teste 1: Criação de pedido
    task_id = test_order_creation()

    # Teste 2: Consulta de status
    if task_id:
        test_task_status(task_id)

        # Aguardar um pouco para processamento
        print("\n⏳ Aguardando 5 segundos para processamento...")
        time.sleep(5)

        # Consultar status novamente
        test_task_status(task_id)

    # Teste 3: Saúde da API
    test_api_health()

    # Teste 4: Endpoint raiz
    test_api_root()

    # Teste 5: Simulação de processamento
    test_order_processing_simulation()

    print("\n" + "=" * 60)
    print("🏁 TESTES COMPLETOS DA FASE 3 FINALIZADOS!")
    print(f"🕐 Fim: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 60)


if __name__ == "__main__":
    try:
        run_complete_test()
    except KeyboardInterrupt:
        print("\n\n⏹️ Teste interrompido pelo usuário")
    except Exception as e:
        print(f"\n\n❌ Erro durante os testes: {str(e)}")
        print("💡 Verifique se a API está rodando e os workers estão ativos")
