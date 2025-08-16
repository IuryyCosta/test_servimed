"""
Modelo de dados para produtos do Servimed.

Este módulo define a estrutura de dados para produtos extraídos
da API, incluindo validação e serialização automática.
"""

from pydantic import BaseModel, Field, validator


class Product(BaseModel):
    """
    Modelo de dados para produtos do Servimed.

    Representa a estrutura retornada pelo endpoint /produto
    com validação automática de tipos e formatos.
    """

    id: int = Field(..., description="ID único do produto")
    gtin: str = Field(..., description="Código GTIN do produto")
    codigo: str = Field(..., description="Código interno do produto")
    descricao: str = Field(..., description="Descrição/nome do produto")
    preco_fabrica: float = Field(..., description="Preço de fábrica do produto")
    estoque: int = Field(..., description="Quantidade em estoque")

    @validator("preco_fabrica")
    def validate_preco_fabrica(cls, v):
        """Valida que o preço não seja negativo."""
        if v < 0:
            raise ValueError("Preço de fábrica não pode ser negativo")
        return v

    @validator("estoque")
    def validate_estoque(cls, v):
        """Valida que o estoque não seja negativo."""
        if v < 0:
            raise ValueError("Estoque não pode ser negativo")
        return v

    @validator("gtin")
    def validate_gtin(cls, v):
        """Valida formato básico do GTIN."""
        if not v or len(v.strip()) == 0:
            raise ValueError("GTIN não pode estar vazio")
        return v.strip()

    def to_dict(self) -> dict:
        """Converte o modelo para dicionário."""
        return self.dict()

    def __str__(self) -> str:
        """Representação string do produto."""
        return f"Product(id={self.id}, codigo='{self.codigo}', descricao='{self.descricao}')"
