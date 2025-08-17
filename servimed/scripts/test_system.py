"""
Script para testar o sistema completo - Fase 2.

Este script testa todo o fluxo: API -> Celery -> Workers -> Resultado.
"""

import requests
import time
import json
from datetime import datetime


def test_api_health():
    """Testa se a API está funcionando."""
    try:
        print("🔍 Testando saúde da API...")
        response = requests.get("http://localhost:8000/health")

        if response.status_code == 200:
            data = response.json()
            print("✅ API funcionando!")
            print(f"📊 Status: {data.get('status')}")
            print(f"🕐 Timestamp: {data.get('timestamp')}")
            return True
        else:
            print(f"❌ API não respondeu: Status {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Erro ao testar API: {e}")
        return False


def test_create_task():
    """Testa criação de tarefa de scraping."""
    try:
        print("\n📝 Testando criação de tarefa...")

        # Dados de teste
        task_data = {
            "usuario": "teste@servimed.com",
            "senha": "senha123",
            "callback_url": "https://httpbin.org/post",
        }

        # Criar tarefa
        response = requests.post("http://localhost:8000/scraping", json=task_data)

        if response.status_code == 200:
            data = response.json()
            print("✅ Tarefa criada com sucesso!")
            print(f"🆔 Task ID: {data.get('task_id')}")
            print(f"📊 Status: {data.get('status')}")
            print(f"💬 Mensagem: {data.get('message')}")
            return data.get("task_id")
        else:
            print(f"❌ Erro ao criar tarefa: Status {response.status_code}")
            print(f"📄 Resposta: {response.text}")
            return None

    except Exception as e:
        print(f"❌ Erro ao criar tarefa: {e}")
        return None


def test_task_status(task_id):
    """Testa consulta de status da tarefa."""
    try:
        print(f"\n📊 Testando status da tarefa {task_id}...")

        # Consultar status
        response = requests.get(f"http://localhost:8000/scraping/{task_id}")

        if response.status_code == 200:
            data = response.json()
            print("✅ Status consultado com sucesso!")
            print(f"📊 Status: {data.get('status')}")
            print(f"📈 Progresso: {data.get('progress', 0):.1%}")
            print(f"💬 Mensagem: {data.get('message')}")
            return data.get("status")
        else:
            print(f"❌ Erro ao consultar status: Status {response.status_code}")
            return None

    except Exception as e:
        print(f"❌ Erro ao consultar status: {e}")
        return None


def monitor_task_progress(task_id, max_wait=60):
    """Monitora o progresso da tarefa."""
    print(f"\n⏳ Monitorando progresso da tarefa {task_id}...")
    print("💡 Aguardando processamento...")

    start_time = time.time()

    while time.time() - start_time < max_wait:
        status = test_task_status(task_id)

        if status == "completed":
            print("🎉 TAREFA CONCLUÍDA COM SUCESSO!")
            return True
        elif status == "failed":
            print("❌ TAREFA FALHOU!")
            return False
        elif status in ["pending", "processing"]:
            print("⏳ Aguardando...")
            time.sleep(5)
        else:
            print(f"⚠️ Status desconhecido: {status}")
            time.sleep(5)

    print("⏰ Tempo limite excedido")
    return False


def main():
    """Função principal de teste."""
    print("=" * 60)
    print("🧪 TESTE DO SISTEMA COMPLETO - FASE 2")
    print("=" * 60)

    print("📋 Pré-requisitos:")
    print("   ✅ Redis rodando (localhost:6379)")
    print("   ✅ Workers Celery ativos")
    print("   ✅ API FastAPI rodando (localhost:8000)")
    print("=" * 60)

    # Teste 1: Saúde da API
    if not test_api_health():
        print("❌ Falha no teste de saúde da API")
        return

    # Teste 2: Criar tarefa
    task_id = test_create_task()
    if not task_id:
        print("❌ Falha na criação de tarefa")
        return

    # Teste 3: Monitorar progresso
    success = monitor_task_progress(task_id)

    # Resultado final
    print("\n" + "=" * 60)
    if success:
        print("🎉 SISTEMA FUNCIONANDO PERFEITAMENTE!")
        print("✅ Fase 2 validada com sucesso!")
    else:
        print("❌ SISTEMA COM PROBLEMAS")
        print("⚠️ Verifique logs e configurações")
    print("=" * 60)


if __name__ == "__main__":
    main()




