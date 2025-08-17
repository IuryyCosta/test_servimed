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
                "callback_url": "https://desafio.cotefal.net",
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
    progress: float = Field(0.0, ge=0.0, le=1.0, description="Progresso de 0 a 1")
    message: str = Field(..., description="Mensagem descritiva do status")
    created_at: datetime = Field(
        default_factory=datetime.now, description="Data de criação"
    )
    started_at: Optional[datetime] = Field(
        None, description="Data de início do processamento"
    )
    completed_at: Optional[datetime] = Field(None, description="Data de conclusão")
    error: Optional[str] = Field(None, description="Mensagem de erro se houver")
    result: Optional[OrderResponse] = Field(
        None, description="Resultado do processamento"
    )

    class Config:
        schema_extra = {
            "example": {
                "task_id": "e6a0e772-78fc-4ed9-96ba-4b6019b3e532",
                "status": "completed",
                "progress": 1.0,
                "message": "Pedido processado com sucesso",
                "created_at": "2025-08-17T08:24:41.752164",
                "started_at": None,
                "completed_at": None,
                "error": None,
                "result": {
                    "codigo_confirmacao": "ABC987",
                    "status": "pedido_realizado",
                },
            }
        }


# Aliases para compatibilidade
OrderItem = ProductItem
OrderConfirmation = OrderResponse
