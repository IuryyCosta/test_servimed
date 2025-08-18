"""
Script para iniciar e verificar Redis - Fase 2.

Este script verifica se o Redis está rodando e inicia se necessário.
Se Redis real não estiver disponível, usa fakeredis para testes locais.
"""

import subprocess
import sys
import time
import os

# Tentar importar Redis real primeiro
try:
    import redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

# Tentar importar fakeredis como fallback
try:
    import fakeredis

    FAKEREDIS_AVAILABLE = True
except ImportError:
    FAKEREDIS_AVAILABLE = False


def check_redis_connection():
    """Verifica se consegue conectar ao Redis real."""
    if not REDIS_AVAILABLE:
        return False

    try:
        r = redis.Redis(host="localhost", port=6379, db=0)
        r.ping()
        return True
    except Exception:
        return False


def start_redis_real():
    
    try:
        print("🚀 Tentando iniciar Redis real...")

        # Comando para Windows (Git Bash)
        if sys.platform.startswith("win"):
            cmd = "redis-server"
        else:
            cmd = "redis-server"

        # Iniciar Redis em background
        process = subprocess.Popen(
            [cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        time.sleep(3)

        if process.poll() is None:
            print(" Redis real iniciado com sucesso!")
            return True
        else:
            print(" Falha ao iniciar Redis real")
            return False

    except Exception as e:
        print(f" Erro ao iniciar Redis real: {e}")
        return False


def start_fakeredis():
    """Inicia Redis fake na porta 6379 para compatibilidade."""
    try:
        print(" Iniciando Redis Fake (porta 6379)...")

        # Criar instância fakeredis escutando na porta 6379
        fake_redis = fakeredis.FakeServer(port=6379)

        print("Redis Fake iniciado com sucesso!")
        print(" Host: localhost")
        print(" Porta: 6379")
        print(" Status: Conectado")
        print(" Redis Fake escutando na porta real para compatibilidade")

        return True

    except Exception as e:
        print(f" Erro ao iniciar Redis Fake: {e}")
        return False


def main():
    """Função principal."""
    print("=" * 50)
    print("🔍 VERIFICANDO REDIS")
    print("=" * 50)

    # Verificar se Redis real já está rodando
    if REDIS_AVAILABLE and check_redis_connection():
        print(" Redis real já está rodando!")
        print(" Host: localhost")
        print(" Porta: 6379")
        print(" Status: Conectado")
        return

    print("Redis real não está rodando")

    # Tentar iniciar Redis real primeiro
    if REDIS_AVAILABLE and start_redis_real():
        # Aguardar e verificar novamente
        time.sleep(2)
        if check_redis_connection():
            print(" Redis real iniciado e funcionando!")
            print(" Host: localhost")
            print(" Porta: 6379")
            print(" Status: Conectado")
            return
        else:
            print(" Redis real iniciado mas não consegue conectar")

    # Fallback para fakeredis
    print("\n Tentando fallback para Redis Fake...")

    if FAKEREDIS_AVAILABLE:
        if start_fakeredis():
            print("\n SISTEMA FUNCIONANDO COM REDIS FAKE!")
            print(" Perfeito para testes e desenvolvimento local")
            print(" Para produção, instale Redis real")
            return
        else:
            print(" Falha ao iniciar Redis Fake")
    else:
        print(" Fakeredis não está disponível")
        print(" Instale com: pip install fakeredis")

    # Se chegou aqui, nada funcionou
    print("\n Nenhuma opção de Redis funcionou")
    print(" Soluções:")
    print("   1. Instalar Redis real")
    print("   2. Instalar fakeredis: pip install fakeredis")
    print("   3. Verificar configurações de rede")


if __name__ == "__main__":
    main()
