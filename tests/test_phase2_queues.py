"""
Testes automatizados para FASE 2 - Sistema de Filas
Sistema de filas assíncrono com Celery + Redis

Este módulo testa:
- Modelos de dados de scraping
- Sistema de filas Celery
- Validações e regras de negócio
"""

import pytest
from datetime import datetime
from typing import List

# Importar modelos e funções para teste
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from servimed.models.scraping_task import (
    ScrapingTaskRequest,
    ScrapingTaskResponse,
    ScrapingTaskStatus
)


class TestScrapingTaskRequest:
    """Testes para o modelo ScrapingTaskRequest."""
    
    def test_scraping_task_request_creation_valid(self):
        """Testa criação de ScrapingTaskRequest com dados válidos."""
        request = ScrapingTaskRequest(
            usuario="teste@email.com",
            senha="senha123",
            callback_url="https://httpbin.org/post"
        )
        
        assert request.usuario == "teste@email.com"
        assert request.senha == "senha123"
        assert request.callback_url == "https://httpbin.org/post"
    
    def test_scraping_task_request_usuario_vazio(self):
        """Testa validação de usuário vazio."""
        with pytest.raises(ValueError, match="Usuário não pode estar vazio"):
            ScrapingTaskRequest(
                usuario="",
                senha="senha123",
                callback_url="https://httpbin.org/post"
            )
    
    def test_scraping_task_request_senha_vazia(self):
        """Testa validação de senha vazia."""
        with pytest.raises(ValueError, match="Senha não pode estar vazia"):
            ScrapingTaskRequest(
                usuario="teste@email.com",
                senha="",
                callback_url="https://httpbin.org/post"
            )
    
    def test_scraping_task_request_callback_url_invalida(self):
        """Testa validação de URL de callback inválida."""
        with pytest.raises(ValueError, match="URL de callback deve ser uma URL válida"):
            ScrapingTaskRequest(
                usuario="teste@email.com",
                senha="senha123",
                callback_url="url_invalida"
            )
    
    def test_scraping_task_request_example_schema(self):
        """Testa se o schema de exemplo está correto."""
        request = ScrapingTaskRequest(
            usuario="fornecedor_user",
            senha="fornecedor_pass",
            callback_url="https://desafio.cotefacil.net"
        )
        
        # Verificar se o schema está configurado
        assert hasattr(request.Config, 'schema_extra')
        assert 'example' in request.Config.schema_extra


class TestScrapingTaskResponse:
    """Testes para o modelo ScrapingTaskResponse."""
    
    def test_scraping_task_response_creation_valid(self):
        """Testa criação de ScrapingTaskResponse com dados válidos."""
        response = ScrapingTaskResponse(
            task_id="uuid-1234",
            status="pending",
            message="Tarefa criada com sucesso",
            created_at=datetime.now(),
            estimated_completion=None
        )
        
        assert response.task_id == "uuid-1234"
        assert response.status == "pending"
        assert response.message == "Tarefa criada com sucesso"
        assert response.created_at is not None
        assert response.estimated_completion is None
    
    def test_scraping_task_response_status_validation(self):
        """Testa validação de status da tarefa."""
        # Status válidos
        valid_statuses = ["pending", "processing", "completed", "failed"]
        
        for status in valid_statuses:
            response = ScrapingTaskResponse(
                task_id="uuid-1234",
                status=status,
                message="Tarefa criada com sucesso",
                created_at=datetime.now(),
                estimated_completion=None
            )
            assert response.status == status
        
        # Status inválido
        with pytest.raises(ValueError, match="Status deve ser um dos: pending, processing, completed, failed"):
            ScrapingTaskResponse(
                task_id="uuid-1234",
                status="invalid_status",
                message="Tarefa criada com sucesso",
                created_at=datetime.now(),
                estimated_completion=None
            )
    
    def test_scraping_task_response_example_schema(self):
        """Testa se o schema de exemplo está correto."""
        response = ScrapingTaskResponse(
            task_id="uuid-1234",
            status="pending",
            message="Tarefa criada com sucesso",
            created_at=datetime.now(),
            estimated_completion=None
        )
        
        # Verificar se o schema está configurado
        assert hasattr(response.Config, 'schema_extra')
        assert 'example' in response.Config.schema_extra


class TestScrapingTaskStatus:
    """Testes para o modelo ScrapingTaskStatus."""
    
    def test_scraping_task_status_creation_valid(self):
        """Testa criação de ScrapingTaskStatus com dados válidos."""
        status = ScrapingTaskStatus(
            task_id="uuid-1234",
            status="pending",
            progress=0.0,
            message="Tarefa aguardando processamento",
            created_at=datetime.now(),
            started_at=None,
            completed_at=None,
            error=None,
            result=None
        )
        
        assert status.task_id == "uuid-1234"
        assert status.status == "pending"
        assert status.progress == 0.0
        assert status.message == "Tarefa aguardando processamento"
        assert status.created_at is not None
        assert status.started_at is None
        assert status.completed_at is None
        assert status.error is None
        assert status.result is None
    
    def test_scraping_task_status_progress_validation(self):
        """Testa validação de progresso entre 0.0 e 1.0."""
        # Progresso válido
        status = ScrapingTaskStatus(
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
            ScrapingTaskStatus(
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
            ScrapingTaskStatus(
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
    
    def test_scraping_task_status_example_schema(self):
        """Testa se o schema de exemplo está correto."""
        status = ScrapingTaskStatus(
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
    
    def test_complete_scraping_flow(self):
        """Testa fluxo completo de criação de tarefa de scraping."""
        # 1. Criar requisição
        request = ScrapingTaskRequest(
            usuario="teste@email.com",
            senha="senha123",
            callback_url="https://httpbin.org/post"
        )
        
        # 2. Simular resposta de criação
        response = ScrapingTaskResponse(
            task_id="uuid-1234",
            status="pending",
            message="Tarefa criada com sucesso",
            created_at=datetime.now(),
            estimated_completion=None
        )
        
        # 3. Simular status de processamento
        status = ScrapingTaskStatus(
            task_id="uuid-1234",
            status="completed",
            progress=1.0,
            message="Tarefa concluída com sucesso",
            created_at=datetime.now(),
            started_at=datetime.now(),
            completed_at=datetime.now(),
            error=None,
            result={"total_products": 298, "products": []}
        )
        
        # Verificações de integração
        assert request.usuario == "teste@email.com"
        assert response.task_id == "uuid-1234"
        assert status.task_id == response.task_id
        assert status.status == "completed"
        assert status.progress == 1.0
        assert status.result is not None


if __name__ == "__main__":
    # Executar testes
    pytest.main([__file__, "-v"])
