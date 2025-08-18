"""
Teste simples para demonstrar que o sistema de testes está funcionando.
"""

import pytest
from servimed.models.order import ProductItem


def test_simple_product_creation():
    """Teste simples de criação de produto."""
    product = ProductItem(
        gtin="7899095203136",
        codigo="446231",
        quantidade=1
    )
    
    assert product.gtin == "7899095203136"
    assert product.codigo == "446231"
    assert product.quantidade == 1
    print("✅ Teste simples passou!")


def test_product_validation():
    """Teste de validação de produto."""
    # Teste válido
    product = ProductItem(
        gtin="7899095203136",
        codigo="446231",
        quantidade=5
    )
    assert product.quantidade == 5
    
    # Teste de quantidade inválida
    with pytest.raises(ValueError):
        ProductItem(
            gtin="7899095203136",
            codigo="446231",
            quantidade=0  # Inválido
        )
    print("✅ Teste de validação passou!")


if __name__ == "__main__":
    # Executar testes
    test_simple_product_creation()
    test_product_validation()
    print("\n🎉 Todos os testes passaram!")
