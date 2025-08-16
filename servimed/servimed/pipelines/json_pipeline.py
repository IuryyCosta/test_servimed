
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from scrapy import signals
from scrapy.exceptions import DropItem

from config import get_config


class JsonPipeline:
    """
    Pipeline para salvar produtos em arquivo JSON.

    Organiza os dados por data/hora e mantém estrutura limpa.
    """

    def __init__(self):
        """Inicializa o pipeline com configurações."""
        self.config = get_config()
        self.output_dir = Path(self.config.output.directory)
        self.filename_prefix = self.config.output.filename_prefix

        # Criar diretório de saída se não existir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Contador de itens processados
        self.item_count = 0

    @classmethod
    def from_crawler(cls, crawler):
        """Método de classe para criar instância do pipeline."""
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signal=signals.spider_closed)
        return pipeline

    def spider_opened(self, spider):
        """Chamado quando o spider é aberto."""
        spider.logger.info(
            f"Pipeline JSON iniciado. Diretório de saída: {self.output_dir}"
        )

    def spider_closed(self, spider):
        """Chamado quando o spider é fechado."""
        spider.logger.info(
            f"Pipeline JSON finalizado. Total de itens processados: {self.item_count}"
        )

    def process_item(self, item: Any, spider) -> Any:
        """
        Processa cada item extraído.

        Args:
            item: Item extraído pelo spider
            spider: Spider que extraiu o item

        Returns:
            Item processado ou DropItem se inválido
        """
        try:
            # Validar item
            if not self._is_valid_item(item):
                spider.logger.warning(f"Item inválido ignorado: {item}")
                raise DropItem("Item inválido")

            # Incrementar contador
            self.item_count += 1

            # Log do processamento
            if self.item_count % 100 == 0:
                spider.logger.info(f"Processados {self.item_count} itens")

            return item

        except Exception as e:
            spider.logger.error(f"Erro ao processar item: {e}")
            raise DropItem(f"Erro no pipeline: {e}")

    def _is_valid_item(self, item: Any) -> bool:
        """
        Valida se o item é válido para processamento.

        Args:
            item: Item a ser validado

        Returns:
            True se válido, False caso contrário
        """
        # Verificar se é um dict ou tem método to_dict
        if isinstance(item, dict):
            return True
        elif hasattr(item, "to_dict"):
            return True
        else:
            return False

    def _get_output_filename(self) -> str:
        """
        Gera nome do arquivo de saída com timestamp.

        Returns:
            Nome do arquivo com timestamp
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{self.filename_prefix}_{timestamp}.json"

    def _save_to_json(self, data: list, filename: str):
        """
        Salva dados em arquivo JSON.

        Args:
            data: Lista de dados para salvar
            filename: Nome do arquivo
        """
        filepath = self.output_dir / filename

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            print(f"✅ Dados salvos em: {filepath}")

        except Exception as e:
            print(f"❌ Erro ao salvar arquivo {filepath}: {e}")
            raise
