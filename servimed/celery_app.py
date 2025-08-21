"""
Configuração Celery para o projeto Servimed
"""

import os
from celery import Celery

# Configuração básica
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")

# Criar app Celery 
celery_app = Celery(
    "servimed",
    broker=CELERY_BROKER_URL,
    include=["tasks.scraping_tasks", "tasks.order_tasks"],
) 

# Configurações 
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    timezone="America/Sao_Paulo",
    enable_utc=True,
    worker_concurrency=4,
    task_default_queue="scraping",
)
