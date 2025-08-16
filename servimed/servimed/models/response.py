"""
Modelos de dados para respostas da API.

Este módulo define estruturas para:
- Respostas genéricas da API
- Tratamento de erros
- Respostas de sucesso
"""

from typing import Optional, Any, Dict
from pydantic import BaseModel, Field


class APIResponse(BaseModel):
    """

    """

    success: bool = Field(..., description="Indica se a operação foi bem-sucedida")
    data: Optional[Any] = Field(None, description="Dados da resposta (se sucesso)")
    message: Optional[str] = Field(None, description="Mensagem informativa")
    timestamp: Optional[str] = Field(None, description="Timestamp da resposta")

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return {
            "success": self.success,
            "data": self.data,
            "message": self.message,
            "timestamp": self.timestamp,
        }


class ErrorResponse(BaseModel):
    """
    Resposta de erro da API.

    Estrutura para erros e falhas.
    """

    success: bool = Field(False, description="Sempre false para erros")
    error: str = Field(..., description="Mensagem de erro")
    error_code: Optional[str] = Field(None, description="Código do erro")
    details: Optional[Dict[str, Any]] = Field(
        None, description="Detalhes adicionais do erro"
    )

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return {
            "success": self.success,
            "error": self.error,
            "error_code": self.error_code,
            "details": self.details,
        }


class SuccessResponse(BaseModel):
    """
    Resposta de sucesso da API.

    Estrutura para operações bem-sucedidas.
    """

    success: bool = Field(True, description="Sempre true para sucessos")
    data: Any = Field(..., description="Dados da resposta")
    message: Optional[str] = Field(None, description="Mensagem de sucesso")

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return {"success": self.success, "data": self.data, "message": self.message}
