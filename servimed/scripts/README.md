# 📁 Scripts Utilitários - Servimed

Esta pasta contém scripts para iniciar e testar o sistema Servimed Fase 2.

## 🚀 Scripts Disponíveis

### 1. **`start_redis.py`** - Iniciar Redis

```bash
python scripts/start_redis.py
```

- Verifica se Redis está rodando
- Inicia Redis se necessário
- Confirma conexão

### 2. **`start_workers.py`** - Iniciar Workers Celery

```bash
python scripts/start_workers.py
```

- Inicia workers Celery
- Configura broker Redis
- 2 workers concorrentes

### 3. **`start_api.py`** - Iniciar API FastAPI

```bash
python scripts/start_api.py
```

- Inicia API FastAPI
- Porta 8000
- Reload automático

### 4. **`test_system.py`** - Testar Sistema Completo

```bash
python scripts/test_system.py
```

- Testa saúde da API
- Cria tarefa de scraping
- Monitora progresso

## 📋 Ordem de Execução

1. **Redis** → `start_redis.py`
2. **Workers** → `start_workers.py` (em novo terminal)
3. **API** → `start_api.py` (em novo terminal)
4. **Teste** → `test_system.py` (em novo terminal)

## 🔧 Pré-requisitos

- ✅ Redis instalado
- ✅ Dependências Python instaladas
- ✅ Configuração válida
- ✅ Ambiente virtual ativado

## 📊 Status dos Serviços

- **Redis**: localhost:6379
- **Celery**: 2 workers ativos
- **FastAPI**: http://localhost:8000
- **Docs**: http://localhost:8000/docs



