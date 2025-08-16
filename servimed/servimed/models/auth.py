"""
Modelos de dados para autenticação OAuth2.

Este módulo define as estruturas de dados para:
- Credenciais de login
- Tokens de acesso
- Respostas de autenticação
"""

from typing import Optional
from pydantic import BaseModel, Field, validator


class AuthCredentials(BaseModel):

    username: str = Field(..., description="Email do usuário")
    password: str = Field(..., description="Senha do usuário")

    @validator("username")
    def validate_username(cls, v):
        """Valida formato básico do email."""
        if not v or "@" not in v:
            raise ValueError("Username deve ser um email válido")
        return v.strip().lower()

    @validator("password")
    def validate_password(cls, v):
        """Valida que a senha não esteja vazia."""
        if not v or len(v.strip()) < 1:
            raise ValueError("Senha não pode estar vazia")
        return v

    def to_dict(self) -> dict:
        """Converte para dicionário (sem senha para segurança)."""
        return {"username": self.username, "password": "***"}  # Mascarar senha


class AuthToken(BaseModel):
    """
    Token de acesso OAuth2.

    Resposta do endpoint /oauth/token.
    """

    token_type: str = Field(..., description="Tipo do token (Bearer)")
    access_token: str = Field(..., description="Token de acesso JWT")
    expires_in: int = Field(..., description="Tempo de expiração em segundos")

    @validator("token_type")
    def validate_token_type(cls, v):
        """Valida tipo do token."""
        if v.lower() != "bearer":
            raise ValueError("Tipo de token deve ser Bearer")
        return v

    @validator("access_token")
    def validate_access_token(cls, v):
        """Valida que o token não esteja vazio."""
        if not v or len(v.strip()) < 10:
            raise ValueError("Token de acesso inválido")
        return v.strip()

    @validator("expires_in")
    def validate_expires_in(cls, v):
        """Valida tempo de expiração."""
        if v <= 0:
            raise ValueError("Tempo de expiração deve ser positivo")
        return v

    def get_authorization_header(self) -> str:
        """Retorna header de autorização para requisições."""
        return f"{self.token_type} {self.access_token}"

    def is_expired(self, current_timestamp: int) -> bool:
        """Verifica se o token expirou."""
        return current_timestamp >= self.expires_in

    def __str__(self) -> str:
        """Representação segura do token."""
        return f"AuthToken(type={self.token_type}, expires_in={self.expires_in})"


class AuthResponse(BaseModel):
    """
    Resposta de autenticação.

    Pode conter token ou mensagem de erro.
    """

    success: bool = Field(..., description="Indica se a autenticação foi bem-sucedida")
    token: Optional[AuthToken] = Field(None, description="Token de acesso (se sucesso)")
    error: Optional[str] = Field(None, description="Mensagem de erro (se falha)")

    @validator("error")
    def validate_error(cls, v, values):
        """Valida que erro existe apenas quando não há sucesso."""
        if values.get("success") and v:
            raise ValueError("Erro não deve existir quando autenticação é bem-sucedida")
        if not values.get("success") and not v:
            raise ValueError("Erro deve ser informado quando autenticação falha")
        return v

    def to_dict(self) -> dict:
        """Converte para dicionário."""
        return {
            "success": self.success,
            "token": self.token.dict() if self.token else None,
            "error": self.error,
        }
