"""
Configurações do Projeto Servimed - Desafio Técnico

Este módulo centraliza todas as configurações do projeto, carregando
variáveis de ambiente e validando configurações obrigatórias.
"""

import os
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Exceção personalizada para erros de configuração."""

    pass


@dataclass
class OAuth2Config:
    """Configurações OAuth2 para autenticação na API."""
    username: str
    password: str
    client_id: str
    client_secret: str
    grant_type: str
    scope: str

    @classmethod
    def from_env(cls) -> "OAuth2Config":
        """Cria instância a partir de variáveis de ambiente."""
        return cls(
            username=os.getenv("SERVIMED_USERNAME", "string"),
            password=os.getenv("SERVIMED_PASSWORD", "********"),
            client_id=os.getenv("OAUTH2_CLIENT_ID", "string"),
            client_secret=os.getenv("OAUTH2_CLIENT_SECRET", "********"),
            grant_type=os.getenv("OAUTH2_GRANT_TYPE", "password"),
            scope=os.getenv("OAUTH2_SCOPE", ""),
        )


@dataclass
class APIConfig:
    """Configurações da API de callback."""

    base_url: str
    signup_endpoint: str
    token_endpoint: str
    products_endpoint: str

    @classmethod
    def from_env(cls) -> "APIConfig":
        """Cria instância a partir de variáveis de ambiente."""
        return cls(
            base_url=os.getenv("CALLBACK_API_BASE_URL", ""),
            signup_endpoint=os.getenv("CALLBACK_API_SIGNUP_ENDPOINT", ""),
            token_endpoint=os.getenv("CALLBACK_API_TOKEN_ENDPOINT", ""),
            products_endpoint=os.getenv("CALLBACK_API_PRODUCTS_ENDPOINT", ""),
        )


@dataclass
class ScrapyConfig:
    """Configurações do Scrapy."""

    log_level: str
    download_delay: int
    concurrent_requests: int
    download_timeout: int

    @classmethod
    def from_env(cls) -> "ScrapyConfig":
        """Cria instância a partir de variáveis de ambiente."""
        return cls(
            log_level=os.getenv("SCRAPY_LOG_LEVEL", "INFO"),
            download_delay=int(os.getenv("SCRAPY_DOWNLOAD_DELAY", "1")),
            concurrent_requests=int(os.getenv("SCRAPY_CONCURRENT_REQUESTS", "16")),
            download_timeout=int(os.getenv("SCRAPY_DOWNLOAD_TIMEOUT", "30")),
        )


@dataclass
class OutputConfig:
    """Configurações de saída e armazenamento."""

    directory: str
    filename_prefix: str

    @classmethod
    def from_env(cls) -> "OutputConfig":
        """Cria instância a partir de variáveis de ambiente."""
        return cls(
            directory=os.getenv("OUTPUT_DIRECTORY", "dados_servimed"),
            filename_prefix=os.getenv("OUTPUT_FILENAME_PREFIX", "produtos_servimed"),
        )


@dataclass
class LogConfig:
    """Configurações de logging."""

    level: str
    format: str
    file: str

    @classmethod
    def from_env(cls) -> "LogConfig":
        """Cria instância a partir de variáveis de ambiente."""
        return cls(
            level=os.getenv("LOG_LEVEL", "INFO"),
            format=os.getenv("LOG_FORMAT", "json"),
            file=os.getenv("LOG_FILE", "logs/servimed.log"),
        )


@dataclass
class CacheConfig:
    """Configurações de cache."""

    enabled: bool
    ttl: int

    @classmethod
    def from_env(cls) -> "CacheConfig":
        """Cria instância a partir de variáveis de ambiente."""
        return cls(
            enabled=os.getenv("CACHE_ENABLED", "true").lower() == "true",
            ttl=int(os.getenv("CACHE_TTL", "1800")),
        )


@dataclass
class RetryConfig:
    """Configurações de retry."""

    max_attempts: int
    delay: int

    @classmethod
    def from_env(cls) -> "RetryConfig":
        """Cria instância a partir de variáveis de ambiente."""
        return cls(
            max_attempts=int(os.getenv("MAX_RETRY_ATTEMPTS", "3")),
            delay=int(os.getenv("RETRY_DELAY", "5")),
        )


class Config:
    """
    Classe principal de configuração do projeto.

    Centraliza todas as configurações e valida variáveis obrigatórias.
    """

    def __init__(self):
        """Inicializa configurações carregando variáveis de ambiente."""
        self._load_environment()
        self._validate_configuration()
        self._setup_logging()

    def _load_environment(self) -> None:
        """Carrega variáveis de ambiente do arquivo .env."""
        try:
            # Tentar carregar do arquivo .env na raiz do projeto
            env_path = Path(__file__).parent.parent / ".env"
            if env_path.exists():
                load_dotenv(env_path)
                logger.info("Arquivo .env carregado com sucesso")
            else:
                logger.warning(
                    "Arquivo .env não encontrado, usando variáveis do sistema"
                )
                load_dotenv()
        except Exception as e:
            logger.error(f"Erro ao carregar arquivo .env: {e}")
            raise ConfigurationError(f"Falha ao carregar configurações: {e}")

    def _validate_configuration(self) -> None:
        """Valida configurações obrigatórias."""
        required_vars = [
            "SERVIMED_USERNAME",
            "SERVIMED_PASSWORD",
            "CALLBACK_API_BASE_URL",
        ]

        missing_vars = [var for var in required_vars if not os.getenv(var)]

        if missing_vars:
            error_msg = f"Variáveis de ambiente obrigatórias não encontradas: {', '.join(missing_vars)}"
            logger.error(error_msg)
            raise ConfigurationError(error_msg)

        logger.info("Todas as configurações obrigatórias foram validadas")

    def _setup_logging(self) -> None:
        """Configura sistema de logging."""
        log_config = self.log
        log_level = getattr(logging, log_config.level.upper(), logging.INFO)

        # Configurar logging para arquivo
        log_file = Path(log_config.file)
        log_file.parent.mkdir(parents=True, exist_ok=True)

        # Configurar handler para arquivo
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)

        # Configurar handler para console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)

        # Configurar formato
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Aplicar configurações
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        logger.setLevel(log_level)

    @property
    def servimed_credentials(self) -> Dict[str, str]:
        """Retorna credenciais do Servimed."""
        return {
            "username": os.getenv("SERVIMED_USERNAME"),
            "password": os.getenv("SERVIMED_PASSWORD"),
        }

    @property
    def oauth2(self) -> OAuth2Config:
        """Retorna configurações OAuth2."""
        return OAuth2Config.from_env()

    @property
    def api(self) -> APIConfig:
        """Retorna configurações da API."""
        return APIConfig.from_env()

    @property
    def scrapy(self) -> ScrapyConfig:
        """Retorna configurações do Scrapy."""
        return ScrapyConfig.from_env()

    @property
    def output(self) -> OutputConfig:
        """Retorna configurações de saída."""
        return OutputConfig.from_env()

    @property
    def log(self) -> LogConfig:
        """Retorna configurações de logging."""
        return LogConfig.from_env()

    @property
    def cache(self) -> CacheConfig:
        """Retorna configurações de cache."""
        return CacheConfig.from_env()

    @property
    def retry(self) -> RetryConfig:
        """Retorna configurações de retry."""
        return RetryConfig.from_env()

    def get_full_url(self, endpoint: str) -> str:
        """
        Constrói URL completa para um endpoint.

        Args:
            endpoint: Endpoint da API (ex: /oauth/token)

        Returns:
            URL completa (ex: https://desafio.cotefacil.net/oauth/token)
        """
        base_url = self.api.base_url.rstrip("/")
        endpoint = endpoint.lstrip("/")
        return f"{base_url}/{endpoint}"

    def to_dict(self) -> Dict[str, Any]:
        """Converte configurações para dicionário (para debug)."""
        return {
            "servimed_credentials": self.servimed_credentials,
            "oauth2": self.oauth2.__dict__,
            "api": self.api.__dict__,
            "scrapy": self.scrapy.__dict__,
            "output": self.output.__dict__,
            "log": self.log.__dict__,
            "cache": self.cache.__dict__,
            "retry": self.retry.__dict__,
        }

    def __str__(self) -> str:
        """Representação string das configurações (sem credenciais sensíveis)."""
        config_dict = self.to_dict()
        # Remover senhas para segurança
        if "servimed_credentials" in config_dict:
            config_dict["servimed_credentials"]["password"] = "***"
        return f"Config(api_base_url={self.api.base_url}, output_dir={self.output.directory})"


# Instância global de configuração
config = Config()


# Função de conveniência para importação
def get_config() -> Config:
    """Retorna instância global de configuração."""
    return config


if __name__ == "__main__":
    # Teste das configurações
    try:
        print("=== CONFIGURAÇÕES CARREGADAS ===")
        print(f"API Base URL: {config.api.base_url}")
        print(f"Output Directory: {config.output.directory}")
        print(f"Scrapy Log Level: {config.scrapy.log_level}")
        print(f"Cache Enabled: {config.cache.enabled}")
        print("=== CONFIGURAÇÃO VÁLIDA ===")
    except ConfigurationError as e:
        print(f"ERRO DE CONFIGURAÇÃO: {e}")
        exit(1)
