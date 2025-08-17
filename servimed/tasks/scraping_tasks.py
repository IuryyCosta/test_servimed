"""
Tarefas Celery para processamento assíncrono de scraping - Fase 2.

Este módulo define as tarefas que serão executadas pelos workers
Celery para extrair produtos e enviar para API de callback.
"""

import time
import logging
import requests
from datetime import datetime
from typing import Dict, Any, Optional

from queues.celery_config import celery_app
from models.scraping_task import ScrapingResult
from servimed.config import get_config


logger = logging.getLogger(__name__)


def _authenticate_oauth2(username: str, password: str) -> Optional[str]:
    """Realiza autenticação OAuth2 com a API de callback."""
    try:
        config = get_config()

        # Dados para autenticação
        auth_data = {
            "grant_type": "password",
            "username": username,
            "password": password,
            "scope": "",
            "client_id": "string",
            "client_secret": "********",
        }

        # Headers
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }

        # URL de autenticação
        token_url = f"{config.api.base_url}{config.api.token_endpoint}"

        logger.info(f"Fazendo requisição para: {token_url}")

        # Requisição POST
        response = requests.post(
            url=token_url, data=auth_data, headers=headers, timeout=30
        )

        if response.status_code == 200:
            auth_response = response.json()
            access_token = auth_response.get("access_token")

            if access_token:
                logger.info("Autenticação OAuth2 realizada com sucesso")
                return access_token
            else:
                logger.error("Token de acesso não encontrado na resposta")
                return None
        else:
            logger.error(f"Erro na autenticação: Status {response.status_code}")
            logger.error(f"Resposta: {response.text}")
            return None

    except Exception as e:
        logger.error(f"Erro durante autenticação: {e}")
        return None


def _create_user_signup(username: str, password: str) -> bool:
    """Cria usuário na API de callback ."""
    try:
        config = get_config()

        # Dados para signup
        signup_data = {"username": username, "password": password}

        # Headers
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        # URL de signup
        signup_url = f"{config.api.base_url}{config.api.signup_endpoint}"

        logger.info(f"Tentando criar usuário em: {signup_url}")

        # Requisição POST
        response = requests.post(
            url=signup_url, json=signup_data, headers=headers, timeout=30
        )

        # Se usuário criado OU já existe, considerar sucesso
        if response.status_code in [200, 201] or (
            response.status_code == 400 and "Usuário já registrado" in response.text
        ):
            logger.info("Usuário disponível para autenticação")
            return True
        else:
            logger.warning(f"Signup não concluído: Status {response.status_code}")
            return False

    except Exception as e:
        logger.error(f"Erro no signup: {e}")
        return False


def _extract_products(auth_token: str) -> list:
    """Extrai produtos da API usando o token de autenticação."""
    try:
        config = get_config()

        # Headers com autorização
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {auth_token}",
        }

        # URL de produtos
        products_url = f"{config.api.base_url}{config.api.products_endpoint}"

        logger.info(f"Fazendo requisição para: {products_url}")

        # Requisição GET
        response = requests.get(url=products_url, headers=headers, timeout=30)

        if response.status_code == 200:
            products = response.json()

            if isinstance(products, list):
                logger.info(f"Produtos extraídos: {len(products)}")
                return products
            else:
                logger.error("Resposta não é uma lista de produtos")
                return []
        else:
            logger.error(f"Erro na API de produtos: Status {response.status_code}")
            logger.error(f"Resposta: {response.text}")
            return []

    except Exception as e:
        logger.error(f"Erro durante extração de produtos: {e}")
        return []


def _send_to_callback(
    callback_url: str, products: list, auth_token: str
) -> Dict[str, Any]:
    """Envia produtos extraídos para a API de callback."""
    try:
        # Headers com autorização
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {auth_token}",
        }

        # Dados para enviar
        payload = {
            "products": products,
            "extracted_at": datetime.now().isoformat(),
            "total_count": len(products),
        }

        logger.info(f"Enviando {len(products)} produtos para: {callback_url}")

        # Requisição POST
        response = requests.post(
            url=callback_url, json=payload, headers=headers, timeout=60
        )

        if response.status_code in [200, 201]:
            logger.info("Dados enviados para callback com sucesso")
            return {
                "status": "success",
                "status_code": response.status_code,
                "response": response.json() if response.content else None,
            }
        else:
            logger.warning(
                f"Resposta inesperada do callback: Status {response.status_code}"
            )
            return {
                "status": "warning",
                "status_code": response.status_code,
                "response": response.text,
            }

    except Exception as e:
        logger.error(f"Erro ao enviar para callback: {e}")
        return {"status": "error", "error": str(e)}


@celery_app.task(bind=True, name="servimed.scraping_tasks.execute_scraping")
def execute_scraping(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tarefa principal para executar scraping de produtos.

    Args:
        task_data: Dados da tarefa (usuário, senha, callback_url)

    Returns:
        Dict com resultado da execução
    """
    task_id = self.request.id
    start_time = time.time()

    try:
        logger.info(f"Iniciando tarefa de scraping: {task_id}")

        # 1. Criar usuário na API (signup)
        logger.info("Tentando criar usuário na API...")
        signup_success = _create_user_signup(
            username=task_data["usuario"], password=task_data["senha"]
        )

        if not signup_success:
            logger.warning("Signup não concluído, mas continuando com autenticação...")

        # 2. Autenticação OAuth2
        logger.info("Realizando autenticação OAuth2...")
        auth_token = _authenticate_oauth2(
            username=task_data["usuario"], password=task_data["senha"]
        )

        if not auth_token:
            raise ValueError("Falha na autenticação OAuth2")

        # 3. Extrair produtos
        logger.info("Extraindo produtos da API...")
        products = _extract_products(auth_token)

        if not products:
            raise ValueError("Nenhum produto extraído")

        # 4. Enviar para API de callback
        logger.info("Enviando dados para API de callback...")
        callback_response = _send_to_callback(
            callback_url=task_data["callback_url"],
            products=products,
            auth_token=auth_token,
        )

        # Calcular tempo total
        extraction_time = time.time() - start_time

        # 4. Criar resultado
        result = ScrapingResult(
            task_id=task_id,
            total_products=len(products),
            products=products,
            extraction_time=extraction_time,
            callback_sent=True,
            callback_response=callback_response,
        )

        logger.info(f"Tarefa concluída com sucesso: {task_id}")
        logger.info(f"Total de produtos: {len(products)}")
        logger.info(f"Tempo de execução: {extraction_time:.2f}s")

        return result.dict()

    except Exception as e:
        error_msg = f"Erro na tarefa de scraping: {str(e)}"
        logger.error(error_msg)
        raise ValueError(error_msg)


@celery_app.task(name="servimed.scraping_tasks.test_task")
def test_task() -> str:
    """Tarefa de teste para verificar funcionamento do Celery."""
    return "Tarefa de teste executada com sucesso!"
