"""
API FastAPI para gerenciamento de tarefas de scraping e pedidos - Fases 2 e 3.

Esta API recebe requisições de scraping e pedidos, enviando-as para processamento
assíncrono via Celery workers com detecção automática do tipo de tarefa.
"""

import uuid
from datetime import datetime
from typing import Dict, Any, Union

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

from models.scraping_task import (
    ScrapingTaskRequest,
    ScrapingTaskResponse,
    ScrapingTaskStatus,
)
from models.order import OrderRequest, OrderStatus
from tasks.scraping_tasks import execute_scraping
from tasks.order_tasks import execute_order
from celery_app import celery_app


# Configuração da API
app = FastAPI(
    title="Servimed Scraping & Orders API",
    description="API para gerenciamento de tarefas de scraping e pedidos assíncrono",
    version="2.0.0",
)


@app.post("/scraping", response_model=ScrapingTaskResponse)
async def create_task(request: Union[ScrapingTaskRequest, OrderRequest]):
    """
    Cria uma nova tarefa de scraping ou pedido.

    Detecta automaticamente o tipo de tarefa baseado nos dados recebidos:
    - Se contém 'produtos': Tarefa de pedido (Fase 3)
    - Se não contém 'produtos': Tarefa de scraping (Fase 2)

    Args:
        request: Dados da tarefa (ScrapingTaskRequest ou OrderRequest)

    Returns:
        Resposta com ID da tarefa criada
    """
    try:
        # Gerar ID único para a tarefa
        task_id = str(uuid.uuid4())

        # Detectar tipo de tarefa baseado na presença de 'produtos'
        is_order_task = hasattr(request, "produtos") and hasattr(request, "id_pedido")

        if is_order_task:
            # TAREFA DE PEDIDO (Fase 3)
            order_request = OrderRequest(**request.dict())

            # Preparar dados para o Celery
            task_data = {
                "task_type": "order",
                "usuario": order_request.usuario,
                "senha": order_request.senha,
                "id_pedido": order_request.id_pedido,
                "produtos": [prod.dict() for prod in order_request.produtos],
                "callback_url": order_request.callback_url,
            }

            # Enviar tarefa de pedido para processamento assíncrono
            celery_task = execute_order.delay(task_data)
            celery_task_id = celery_task.id

            # Criar resposta para pedido
            response = OrderStatus(
                task_id=celery_task_id,
                status="pending",
                progress=0.0,
                message="Tarefa de pedido criada com sucesso",
                created_at=datetime.now(),
                started_at=None,
                completed_at=None,
                error=None,
                result=None,
            )

        else:
            # TAREFA DE SCRAPING (Fase 2)
            scraping_request = ScrapingTaskRequest(**request.dict())

            # Preparar dados para o Celery
            task_data = {
                "task_type": "scraping",
                "usuario": scraping_request.usuario,
                "senha": scraping_request.senha,
                "callback_url": scraping_request.callback_url,
            }

            # Enviar tarefa para processamento assíncrono
            celery_task = execute_scraping.delay(task_data)
            celery_task_id = celery_task.id

            # Criar resposta para scraping
            response = ScrapingTaskResponse(
                task_id=celery_task_id,
                status="pending",
                message="Tarefa de scraping criada com sucesso",
                created_at=datetime.now(),
                estimated_completion=None,
            )

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar tarefa: {str(e)}")


@app.get("/scraping/{task_id}", response_model=ScrapingTaskStatus)
async def get_task_status(task_id: str):
    """
    Consulta o status de uma tarefa de scraping.

    Args:
        task_id: ID da tarefa

    Returns:
        Status atual da tarefa
    """
    try:
        # Buscar tarefa no Celery
        task_result = celery_app.AsyncResult(task_id)

        if not task_result:
            raise HTTPException(status_code=404, detail="Tarefa não encontrada")

        # Determinar status baseado no estado do Celery
        if task_result.state == "PENDING":
            status = "pending"
            progress = 0.0
            message = "Tarefa aguardando processamento"
        elif task_result.state == "PROGRESS":
            status = "processing"
            meta = task_result.info or {}
            progress = meta.get("progress", 0.0)
            message = meta.get("message", "Processando...")
        elif task_result.state == "SUCCESS":
            status = "completed"
            progress = 1.0
            message = "Tarefa concluída com sucesso"
        elif task_result.state == "FAILURE":
            status = "failed"
            progress = 0.0
            message = f"Tarefa falhou: {task_result.info}"
        else:
            status = "unknown"
            progress = 0.0
            message = "Status desconhecido"

        # TODO: Detectar tipo de tarefa para retornar modelo correto
        # Por enquanto, retornamos ScrapingTaskStatus para compatibilidade

        # Criar resposta de status
        response = ScrapingTaskStatus(
            task_id=task_id,
            status=status,
            progress=progress,
            message=message,
            created_at=datetime.now(),
            started_at=None,
            completed_at=None,
            error=None,
            result=None,
        )

        # Adicionar informações específicas baseadas no status
        if status == "completed":
            response.result = task_result.result
        elif status == "failed":
            response.error = str(task_result.info)

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao consultar status da tarefa: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """Endpoint de verificação de saúde da API."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Servimed Scraping & Orders API",
        "phases": ["Fase 1: Scraping", "Fase 2: Filas", "Fase 3: Pedidos"],
    }


@app.get("/")
async def root():
    """Endpoint raiz da API."""
    return {
        "message": "Servimed Scraping & Orders API - Fases 2 e 3",
        "version": "2.0.0",
        "endpoints": {
            "create_task": "POST /scraping (Scraping ou Pedido)",
            "check_status": "GET /scraping/{task_id}",
            "health": "GET /health",
        },
        "supported_tasks": {
            "scraping": "Extração de produtos (Fase 2)",
            "order": "Processamento de pedidos (Fase 3)",
        },
    }
