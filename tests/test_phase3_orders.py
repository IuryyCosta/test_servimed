"""
Testes automatizados para FASE 3 - Sistema de Pedidos
Sistema de pedidos integrado ao scraping Servimed

Este módulo testa:
- Modelos de dados de pedidos
- Lógica de tarefas de pedidos
- Integração com API do desafio
- Validações e regras de negócio
"""

import pytest
from datetime import datetime
from typing import List

# Importar modelos e funções para teste
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from servimed.models.order import (
    ProductItem,
    OrderRequest,
    OrderResponse,
    Order,
    OrderStatus
)


class TestProductItem:
    """Testes para o modelo ProductItem."""
    
    def test_product_item_creation_valid(self):
        """Testa criação de ProductItem com dados válidos."""
        product = ProductItem(
            gtin="7899095203136",
            codigo="446231",
            quantidade=1
        )
        
        assert product.gtin == "7899095203136"
        assert product.codigo == "446231"
        assert product.quantidade == 1
    
    def test_product_item_quantidade_minima(self):
        """Testa validação de quantidade mínima."""
        with pytest.raises(ValueError, match="Quantidade deve ser maior que zero"):
            ProductItem(
                gtin="7899095203136",
                codigo="446231",
                quantidade=0
            )
    
    def test_product_item_quantidade_negativa(self):
        """Testa validação de quantidade negativa."""
        with pytest.raises(ValueError, match="Quantidade deve ser maior que zero"):
            ProductItem(
                gtin="7899095203136",
                codigo="446231",
                quantidade=-1
            )
    
    def test_product_item_example_schema(self):
        """Testa se o schema de exemplo está correto."""
        product = ProductItem(
            gtin="7899095203136",
            codigo="446231",
            quantidade=1
        )
        
        # Verificar se o schema está configurado
        assert hasattr(product.Config, 'schema_extra')
        assert 'example' in product.Config.schema_extra


class TestOrderRequest:
    """Testes para o modelo OrderRequest."""
    
    def test_order_request_creation_valid(self):
        """Testa criação de OrderRequest com dados válidos."""
        produtos = [
            ProductItem(gtin="7899095203136", codigo="446231", quantidade=1),
            ProductItem(gtin="7898636193493", codigo="444212", quantidade=2)
        ]
        
        order = OrderRequest(
            usuario="teste@email.com",
            senha="senha123",
            id_pedido="PED001",
            produtos=produtos,
            callback_url="https://httpbin.org/post"
        )
        
        assert order.usuario == "teste@email.com"
        assert order.senha == "senha123"
        assert order.id_pedido == "PED001"
        assert len(order.produtos) == 2
        assert order.callback_url == "https://httpbin.org/post"
    
    def test_order_request_produtos_vazios(self):
        """Testa validação de lista de produtos vazia."""
        with pytest.raises(ValueError, match="Pedido deve ter pelo menos um produto"):
            OrderRequest(
                usuario="teste@email.com",
                senha="senha123",
                id_pedido="PED001",
                produtos=[],
                callback_url="https://httpbin.org/post"
            )
    
    def test_order_request_example_schema(self):
        """Testa se o schema de exemplo está correto."""
        produtos = [
            ProductItem(gtin="7899095203136", codigo="446231", quantidade=1)
        ]
        
        order = OrderRequest(
            usuario="fornecedor_user",
            senha="fornecedor_pass",
            id_pedido="1234",
            produtos=produtos,
            callback_url="https://desafio.cotefacil.net"
        )
        
        # Verificar se o schema está configurado
        assert hasattr(order.Config, 'schema_extra')
        assert 'example' in order.Config.schema_extra


class TestOrderResponse:
    """Testes para o modelo OrderResponse."""
    
    def test_order_response_creation_valid(self):
        """Testa criação de OrderResponse com dados válidos."""
        response = OrderResponse(
            codigo_confirmacao="ABC987",
            status="pedido_realizado"
        )
        
        assert response.codigo_confirmacao == "ABC987"
        assert response.status == "pedido_realizado"
    
    def test_order_response_example_schema(self):
        """Testa se o schema de exemplo está correto."""
        response = OrderResponse(
            codigo_confirmacao="ABC987",
            status="pedido_realizado"
        )
        
        # Verificar se o schema está configurado
        assert hasattr(response.Config, 'schema_extra')
        assert 'example' in response.Config.schema_extra


class TestOrder:
    """Testes para o modelo Order."""
    
    def test_order_creation_valid(self):
        """Testa criação de Order com dados válidos."""
        itens = [
            ProductItem(gtin="7899095203136", codigo="446231", quantidade=1)
        ]
        
        order = Order(
            id=64,
            codigo_fornecedor=None,
            status=None,
            itens=itens
        )
        
        assert order.id == 64
        assert order.codigo_fornecedor is None
        assert order.status is None
        assert len(order.itens) == 1
        assert order.itens[0].gtin == "7899095203136"
    
    def test_order_example_schema(self):
        """Testa se o schema de exemplo está correto."""
        itens = [
            ProductItem(gtin="7899095203136", codigo="446231", quantidade=1)
        ]
        
        order = Order(
            id=64,
            codigo_fornecedor=None,
            status=None,
            itens=itens
        )
        
        # Verificar se o schema está configurado
        assert hasattr(order.Config, 'schema_extra')
        assert 'example' in order.Config.schema_extra


class TestOrderStatus:
    """Testes para o modelo OrderStatus."""
    
    def test_order_status_creation_valid(self):
        """Testa criação de OrderStatus com dados válidos."""
        status = OrderStatus(
            task_id="uuid-1234",
            status="pending",
            progress=0.0,
            message="Tarefa criada com sucesso",
            created_at=datetime.now(),
            started_at=None,
            completed_at=None,
            error=None,
            result=None
        )
        
        assert status.task_id == "uuid-1234"
        assert status.status == "pending"
        assert status.progress == 0.0
        assert status.message == "Tarefa criada com sucesso"
        assert status.created_at is not None
        assert status.started_at is None
        assert status.completed_at is None
        assert status.error is None
        assert status.result is None
    
    def test_order_status_progress_validation(self):
        """Testa validação de progresso entre 0.0 e 1.0."""
        # Progresso válido
        status = OrderStatus(
            task_id="uuid-1234",
            status="processing",
            progress=0.5,
            message="Processando...",
            created_at=datetime.now(),
            started_at=None,
            completed_at=None,
            error=None,
            result=None
        )
        assert status.progress == 0.5
        
        # Progresso inválido - menor que 0.0
        with pytest.raises(ValueError, match="Progresso deve estar entre 0.0 e 1.0"):
            OrderStatus(
                task_id="uuid-1234",
                status="processing",
                progress=-0.1,
                message="Processando...",
                created_at=datetime.now(),
                started_at=None,
                completed_at=None,
                error=None,
                result=None
            )
        
        # Progresso inválido - maior que 1.0
        with pytest.raises(ValueError, match="Progresso deve estar entre 0.0 e 1.0"):
            OrderStatus(
                task_id="uuid-1234",
                status="processing",
                progress=1.1,
                message="Processando...",
                created_at=datetime.now(),
                started_at=None,
                completed_at=None,
                error=None,
                result=None
            )
    
    def test_order_status_example_schema(self):
        """Testa se o schema de exemplo está correto."""
        status = OrderStatus(
            task_id="uuid-1234",
            status="pending",
            progress=0.0,
            message="Tarefa criada com sucesso",
            created_at=datetime.now(),
            started_at=None,
            completed_at=None,
            error=None,
            result=None
        )
        
        # Verificar se o schema está configurado
        assert hasattr(status.Config, 'schema_extra')
        assert 'example' in status.Config.schema_extra


class TestIntegration:
    """Testes de integração entre os modelos."""
    
    def test_complete_order_flow(self):
        """Testa fluxo completo de criação de pedido."""
        # 1. Criar produtos
        produtos = [
            ProductItem(gtin="7899095203136", codigo="446231", quantidade=1),
            ProductItem(gtin="7898636193493", codigo="444212", quantidade=2)
        ]
        
        # 2. Criar requisição de pedido
        order_request = OrderRequest(
            usuario="teste@email.com",
            senha="senha123",
            id_pedido="PED001",
            produtos=produtos,
            callback_url="https://httpbin.org/post"
        )
        
        # 3. Simular resposta da API
        order_response = OrderResponse(
            codigo_confirmacao="ABC987",
            status="pedido_realizado"
        )
        
        # 4. Criar estrutura de pedido
        order = Order(
            id=64,
            codigo_fornecedor="FORN001",
            status="confirmado",
            itens=produtos
        )
        
        # 5. Criar status de processamento
        order_status = OrderStatus(
            task_id="uuid-1234",
            status="completed",
            progress=1.0,
            message="Pedido processado com sucesso",
            created_at=datetime.now(),
            started_at=datetime.now(),
            completed_at=datetime.now(),
            error=None,
            result=order_response.dict()
        )
        
        # Verificações de integração
        assert len(order_request.produtos) == len(order.itens)
        assert order_request.id_pedido == "PED001"
        assert order_response.status == "pedido_realizado"
        assert order_status.status == "completed"
        assert order_status.progress == 1.0
        assert order_status.result is not None


if __name__ == "__main__":
    # Executar testes
    pytest.main([__file__, "-v"])
