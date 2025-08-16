# Importar configurações do projeto
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config import get_config

    config = get_config()
except ImportError:
    # Fallback se config.py não estiver disponível
    config = None

BOT_NAME = "servimed"

SPIDER_MODULES = ["servimed.spiders"]
NEWSPIDER_MODULE = "servimed.spiders"

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Concurrency and throttling settings
CONCURRENT_REQUESTS_PER_DOMAIN = 1
DOWNLOAD_DELAY = 1

# Configurações de performance integradas com config.py
if config:
    # Configurações de concorrência
    CONCURRENT_REQUESTS = config.scrapy.concurrent_requests
    DOWNLOAD_DELAY = config.scrapy.download_delay
    DOWNLOAD_TIMEOUT = config.scrapy.download_timeout

    # Configurações de logging
    LOG_LEVEL = config.scrapy.log_level
    LOG_FILE = config.log.file if config.log else None
else:
    # Valores padrão se config.py não estiver disponível
    CONCURRENT_REQUESTS = 16
    DOWNLOAD_DELAY = 1
    DOWNLOAD_TIMEOUT = 30
    LOG_LEVEL = "INFO"

# Headers para APIs
DEFAULT_REQUEST_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "User-Agent": "Servimed-Scrapy/1.0 (+https://github.com/servimed)",
    "Connection": "keep-alive",
}

# Configurações de retry e cache
RETRY_ENABLED = True
RETRY_TIMES = config.retry.max_attempts if config else 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]

# Cache HTTP
HTTPCACHE_ENABLED = config.cache.enabled if config else False
HTTPCACHE_EXPIRATION_SECS = config.cache.ttl if config else 1800
HTTPCACHE_DIR = "httpcache"
HTTPCACHE_IGNORE_HTTP_CODES = [400, 401, 403, 404, 500, 502, 503, 504]

# Pipelines habilitados
ITEM_PIPELINES = {
    "servimed.pipelines.json_pipeline.JsonPipeline": 300,
}

# Configurações de segurança e desenvolvimento
COOKIES_ENABLED = False  # Desabilitar cookies para APIs
TELNETCONSOLE_ENABLED = False  # Desabilitar console Telnet
DOWNLOAD_WARNSIZE = 0  # Sem limite de tamanho para downloads

# Configurações de desenvolvimento
if config and config.scrapy.log_level == "DEBUG":
    LOG_LEVEL = "DEBUG"
    LOG_STDOUT = True
    TELNETCONSOLE_ENABLED = True

# Configurações de saída
FEED_EXPORT_ENCODING = "utf-8"
FEEDS = (
    {
        "%(output_directory)s/%(filename_prefix)s_%(time)s.json": {
            "format": "json",
            "encoding": "utf8",
            "indent": 2,
            "overwrite": False,
        }
    }
    if config
    else {}
)

# Configurações de middleware (desabilitados por padrão)
SPIDER_MIDDLEWARES = {}
DOWNLOADER_MIDDLEWARES = {}

# Extensões desabilitadas para simplificar
EXTENSIONS = {
    "scrapy.extensions.telnet.TelnetConsole": None,
}
