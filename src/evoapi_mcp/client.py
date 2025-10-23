"""Wrapper do cliente Evolution API."""

import sys
import re
from typing import Any
from pathlib import Path
from evolutionapi.client import EvolutionClient as BaseEvolutionClient
from evolutionapi.models.message import TextMessage

# Adiciona o diretório src ao path para permitir importações
src_dir = Path(__file__).parent.parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from evoapi_mcp.config import EvolutionConfig


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
        self.instance_id = config.instance_name
        self.instance_token = config.api_token  # Na v0.1.2, o token é usado tanto como global quanto como instance

        # Inicializa o cliente base da Evolution API
        self._client = BaseEvolutionClient(
            base_url=config.base_url,
            api_token=config.api_token
        )

        self._log(f"Cliente inicializado para instância '{self.instance_id}'")

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
                f"Instância '{self.instance_id}' está desconectada. "
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
        link_preview: bool = True
    ) -> dict[str, Any]:
        """Envia uma mensagem de texto.

        Args:
            number: Número de telefone no formato internacional
            text: Texto da mensagem
            link_preview: Se deve mostrar preview de links

        Returns:
            dict: Resposta da API

        Raises:
            InvalidPhoneNumberError: Se o número for inválido
            EvolutionAPIError: Erros da API
        """
        try:
            # Valida e normaliza o número
            clean_number = self.validate_phone_number(number)

            self._log(f"Enviando mensagem de texto para {clean_number}")

            # Cria o objeto TextMessage
            message = TextMessage(
                number=clean_number,
                text=text,
                linkPreview=link_preview
            )

            # Chama a API
            response = self._client.messages.send_text(
                instance_id=self.instance_id,
                message=message,
                instance_token=self.instance_token
            )

            self._log(f"Mensagem enviada com sucesso")
            return response

        except (InvalidPhoneNumberError, InstanceDisconnectedError, EvolutionAPIError):
            raise
        except Exception as e:
            self._handle_error(e, "send_text")

    def get_connection_state(self) -> dict[str, Any]:
        """Obtém o estado da conexão da instância.

        Returns:
            dict: Estado da conexão

        Raises:
            EvolutionAPIError: Se houver erro ao consultar o estado
        """
        try:
            self._log(f"Consultando estado da conexão")

            response = self._client.instance_operations.get_connection_state(
                instance_id=self.instance_id,
                instance_token=self.instance_token
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

            # A API evolutionapi usa send_media para todos os tipos
            from evolutionapi.models.message import MediaMessage

            media_message = MediaMessage(
                number=clean_number,
                media=media_url,
                caption=caption,
                fileName=filename if filename else None
            )

            response = self._client.messages.send_media(
                instance_id=self.instance_id,
                message=media_message,
                instance_token=self.instance_token
            )

            self._log(f"Mídia enviada com sucesso")
            return response

        except (InvalidPhoneNumberError, EvolutionAPIError):
            raise
        except Exception as e:
            self._handle_error(e, f"send_media ({media_type})")

    def get_messages(
        self,
        number: str,
        limit: int = 50
    ) -> dict[str, Any]:
        """Obtém mensagens de uma conversa.

        Args:
            number: Número de telefone
            limit: Número máximo de mensagens

        Returns:
            dict: Mensagens da conversa

        Raises:
            EvolutionAPIError: Se houver erro
        """
        try:
            clean_number = self.validate_phone_number(number)
            # Formato de chat_id do WhatsApp
            remote_jid = f"{clean_number}@s.whatsapp.net"

            self._log(f"Obtendo mensagens de {clean_number}")

            response = self._client.chat.get_messages(
                instance_id=self.instance_id,
                instance_token=self.instance_token,
                remote_jid=remote_jid,
                limit=limit
            )

            return response

        except Exception as e:
            self._handle_error(e, "get_messages")

    def set_presence(
        self,
        status: str,
        number: str | None = None
    ) -> dict[str, Any]:
        """Define presença.

        Args:
            status: Status (available, unavailable, composing, recording)
            number: Número para enviar presença (opcional)

        Returns:
            dict: Resposta

        Raises:
            EvolutionAPIError: Se houver erro
        """
        try:
            self._log(f"Definindo presença como '{status}'")

            response = self._client.chat.send_presence(
                instance_id=self.instance_id,
                instance_token=self.instance_token,
                number=number if number else "",
                presence=status,
                delay=0
            )

            return response

        except Exception as e:
            self._handle_error(e, "set_presence")

    def get_instance_info(self) -> dict[str, Any]:
        """Obtém informações detalhadas da instância.

        Returns:
            dict: Informações da instância

        Raises:
            EvolutionAPIError: Se houver erro ao consultar
        """
        try:
            self._log("Consultando informações da instância")

            # Usa get_connection_state que retorna info da instância
            response = self.get_connection_state()

            return {
                "instance_name": self.instance_id,
                "status": response.get("state", "unknown"),
                "info": response
            }

        except Exception as e:
            self._handle_error(e, "get_instance_info")
