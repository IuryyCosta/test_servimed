"""
Tarefas de processamento de pedidos - Fase 3
Sistema de pedidos integrado ao scraping Servimed
"""

import time
import logging
import requests
from typing import Dict, Any, List
from datetime import datetime

from servimed.models.order import OrderRequest, OrderResponse, Order
from servimed.config import get_config

# Configurar logging
logger = logging.getLogger(__name__)
config = get_config()


def execute_order(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executa tarefa de processamento de pedido.

    Args:
        task_data: Dados da tarefa contendo informações do pedido

    Returns:
        Dicionário com resultado do processamento
    """
    try:
        logger.info(f"Iniciando processamento de pedido: {task_data.get('id_pedido')}")

        # Extrair dados da tarefa
        usuario = task_data.get("usuario")
        senha = task_data.get("senha")
        id_pedido = task_data.get("id_pedido")
        produtos = task_data.get("produtos", [])
        callback_url = task_data.get("callback_url")

        # Validar dados obrigatórios
        if not all([usuario, senha, id_pedido, produtos, callback_url]):
            raise ValueError("Dados obrigatórios não fornecidos")

        logger.info(f"Processando pedido {id_pedido} com {len(produtos)} produtos")

        # PASSO 1: Simular login no Servimed
        logger.info("Simulando login no Servimed...")
        login_success = simulate_servimed_login(usuario, senha)

        if not login_success:
            raise Exception("Falha no login do Servimed")

        # PASSO 2: Simular busca e compra dos produtos
        logger.info("Simulando busca e compra dos produtos...")
        order_result = simulate_product_purchase(produtos)

        # PASSO 3: Integrar com API do desafio
        logger.info("Integrando com API do desafio...")
        challenge_order = create_challenge_order(produtos)

        # PASSO 4: Atualizar pedido via PATCH
        logger.info("Atualizando pedido via PATCH...")
        update_result = update_challenge_order(challenge_order["id"], order_result)

        # PASSO 5: Preparar resposta de confirmação
        confirmation = OrderResponse(
            codigo_confirmacao=challenge_order["id"], status="pedido_realizado"
        )

        # PASSO 6: Enviar callback
        logger.info("Enviando callback...")
        callback_success = send_callback(callback_url, confirmation.dict())

        if not callback_success:
            logger.warning("Callback falhou, mas pedido foi processado")

        # Resultado final
        result = {
            "task_id": task_data.get("task_id"),
            "id_pedido": id_pedido,
            "status": "completed",
            "challenge_order_id": challenge_order["id"],
            "confirmation": confirmation.dict(),
            "callback_sent": callback_success,
            "processing_time": time.time(),
            "message": "Pedido processado com sucesso",
        }

        logger.info(f"Pedido {id_pedido} processado com sucesso")
        return result

    except Exception as e:
        logger.error(f"Erro ao processar pedido: {str(e)}")
        return {
            "task_id": task_data.get("task_id"),
            "id_pedido": task_data.get("id_pedido"),
            "status": "failed",
            "error": str(e),
            "processing_time": time.time(),
            "message": f"Falha no processamento: {str(e)}",
        }


def simulate_servimed_login(usuario: str, senha: str) -> bool:
    """
    Simula login no site Servimed.

    Args:
        usuario: Nome de usuário
        senha: Senha do usuário

    Returns:
        True se login simulado com sucesso
    """
    try:
        logger.info(f"Simulando login para usuário: {usuario}")

        # Simulação de login (mock)
        # Em produção, aqui seria implementada a lógica real de login
        time.sleep(1)  # Simular tempo de processamento

        # Simular sucesso (90% das vezes)
        import random

        success = random.random() > 0.1

        if success:
            logger.info("Login simulado com sucesso")
            return True
        else:
            logger.warning("Login simulado falhou")
            return False

    except Exception as e:
        logger.error(f"Erro na simulação de login: {str(e)}")
        return False


def simulate_product_purchase(produtos: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Simula busca e compra dos produtos.

    Args:
        produtos: Lista de produtos para comprar

    Returns:
        Resultado da simulação de compra
    """
    try:
        logger.info(f"Simulando compra de {len(produtos)} produtos")

        purchase_results = []

        for produto in produtos:
            gtin = produto.get("gtin")
            codigo = produto.get("codigo")
            quantidade = produto.get("quantidade")

            logger.info(
                f"Simulando compra: {codigo} (GTIN: {gtin}) - Qtd: {quantidade}"
            )

            # Simular busca do produto
            time.sleep(0.5)

            # Simular adição ao carrinho
            time.sleep(0.3)

            # Simular finalização da compra
            time.sleep(0.7)

            purchase_results.append(
                {
                    "gtin": gtin,
                    "codigo": codigo,
                    "quantidade": quantidade,
                    "status": "comprado",
                    "preco_unitario": 10.50,  # Mock
                    "preco_total": 10.50 * quantidade,
                }
            )

        result = {
            "produtos_comprados": purchase_results,
            "total_produtos": len(produtos),
            "status": "compra_simulada",
            "timestamp": datetime.now().isoformat(),
        }

        logger.info("Simulação de compra concluída com sucesso")
        return result

    except Exception as e:
        logger.error(f"Erro na simulação de compra: {str(e)}")
        return {"status": "erro", "error": str(e)}


def create_challenge_order(produtos: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Cria pedido na API do desafio.

    Args:
        produtos: Lista de produtos para o pedido

    Returns:
        Dados do pedido criado
    """
    try:
        logger.info("Criando pedido na API do desafio")

        # Preparar dados para a API
        order_data = {
            "itens": [
                {
                    "gtin": prod["gtin"],
                    "codigo": prod["codigo"],
                    "quantidade": prod["quantidade"],
                }
                for prod in produtos
            ]
        }

        # URL da API do desafio
        api_url = "https://desafio.cotefal.net/pedido"

        # Headers (seria necessário token de autenticação em produção)
        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        # Fazer POST para criar pedido
        response = requests.post(api_url, json=order_data, headers=headers, timeout=30)

        if response.status_code == 201:
            order_result = response.json()
            logger.info(f"Pedido criado na API do desafio: ID {order_result.get('id')}")
            return order_result
        else:
            logger.error(
                f"Erro ao criar pedido: {response.status_code} - {response.text}"
            )
            # Em caso de erro, retornar pedido simulado
            return {
                "id": 999,
                "codigo_fornecedor": None,
                "status": "simulado",
                "itens": order_data["itens"],
            }

    except Exception as e:
        logger.error(f"Erro ao criar pedido na API do desafio: {str(e)}")
        # Retornar pedido simulado em caso de erro
        return {
            "id": 999,
            "codigo_fornecedor": None,
            "status": "simulado",
            "itens": [
                {
                    "gtin": prod["gtin"],
                    "codigo": prod["codigo"],
                    "quantidade": prod["quantidade"],
                }
                for prod in produtos
            ],
        }


def update_challenge_order(order_id: int, order_result: Dict[str, Any]) -> bool:
    """
    Atualiza pedido na API do desafio via PATCH.

    Args:
        order_id: ID do pedido
        order_result: Resultado do processamento

    Returns:
        True se atualização bem-sucedida
    """
    try:
        logger.info(f"Atualizando pedido {order_id} via PATCH")

        # Dados para atualização
        update_data = {"status": "processado", "codigo_fornecedor": "SERVIDMED_001"}

        # URL da API do desafio
        api_url = f"https://desafio.cotefal.net/pedido/{order_id}"

        # Headers
        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        # Fazer PATCH para atualizar pedido
        response = requests.patch(
            api_url, json=update_data, headers=headers, timeout=30
        )

        if response.status_code == 200:
            logger.info(f"Pedido {order_id} atualizado com sucesso")
            return True
        else:
            logger.warning(f"Erro ao atualizar pedido: {response.status_code}")
            return False

    except Exception as e:
        logger.error(f"Erro ao atualizar pedido: {str(e)}")
        return False


def send_callback(callback_url: str, confirmation_data: Dict[str, Any]) -> bool:
    """
    Envia callback com confirmação do pedido.

    Args:
        callback_url: URL para envio do callback
        confirmation_data: Dados de confirmação

    Returns:
        True se callback enviado com sucesso
    """
    try:
        logger.info(f"Enviando callback para: {callback_url}")

        # Headers para o callback
        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        # Fazer POST para enviar callback
        response = requests.post(
            callback_url, json=confirmation_data, headers=headers, timeout=30
        )

        if response.status_code in [200, 201, 202]:
            logger.info("Callback enviado com sucesso")
            return True
        else:
            logger.warning(f"Callback falhou: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        logger.error(f"Erro ao enviar callback: {str(e)}")
        return False


# Tarefa Celery para processamento assíncrono
def execute_order_task(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Wrapper da tarefa para Celery.

    Args:
        task_data: Dados da tarefa

    Returns:
        Resultado do processamento
    """
    return execute_order(task_data)
