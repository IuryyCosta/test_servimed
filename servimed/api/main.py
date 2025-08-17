"""
API FastAPI para gerenciamento de tarefas de scraping - Fase 2.

Esta API recebe requisições de scraping e as envia para processamento
assíncrono via Celery workers.
"""

import uuid
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

from models.scraping_task import (
    ScrapingTaskRequest,
    ScrapingTaskResponse,
    ScrapingTaskStatus,
)
from tasks.scraping_tasks import execute_scraping
from queues.celery_config import celery_app


# Configuração da API
app = FastAPI(
    title="Servimed Scraping API",
    description="API para gerenciamento de tarefas de scraping assíncrono",
    version="1.0.0",
)


@app.post("/scraping", response_model=ScrapingTaskResponse)
async def create_scraping_task(request: ScrapingTaskRequest):
    """
    Cria uma nova tarefa de scraping.

    Args:
        request: Dados da tarefa (usuário, senha, callback_url)

    Returns:
        Resposta com ID da tarefa criada
    """
    try:
        # Gerar ID único para a tarefa
        task_id = str(uuid.uuid4())

        # Preparar dados para o Celery
        task_data = {
            "usuario": request.usuario,
            "senha": request.senha,
            "callback_url": request.callback_url,
        }

        # Enviar tarefa para processamento assíncrono
        celery_task = execute_scraping.delay(task_data)

        # Usar o ID do Celery para rastreamento
        celery_task_id = celery_task.id

        # Criar resposta
        response = ScrapingTaskResponse(
            task_id=celery_task_id,
            status="pending",
            message="Tarefa de scraping criada com sucesso",
            created_at=datetime.now(),
            estimated_completion=None,
        )

        return response

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao criar tarefa de scraping: {str(e)}"
        )


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
        "service": "Servimed Scraping API",
    }


@app.get("/")
async def root():
    """Endpoint raiz da API."""
    return {
        "message": "Servimed Scraping API - Fase 2",
        "version": "1.0.0",
        "endpoints": {
            "create_task": "POST /scraping",
            "check_status": "GET /scraping/{task_id}",
            "health": "GET /health",
        },
    }
