"""
Script de teste para demonstrar como chamar a fila de scraping.

Demonstra:
- Criação de tarefas na fila
- Monitoramento de progresso
- Obtenção de resultados
python test_queue.py
"""

import requests
import json
import time
import os
from typing import Dict, Any

import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from servimed.config import get_config


def get_credentials_from_env() -> Dict[str, str]:
    """Obtém credenciais das variáveis de ambiente."""

    print("Carregando configurações...")

    try:
        config = get_config()
        print("Configuração carregada com sucesso")

        return {
            "usuario": config.api.username,
            "senha": config.api.password,
            "callback_url": config.api.base_url,
        }

    except Exception as e:
        print(f"Erro ao carregar configuração: {e}")
        print("Usando variáveis de ambiente diretas...")

        # Fallback para variáveis de ambiente
        username = os.getenv("SERVIMED_USERNAME", "juliano@farmaprevonline.com.br")
        password = os.getenv("SERVIMED_PASSWORD", "a007299A")
        callback_url = os.getenv(
            "SERVIMED_CALLBACK_URL", "https://desafio.cotefacil.net"
        )

        return {"usuario": username, "senha": password, "callback_url": callback_url}


def test_scraping_queue() -> None:
    """Testa a fila de scraping criando uma tarefa e monitorando o progresso."""

    print("TESTANDO FILA DE SCRAPING")
    print("=" * 50)

    task_data = get_credentials_from_env()

    print(f"Enviando tarefa para a fila...")
    print(f"Usuario: {task_data['usuario']}")
    print(f"Callback URL: {task_data['callback_url']}")
    print()

    try:
        # Criar tarefa na fila
        response = requests.post(
            f"http://localhost:8000/scraping",
            json=task_data,
            headers={"Content-Type": "application/json"},
        )

        if response.status_code != 200:
            print(f"Erro ao criar tarefa: {response.status_code}")
            print(f"Resposta: {response.text}")
            return

        # Extrair informações da resposta
        task_info = response.json()
        task_id = task_info["task_id"]

        print(f"Tarefa criada com sucesso!")
        print(f"Task ID: {task_id}")
        print(f"Status: {task_info['status']}")
        print()

        # Monitorar progresso da tarefa
        print("Monitorando progresso da tarefa...")
        print("-" * 30)

        max_attempts = 30
        attempt = 0

        while attempt < max_attempts:
            attempt += 1

            # Verificar status da tarefa
            status_response = requests.get(f"http://localhost:8000/scraping/{task_id}")

            if status_response.status_code != 200:
                print(f"Erro ao verificar status: {status_response.status_code}")
                continue

            task_status = status_response.json()
            current_status = task_status["status"]

            print(f"Tentativa {attempt:2d}: Status = {current_status}")

            # Tarefa concluída
            if current_status == "completed":
                print()
                print("TAREFA CONCLUÍDA COM SUCESSO!")
                print("=" * 50)

                # Mostrar resultados
                result = task_status.get("result", {})
                total_products = result.get("total_products", 0)
                extraction_time = result.get("extraction_time", 0)
                callback_sent = result.get("callback_sent", False)

                print(f"RESULTADOS:")
                print(f"Total de produtos: {total_products}")
                print(f"Tempo de extração: {extraction_time:.2f} segundos")
                print(f"Callback enviado: {'Sim' if callback_sent else 'Não'}")

                # Mostrar alguns produtos de exemplo
                products = result.get("products", [])
                if products:
                    print(f"\nExemplos de produtos:")
                    for i, product in enumerate(products[:3]):
                        print(f"{i+1}. {product['descricao'][:50]}...")
                        print(f"   GTIN: {product['gtin']}")
                        print(f"   Preço: R$ {product['preco_fabrica']:.2f}")
                        print(f"   Estoque: {product['estoque']}")
                        print()

                break

            # Tarefa falhou
            elif current_status == "failed":
                print()
                print("TAREFA FALHOU!")
                print("=" * 50)
                error = task_status.get("error", "Erro desconhecido")
                print(f"Erro: {error}")
                break

            # Aguardar antes da próxima verificação
            time.sleep(10)

        else:
            print()
            print("Tempo limite excedido. A tarefa ainda está em processamento.")
            print(f"Verifique manualmente: http://localhost:8000/scraping/{task_id}")

    except requests.exceptions.ConnectionError:
        print(
            "Erro de conexão: Verifique se a API está rodando em http://localhost:8000"
        )
    except Exception as e:
        print(f"Erro inesperado: {e}")


def show_usage_examples() -> None:
    """Mostra exemplos de como usar a fila."""

    print("\nEXEMPLOS DE USO DA FILA")
    print("=" * 50)

    print("1. Via Python (requests):")
    print(
        """
import requests

response = requests.post(
    "http://localhost:8000/scraping",
    json={
        "usuario": "seu_usuario@email.com",
        "senha": "sua_senha",
        "callback_url": "https://sua-api.com"
    }
)

task_id = response.json()["task_id"]
print(f"Tarefa criada: {task_id}")
"""
    )

    print("2. Via curl:")
    print(
        """
curl -X POST "http://localhost:8000/scraping" \\
  -H "Content-Type: application/json" \\
  -d '{
    "usuario": "seu_usuario@email.com",
    "senha": "sua_senha",
    "callback_url": "https://sua-api.com"
  }'
"""
    )

    print("3. Via navegador:")
    print("   Acesse: http://localhost:8000/docs")
    print("   Use o endpoint POST /scraping")


if __name__ == "__main__":
    try:
        test_scraping_queue()
        show_usage_examples()

    except KeyboardInterrupt:
        print("\nTeste interrompido pelo usuário.")
    except Exception as e:
        print(f"\nErro durante o teste: {e}")
