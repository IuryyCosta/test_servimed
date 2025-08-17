"""
Script para iniciar Redis emulado (fakeredis) - Fase 2.

Este script inicia um Redis emulado para testes sem precisar instalar Redis.
"""

import fakeredis
import time
import threading


def start_fake_redis():
    """Inicia Redis emulado."""
    try:
        print("🚀 Iniciando Redis emulado (fakeredis)...")

        # Criar servidor Redis emulado
        server = fakeredis.FakeServer()

        # Criar cliente Redis
        r = fakeredis.FakeRedis(server=server)

        # Testar conexão
        r.set("test", "redis_working")
        result = r.get("test")

        if result == b"redis_working":
            print("✅ Redis emulado funcionando!")
            print("📍 Host: localhost (emulado)")
            print("🔌 Porta: 6379 (emulado)")
            print("📊 Status: Conectado (emulado)")
            print("💡 Este é um Redis emulado para testes")

            # Manter servidor rodando
            print("⏳ Servidor emulado rodando...")
            print("💡 Pressione Ctrl+C para parar")

            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n⏹️ Parando Redis emulado...")
                print("✅ Redis emulado parado")

        else:
            print("❌ Falha no Redis emulado")
            return False

    except Exception as e:
        print(f"❌ Erro ao iniciar Redis emulado: {e}")
        return False


def main():
    """Função principal."""
    print("=" * 50)
    print("🔍 INICIANDO REDIS EMULADO")
    print("=" * 50)

    print("📋 Informações:")
    print("   ✅ Usando fakeredis (Redis emulado)")
    print("   ✅ Não precisa instalar Redis")
    print("   ✅ Ideal para testes e desenvolvimento")
    print("   ⚠️ Não use em produção")
    print("-" * 50)

    # Iniciar Redis emulado
    start_fake_redis()


if __name__ == "__main__":
    main()
