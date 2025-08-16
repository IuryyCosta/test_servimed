import json
import logging
import urllib.parse
from typing import Dict, Any, Optional

import scrapy
from scrapy.http import Request, Response
from scrapy.exceptions import CloseSpider

from ..config import get_config
from ..models.product import Product
from ..models.auth import AuthCredentials, AuthToken, AuthResponse


class ServimedApiSpider(scrapy.Spider):
    """
    Spider para extração de produtos via API Servimed.

    Implementa fluxo completo de autenticação OAuth2 e consumo
    da API de produtos com tratamento robusto de erros.
    """

    name = "servimed_api"
    allowed_domains = ["desafio.cotefacil.net"]

    def __init__(self, *args, **kwargs):
        """Inicializa o spider com configurações."""
        super().__init__(*args, **kwargs)

        # Configurações do projeto
        self.config = get_config()

        # URLs das APIs
        self.base_url = self.config.api.base_url
        self.token_url = f"{self.base_url}{self.config.api.token_endpoint}"
        self.products_url = f"{self.base_url}{self.config.api.products_endpoint}"

        # Credenciais
        self.credentials = AuthCredentials(
            username=self.config.servimed_credentials["username"],
            password=self.config.servimed_credentials["password"],
        )

        # Token de acesso
        self.access_token: Optional[str] = None

        # Logger já disponível via Scrapy (self.logger)

        self.logger.info("Spider ServimedApi inicializado")
        self.logger.info(f"Base URL: {self.base_url}")
        self.logger.info(f"Token URL: {self.token_url}")
        self.logger.info(f"Products URL: {self.products_url}")

    def start_requests(self):
        """
        Inicia o fluxo de autenticação.

        Primeiro faz login para obter token, depois chama
        o método para extrair produtos.
        """
        self.logger.info("Iniciando fluxo de autenticação...")

        # Dados para autenticação
        auth_data = {
            "grant_type": "password",
            "username": self.credentials.username,
            "password": self.credentials.password,
            "scope": "",
            "client_id": "string",
            "client_secret": "********",
        }

        # Headers para autenticação
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }

        # Request de autenticação
        yield Request(
            url=self.token_url,
            method="POST",
            headers=headers,
            body=urllib.parse.urlencode(auth_data),
            callback=self.parse_auth_response,
            errback=self.handle_auth_error,
            meta={"dont_cache": True},
        )

    def parse_auth_response(self, response: Response):
        """
        Processa resposta de autenticação.

        Extrai token de acesso e inicia extração de produtos.
        """
        try:
            self.logger.info("Processando resposta de autenticação...")

            # Verificar status da resposta
            if response.status != 200:
                self.logger.error(f"Erro na autenticação: Status {response.status}")
                raise CloseSpider(f"Falha na autenticação: Status {response.status}")

            # Parsear resposta JSON
            auth_data = json.loads(response.text)
            self.logger.info("Resposta de autenticação recebida")

            # Validar estrutura da resposta
            if "access_token" not in auth_data:
                self.logger.error("Token de acesso não encontrado na resposta")
                raise CloseSpider("Token de acesso não encontrado")

            # Extrair token
            self.access_token = auth_data["access_token"]
            token_type = auth_data.get("token_type", "Bearer")
            expires_in = auth_data.get("expires_in", 1800)

            self.logger.info(f"Token obtido com sucesso")
            self.logger.info(f"Tipo: {token_type}")
            self.logger.info(f"Expira em: {expires_in} segundos")

            # Iniciar extração de produtos
            yield self.create_products_request()

        except json.JSONDecodeError as e:
            self.logger.error(f"Erro ao decodificar resposta JSON: {e}")
            raise CloseSpider(f"Resposta de autenticação inválida: {e}")
        except Exception as e:
            self.logger.error(f"Erro inesperado na autenticação: {e}")
            raise CloseSpider(f"Erro na autenticação: {e}")

    def create_products_request(self) -> Request:
        """
        Cria request para extrair produtos.

        Configura headers de autorização e callback.
        """
        self.logger.info("Criando request para extração de produtos...")

        # Headers com autorização
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.access_token}",
        }

        # Request para produtos
        return Request(
            url=self.products_url,
            method="GET",
            headers=headers,
            callback=self.parse_products,
            errback=self.handle_products_error,
            meta={"dont_cache": True},
        )

    def parse_products(self, response: Response):
        """
        Processa resposta da API de produtos.

        Extrai cada produto e o envia para o pipeline.
        """
        try:
            self.logger.info("Processando produtos da API...")

            # Verificar status da resposta
            if response.status != 200:
                self.logger.error(f"Erro na API de produtos: Status {response.status}")
                raise CloseSpider(f"Falha na API de produtos: Status {response.status}")

            # Parsear resposta JSON
            products_data = json.loads(response.text)
            self.logger.info("Dados de produtos recebidos")

            # Verificar se é uma lista
            if not isinstance(products_data, list):
                self.logger.error("Resposta não é uma lista de produtos")
                raise CloseSpider("Formato de resposta inválido")

            self.logger.info(f"Total de produtos encontrados: {len(products_data)}")

            # Processar cada produto
            for product_data in products_data:
                try:
                    # Criar modelo de produto
                    product = Product(**product_data)

                    # Log do produto
                    self.logger.debug(f"Produto processado: {product}")

                    # Enviar para o pipeline
                    yield product.to_dict()

                except Exception as e:
                    self.logger.warning(
                        f"Erro ao processar produto {product_data.get('id', 'N/A')}: {e}"
                    )
                    continue

            self.logger.info("Processamento de produtos concluído")

        except json.JSONDecodeError as e:
            self.logger.error(f"Erro ao decodificar resposta JSON: {e}")
            raise CloseSpider(f"Resposta de produtos inválida: {e}")
        except Exception as e:
            self.logger.error(f"Erro inesperado no processamento: {e}")
            raise CloseSpider(f"Erro no processamento: {e}")

    def handle_auth_error(self, failure):
        """
        Trata erros de autenticação.

        Loga erro e encerra o spider.
        """
        self.logger.error(f"Erro na requisição de autenticação: {failure.value}")
        raise CloseSpider(f"Falha na requisição de autenticação: {failure.value}")

    def handle_products_error(self, failure):
        """
        Trata erros na API de produtos.

        Loga erro e encerra o spider.
        """
        self.logger.error(f"Erro na requisição de produtos: {failure.value}")
        raise CloseSpider(f"Falha na requisição de produtos: {failure.value}")

    def closed(self, reason):
        """
        Chamado quando o spider é fechado.

        Loga informações finais do processamento.
        """
        self.logger.info(f"Spider fechado. Motivo: {reason}")

        if reason == "finished":
            self.logger.info("✅ Processamento concluído com sucesso!")
        else:
            self.logger.warning(f"⚠️ Spider encerrado: {reason}")
