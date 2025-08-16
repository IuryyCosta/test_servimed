"""
Configuração do Celery para o projeto Servimed - Fase 2.

Este módulo configura o broker Redis e as configurações
básicas do Celery para processamento assíncrono.
"""

import os
from celery import Celery
from ..config import get_config

# Configurações do Celery
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

# Configurações de tarefas
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TIMEZONE = "America/Sao_Paulo"
CELERY_ENABLE_UTC = True

# Configurações de concorrência
CELERY_WORKER_CONCURRENCY = 4
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000
CELERY_WORKER_PREFETCH_MULTIPLIER = 1

# Configurações de retry
CELERY_TASK_ACKS_LATE = True
CELERY_WORKER_DISABLE_RATE_LIMITS = False

# Configurações de logging
CELERY_WORKER_HIJACK_ROOT_LOGGER = False
CELERY_WORKER_LOG_FORMAT = "[%(asctime)s: %(levelname)s/%(processName)s] %(message)s"

# Configurações de filas
CELERY_TASK_DEFAULT_QUEUE = "scraping"
CELERY_TASK_DEFAULT_EXCHANGE = "scraping"
CELERY_TASK_DEFAULT_ROUTING_KEY = "scraping"

# Configurações de segurança
CELERY_SECURITY_KEY = os.getenv("CELERY_SECURITY_KEY", "servimed-secret-key")
CELERY_SECURITY_CERTIFICATE = os.getenv("CELERY_SECURITY_CERTIFICATE", None)
CELERY_SECURITY_CERTIFICATE_KEY = os.getenv("CELERY_SECURITY_CERTIFICATE_KEY", None)

def create_celery_app():
    """
    Cria e configura a aplicação Celery.
    
    Returns:
        Celery: Aplicação Celery configurada
    """
    app = Celery(
        "servimed",
        broker=CELERY_BROKER_URL,
        backend=CELERY_RESULT_BACKEND,
        include=["servimed.tasks.scraping_tasks"]
    )
    
    # Aplicar configurações
    app.conf.update(
        task_serializer=CELERY_TASK_SERIALIZER,
        result_serializer=CELERY_RESULT_SERIALIZER,
        accept_content=CELERY_ACCEPT_CONTENT,
        timezone=CELERY_TIMEZONE,
        enable_utc=CELERY_ENABLE_UTC,
        worker_concurrency=CELERY_WORKER_CONCURRENCY,
        worker_max_tasks_per_child=CELERY_WORKER_MAX_TASKS_PER_CHILD,
        worker_prefetch_multiplier=CELERY_WORKER_PREFETCH_MULTIPLIER,
        task_acks_late=CELERY_TASK_ACKS_LATE,
        worker_disable_rate_limits=CELERY_WORKER_DISABLE_RATE_LIMITS,
        worker_hijack_root_logger=CELERY_WORKER_HIJACK_ROOT_LOGGER,
        worker_log_format=CELERY_WORKER_LOG_FORMAT,
        task_default_queue=CELERY_TASK_DEFAULT_QUEUE,
        task_default_exchange=CELERY_TASK_DEFAULT_EXCHANGE,
        task_default_routing_key=CELERY_TASK_DEFAULT_ROUTING_KEY,
        security_key=CELERY_SECURITY_KEY,
        security_certificate=CELERY_SECURITY_CERTIFICATE,
        security_certificate_key=CELERY_SECURITY_CERTIFICATE_KEY,
    )
    
    return app

# Instância global do Celery
celery_app = create_celery_app()
