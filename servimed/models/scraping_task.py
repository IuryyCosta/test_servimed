"""
Modelos de dados para tarefas de scraping - Fase 2.

Este módulo define as estruturas de dados para:
- Tarefas de scraping
- Respostas de tarefas
- Status de processamento
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator


class ScrapingTaskRequest(BaseModel):
    """
    Modelo para requisição de tarefa de scraping.
    
    Estrutura enviada pelo cliente para criar uma nova tarefa.
    """
    
    usuario: str = Field(..., description="Usuário fornecedor para autenticação")
    senha: str = Field(..., description="Senha do usuário fornecedor")
    callback_url: str = Field(..., description="URL da API de callback")
    
    @validator("usuario")
    def validate_usuario(cls, v):
        """Valida que o usuário não esteja vazio."""
        if not v or len(v.strip()) < 1:
            raise ValueError("Usuário não pode estar vazio")
        return v.strip()
    
    @validator("senha")
    def validate_senha(cls, v):
        """Valida que a senha não esteja vazia."""
        if not v or len(v.strip()) < 1:
            raise ValueError("Senha não pode estar vazia")
        return v
    
    @validator("callback_url")
    def validate_callback_url(cls, v):
        """Valida formato básico da URL."""
        if not v or not v.startswith(("http://", "https://")):
            raise ValueError("URL de callback deve ser uma URL válida")
        return v.strip()


class ScrapingTaskResponse(BaseModel):
    """
    Modelo para resposta de criação de tarefa.
    
    Retornado após criar uma nova tarefa de scraping.
    """
    
    task_id: str = Field(..., description="ID único da tarefa criada")
    status: str = Field(..., description="Status da tarefa (pending, processing, completed, failed)")
    message: str = Field(..., description="Mensagem informativa sobre a tarefa")
    created_at: datetime = Field(..., description="Timestamp de criação da tarefa")
    estimated_completion: Optional[datetime] = Field(None, description="Estimativa de conclusão")
    
    @validator("status")
    def validate_status(cls, v):
        """Valida status da tarefa."""
        valid_statuses = ["pending", "processing", "completed", "failed"]
        if v not in valid_statuses:
            raise ValueError(f"Status deve ser um dos: {', '.join(valid_statuses)}")
        return v


class ScrapingTaskStatus(BaseModel):
    """
    Modelo para consulta de status de tarefa.
    
    Retornado ao consultar o status de uma tarefa existente.
    """
    
    task_id: str = Field(..., description="ID da tarefa")
    status: str = Field(..., description="Status atual da tarefa")
    progress: Optional[float] = Field(None, description="Progresso da tarefa (0.0 a 1.0)")
    message: str = Field(..., description="Mensagem de status atual")
    created_at: datetime = Field(..., description="Timestamp de criação")
    started_at: Optional[datetime] = Field(None, description="Timestamp de início")
    completed_at: Optional[datetime] = Field(None, description="Timestamp de conclusão")
    error: Optional[str] = Field(None, description="Mensagem de erro (se houver)")
    result: Optional[Dict[str, Any]] = Field(None, description="Resultado da tarefa (se concluída)")
    
    @validator("progress")
    def validate_progress(cls, v):
        """Valida progresso entre 0.0 e 1.0."""
        if v is not None and (v < 0.0 or v > 1.0):
            raise ValueError("Progresso deve estar entre 0.0 e 1.0")
        return v


class ScrapingResult(BaseModel):
    """
    Modelo para resultado de scraping.
    
    Estrutura dos dados extraídos e enviados para callback.
    """
    
    task_id: str = Field(..., description="ID da tarefa que gerou o resultado")
    total_products: int = Field(..., description="Total de produtos extraídos")
    products: List[Dict[str, Any]] = Field(..., description="Lista de produtos extraídos")
    extraction_time: float = Field(..., description="Tempo de extração em segundos")
    callback_sent: bool = Field(..., description="Indica se foi enviado para callback")
    callback_response: Optional[Dict[str, Any]] = Field(None, description="Resposta da API de callback")
    
    @validator("total_products")
    def validate_total_products(cls, v):
        """Valida total de produtos."""
        if v < 0:
            raise ValueError("Total de produtos não pode ser negativo")
        return v
    
    @validator("extraction_time")
    def validate_extraction_time(cls, v):
        """Valida tempo de extração."""
        if v < 0:
            raise ValueError("Tempo de extração não pode ser negativo")
        return v
