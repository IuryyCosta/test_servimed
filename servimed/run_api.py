"""
Script para executar a API FastAPI do projeto Servimed - Fase 2.
"""

import os
import sys
import uvicorn
from pathlib import Path

# Adicionar o diretório raiz ao path para importações
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from api.main import app


def main():
    """Função principal para executar a API."""

    # Configurações do servidor
    host = os.getenv("FASTAPI_HOST", "0.0.0.0")
    port = int(os.getenv("FASTAPI_PORT", "8000"))
    reload = os.getenv("FASTAPI_RELOAD", "true").lower() == "true"
    log_level = os.getenv("FASTAPI_LOG_LEVEL", "info")

    print(f"🚀 Iniciando Servimed Scraping API...")
    print(f"📍 Host: {host}")
    print(f"🔌 Porta: {port}")
    print(f"🔄 Reload: {reload}")
    print(f"📝 Log Level: {log_level}")
    print(f"🌐 URL: http://{host}:{port}")
    print(f"📚 Docs: http://{host}:{port}/docs")
    print("-" * 50)

    try:
        # Iniciar servidor Uvicorn
        uvicorn.run(
            "api.main:app",
            host=host,
            port=port,
            reload=reload,
            log_level=log_level,
            access_log=True,
        )

    except KeyboardInterrupt:
        print("\n⏹️ Servidor interrompido pelo usuário")
        sys.exit(0)

    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
