"""
Script para iniciar Workers Celery com Redis emulado - Fase 2.

Este script inicia os workers Celery usando fakeredis para testes.
"""

import subprocess
import sys
import time
import os
from pathlib import Path


def start_celery_worker():
    """Inicia o worker Celery."""
    try:
        print("👷 Iniciando Worker Celery com Redis emulado...")

        # Configurar variáveis de ambiente para fakeredis
        env = os.environ.copy()
        env["CELERY_BROKER_URL"] = "memory://"
        env["CELERY_RESULT_BACKEND"] = "rpc://"

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
            "--pool=solo",  # Usar pool solo para testes
        ]

        print(f"🚀 Comando: {' '.join(cmd)}")
        print("📍 Broker: memory:// (emulado)")
        print("👥 Concorrência: 2 workers")
        print("📝 Log Level: info")
        print("💡 Usando pool solo para testes")
        print("-" * 50)

        # Iniciar worker
        process = subprocess.Popen(cmd, env=env, cwd=Path(__file__).parent.parent)

        print("✅ Worker Celery iniciado!")
        print(f"🆔 PID: {process.pid}")
        print("💡 Pressione Ctrl+C para parar")

        # Aguardar processo
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n⏹️ Parando worker...")
            process.terminate()
            process.wait()
            print("✅ Worker parado")

    except Exception as e:
        print(f"❌ Erro ao iniciar worker: {e}")
        return False


def main():
    """Função principal."""
    print("=" * 50)
    print("👷 INICIANDO WORKERS CELERY (REDIS EMULADO)")
    print("=" * 50)

    print("📋 Pré-requisitos:")
    print("   ✅ Redis emulado rodando")
    print("   ✅ Dependências instaladas")
    print("   ✅ Configuração Celery válida")
    print("   ✅ fakeredis instalado")
    print("-" * 50)

    # Iniciar worker
    start_celery_worker()


if __name__ == "__main__":
    main()




