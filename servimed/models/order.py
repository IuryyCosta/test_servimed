"""
Modelos de dados para pedidos - Fase 3
Sistema de pedidos integrado ao scraping Servimed
"""

from typing import List, Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime


class ProductItem(BaseModel):
    """Item individual de produto em um pedido"""

    gtin: str = Field(..., description="Código GTIN/EAN do produto")
    codigo: str = Field(..., description="Código interno do produto")
    quantidade: int = Field(..., ge=1, description="Quantidade solicitada")

    @validator("quantidade")
    def validate_quantidade(cls, v):
        if v < 1:
            raise ValueError("Quantidade deve ser maior que zero")
        return v

    class Config:
        schema_extra = {
            "example": {"gtin": "7899095203136", "codigo": "446231", "quantidade": 1}
        }


class OrderRequest(BaseModel):
    """Requisição para criar um pedido - Fase 3"""

    usuario: str = Field(..., description="Usuário para login no Servimed")
    senha: str = Field(..., description="Senha para login no Servimed")
    id_pedido: str = Field(..., description="Identificador único do pedido")
    produtos: List[ProductItem] = Field(
        ..., min_items=1, description="Lista de produtos do pedido"
    )
    callback_url: str = Field(..., description="URL para callback da confirmação")

    @validator("produtos")
    def validate_produtos(cls, v):
        if not v:
            raise ValueError("Pedido deve ter pelo menos um produto")
        return v

    class Config:
        schema_extra = {
            "example": {
                "usuario": "fornecedor_user",
                "senha": "fornecedor_pass",
                "id_pedido": "1234",
                "produtos": [
                    {"gtin": "7899095203136", "codigo": "446231", "quantidade": 1}
                ],
                "callback_url": "https://desafio.cotefacil.net",
            }
        }


class OrderResponse(BaseModel):
    """Resposta de confirmação do pedido"""

    codigo_confirmacao: str = Field(..., description="Código de confirmação do pedido")
    status: str = Field(..., description="Status do pedido")

    class Config:
        schema_extra = {
            "example": {"codigo_confirmacao": "ABC987", "status": "pedido_realizado"}
        }


class Order(BaseModel):
    """Estrutura completa do pedido conforme API do desafio"""

    id: int = Field(..., description="ID único do pedido")
    codigo_fornecedor: Optional[str] = Field(None, description="Código do fornecedor")
    status: Optional[str] = Field(None, description="Status atual do pedido")
    itens: List[ProductItem] = Field(..., description="Itens do pedido")

    class Config:
        schema_extra = {
            "example": {
                "id": 64,
                "codigo_fornecedor": None,
                "status": None,
                "itens": [
                    {"gtin": "7899095203136", "codigo": "446231", "quantidade": 1}
                ],
            }
        }


class OrderStatus(BaseModel):
    """Status de processamento do pedido"""

    task_id: str = Field(..., description="ID da tarefa de processamento")
    status: str = Field(
        ..., description="Status atual: pending, processing, completed, failed"
    )
    progress: Optional[float] = Field(None, description="Progresso da tarefa (0.0 a 1.0)")
    message: str = Field(..., description="Mensagem de status atual")
    created_at: datetime = Field(..., description="Timestamp de criação")
    started_at: Optional[datetime] = Field(None, description="Timestamp de início")
    completed_at: Optional[datetime] = Field(None, description="Timestamp de conclusão")
    error: Optional[str] = Field(None, description="Mensagem de erro (se houver)")
    result: Optional[dict] = Field(None, description="Resultado da tarefa (se concluída)")

    @validator("progress")
    def validate_progress(cls, v):
        """Valida progresso entre 0.0 e 1.0."""
        if v is not None and (v < 0.0 or v > 1.0):
            raise ValueError("Progresso deve estar entre 0.0 e 1.0")
        return v

    class Config:
        schema_extra = {
            "example": {
                "task_id": "uuid-1234",
                "status": "pending",
                "progress": 0.0,
                "message": "Tarefa criada com sucesso",
                "created_at": "2025-08-17T10:00:00",
                "started_at": None,
                "completed_at": None,
                "error": None,
                "result": None,
            }
        }
