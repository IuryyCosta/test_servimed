"""
Script para iniciar Workers Celery - Fase 2.

Este script inicia os workers Celery para processar tarefas de scraping.
"""

import subprocess
import sys
import time
import os
from pathlib import Path


def start_celery_worker():
    """Inicia o worker Celery."""
    try:
        print(" Iniciando Worker Celery...")

        # Configurar variáveis de ambiente
        env = os.environ.copy()
        env["CELERY_BROKER_URL"] = "redis://localhost:6379/0"
        env["CELERY_RESULT_BACKEND"] = "redis://localhost:6379/0"

        # Comando para iniciar worker
        cmd = [
            sys.executable,
            "-m",
            "celery",
            "-A",
            "queues.celery_config",
            "worker",
            "--loglevel=info",
            "--concurrency=2",
        ]

        print(f" Comando: {' '.join(cmd)}")
        print(" Broker: redis://localhost:6379/0")
        print(" Concorrência: 2 workers")
        print(" Log Level: info")
        print("-" * 50)

        # Iniciar worker
        process = subprocess.Popen(cmd, env=env, cwd=Path(__file__).parent.parent)

        print(" Worker Celery iniciado!")
        print(f" PID: {process.pid}")
        print(" Pressione Ctrl+C para parar")

        # Aguardar processo
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n Parando worker...")
            process.terminate()
            process.wait()
            print(" Worker parado")

    except Exception as e:
        print(f" Erro ao iniciar worker: {e}")
        return False


def main():
    """Função principal."""
    print("=" * 50)
    print(" INICIANDO WORKERS CELERY")
    print("=" * 50)

    print(" Pré-requisitos:")
    print("    Redis rodando (localhost:6379)")
    print("    Dependências instaladas")
    print("    Configuração Celery válida")
    print("-" * 50)

    # Iniciar worker
    start_celery_worker()


if __name__ == "__main__":
    main()



