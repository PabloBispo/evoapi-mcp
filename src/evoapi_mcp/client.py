"""Wrapper do cliente Evolution API."""

import sys
import re
from typing import Any
from evolutionapi.client import EvolutionClient as BaseEvolutionClient
from .config import EvolutionConfig


class EvolutionAPIError(Exception):
    """Erro base para operações da Evolution API."""
    pass


class InstanceDisconnectedError(EvolutionAPIError):
    """Erro quando a instância não está conectada."""
    pass


class InvalidPhoneNumberError(EvolutionAPIError):
    """Erro quando o número de telefone é inválido."""
    pass


class EvolutionClient:
    """Wrapper do cliente Evolution API com funcionalidades extras.

    Este wrapper adiciona:
    - Validação de números de telefone
    - Tratamento de erros padronizado
    - Logging adequado (stderr)
    - Gerenciamento automático da instância
    """

    def __init__(self, config: EvolutionConfig):
        """Inicializa o cliente Evolution API.

        Args:
            config: Configuração da Evolution API
        """
        self.config = config
        self.instance_name = config.instance_name

        # Inicializa o cliente base da Evolution API
        self._client = BaseEvolutionClient(
            base_url=config.base_url,
            api_token=config.api_token
        )

        self._log(f"Cliente inicializado para instância '{self.instance_name}'")

    def _log(self, message: str, level: str = "INFO") -> None:
        """Registra uma mensagem no stderr.

        Args:
            message: Mensagem a ser registrada
            level: Nível do log (INFO, WARNING, ERROR)
        """
        print(f"[{level}] Evolution API: {message}", file=sys.stderr)

    @staticmethod
    def validate_phone_number(number: str) -> str:
        """Valida e normaliza um número de telefone.

        O número deve estar no formato internacional sem '+' ou espaços.
        Exemplo: 5511999999999 (Brasil)

        Args:
            number: Número de telefone a validar

        Returns:
            str: Número normalizado

        Raises:
            InvalidPhoneNumberError: Se o número for inválido
        """
        # Remove caracteres não numéricos
        clean_number = re.sub(r'\D', '', number)

        # Valida formato básico (mínimo 10 dígitos, máximo 15)
        if not re.match(r'^\d{10,15}$', clean_number):
            raise InvalidPhoneNumberError(
                f"Número inválido: '{number}'. "
                "Use formato internacional sem '+' (ex: 5511999999999)"
            )

        return clean_number

    def _handle_error(self, error: Exception, context: str) -> None:
        """Trata erros de forma padronizada.

        Args:
            error: Exceção capturada
            context: Contexto da operação (para mensagem de erro)

        Raises:
            EvolutionAPIError: Erro tratado com mensagem descritiva
        """
        error_msg = str(error)
        self._log(f"Erro em {context}: {error_msg}", "ERROR")

        # Detecta erros comuns e lança exceções específicas
        if "not connected" in error_msg.lower() or "disconnected" in error_msg.lower():
            raise InstanceDisconnectedError(
                f"Instância '{self.instance_name}' está desconectada. "
                "Verifique a conexão com get_connection_status()"
            )

        if "unauthorized" in error_msg.lower() or "invalid token" in error_msg.lower():
            raise EvolutionAPIError(
                f"Falha de autenticação. Verifique o EVOLUTION_API_TOKEN"
            )

        if "timeout" in error_msg.lower():
            raise EvolutionAPIError(
                f"Timeout ao executar {context}. "
                f"Tente novamente ou aumente EVOLUTION_TIMEOUT"
            )

        # Erro genérico
        raise EvolutionAPIError(f"Erro em {context}: {error_msg}")

    def send_text(
        self,
        number: str,
        text: str,
        mentions: list[str] | None = None,
        link_preview: bool = True
    ) -> dict[str, Any]:
        """Envia uma mensagem de texto.

        Args:
            number: Número de telefone no formato internacional
            text: Texto da mensagem
            mentions: Lista de números a mencionar (opcional)
            link_preview: Se deve mostrar preview de links

        Returns:
            dict: Resposta da API com message_id, status, etc.

        Raises:
            InvalidPhoneNumberError: Se o número for inválido
            InstanceDisconnectedError: Se a instância estiver desconectada
            EvolutionAPIError: Outros erros da API
        """
        try:
            # Valida e normaliza o número
            clean_number = self.validate_phone_number(number)

            self._log(f"Enviando mensagem de texto para {clean_number}")

            # Chama a API
            response = self._client.messages.send_text(
                instance=self.instance_name,
                number=clean_number,
                text=text,
                # TODO: Adicionar suporte a mentions e link_preview quando disponível na lib
            )

            self._log(f"Mensagem enviada com sucesso: {response.get('message_id', 'N/A')}")
            return response

        except (InvalidPhoneNumberError, InstanceDisconnectedError, EvolutionAPIError):
            raise
        except Exception as e:
            self._handle_error(e, "send_text")

    def get_connection_state(self) -> dict[str, Any]:
        """Obtém o estado da conexão da instância.

        Returns:
            dict: Estado da conexão (state, qrcode se disponível, etc.)

        Raises:
            EvolutionAPIError: Se houver erro ao consultar o estado
        """
        try:
            self._log(f"Consultando estado da conexão")

            response = self._client.instance.get_connection_state(
                instance=self.instance_name
            )

            state = response.get('state', 'unknown')
            self._log(f"Estado da conexão: {state}")

            return response

        except Exception as e:
            self._handle_error(e, "get_connection_state")

    def send_media(
        self,
        number: str,
        media_url: str,
        media_type: str,
        caption: str | None = None,
        filename: str | None = None
    ) -> dict[str, Any]:
        """Envia mídia (imagem, vídeo, documento, áudio).

        Args:
            number: Número de telefone no formato internacional
            media_url: URL da mídia a enviar
            media_type: Tipo de mídia (image, video, document, audio)
            caption: Legenda da mídia (opcional)
            filename: Nome do arquivo para documentos (opcional)

        Returns:
            dict: Resposta da API

        Raises:
            InvalidPhoneNumberError: Se o número for inválido
            EvolutionAPIError: Erros da API
        """
        try:
            clean_number = self.validate_phone_number(number)

            self._log(f"Enviando {media_type} para {clean_number}")

            # TODO: Implementar após verificar API exata da evolutionapi
            # Por enquanto, método placeholder
            response = self._client.messages.send_media(
                instance=self.instance_name,
                number=clean_number,
                media_url=media_url,
                media_type=media_type,
                caption=caption,
                filename=filename
            )

            self._log(f"Mídia enviada com sucesso")
            return response

        except (InvalidPhoneNumberError, EvolutionAPIError):
            raise
        except Exception as e:
            self._handle_error(e, f"send_media ({media_type})")

    def get_instance_info(self) -> dict[str, Any]:
        """Obtém informações detalhadas da instância.

        Returns:
            dict: Informações da instância (nome, número conectado, status, etc.)

        Raises:
            EvolutionAPIError: Se houver erro ao consultar
        """
        try:
            self._log("Consultando informações da instância")

            # TODO: Verificar método correto na lib
            response = self._client.instance.get_instance(
                instance=self.instance_name
            )

            return response

        except Exception as e:
            self._handle_error(e, "get_instance_info")
