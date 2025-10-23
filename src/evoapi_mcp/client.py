"""Cliente HTTP direto para Evolution API."""

import sys
import re
import requests
from datetime import datetime, timedelta
from typing import Any
from pathlib import Path

# Adiciona o diretório src ao path para permitir importações
src_dir = Path(__file__).parent.parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from evoapi_mcp.config import EvolutionConfig


# Constantes de validação
VALID_MEDIA_TYPES = {"image", "video", "document", "audio"}
VALID_PRESENCE_STATUS = {"available", "unavailable", "composing", "recording"}
MAX_TEXT_LENGTH = 65536  # 64KB - limite do WhatsApp
MAX_CAPTION_LENGTH = 1024  # Limite de legenda


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
    """Cliente HTTP direto para Evolution API.

    Faz chamadas HTTP diretas à API REST seguindo a documentação oficial.
    Usa o header 'apikey' para autenticação e {instanceId} nos endpoints.
    """

    def __init__(self, config: EvolutionConfig):
        """Inicializa o cliente Evolution API.

        Args:
            config: Configuração da Evolution API
        """
        self.config = config
        self.base_url = config.base_url.rstrip('/')
        self.api_key = config.api_token
        self.instance_id = config.instance_name
        self.timeout = config.timeout

        # Headers padrão para todas as requisições
        self.headers = {
            'apikey': self.api_key,
            'Content-Type': 'application/json'
        }

        # Cache de nomes de contatos (número -> nome)
        self._contact_names_cache: dict[str, str | None] = {}
        self._cache_timestamp: datetime | None = None
        self._cache_ttl = timedelta(minutes=5)  # Cache expira após 5 minutos

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

    @staticmethod
    def validate_url(url: str, param_name: str = "url") -> None:
        """Valida se uma URL é válida.

        Args:
            url: URL a validar
            param_name: Nome do parâmetro (para mensagem de erro)

        Raises:
            ValueError: Se a URL for inválida
        """
        if not url or not isinstance(url, str):
            raise ValueError(f"{param_name} não pode ser vazio")

        if not url.startswith(("http://", "https://")):
            raise ValueError(
                f"{param_name} inválida: '{url}'. "
                "URL deve começar com http:// ou https://"
            )

    @staticmethod
    def validate_text_length(text: str, max_length: int, param_name: str = "text") -> None:
        """Valida o tamanho de um texto.

        Args:
            text: Texto a validar
            max_length: Tamanho máximo permitido
            param_name: Nome do parâmetro (para mensagem de erro)

        Raises:
            ValueError: Se o texto exceder o tamanho máximo
        """
        if len(text) > max_length:
            raise ValueError(
                f"{param_name} muito longo: {len(text)} caracteres. "
                f"Máximo permitido: {max_length} caracteres"
            )

    @staticmethod
    def validate_media_type(media_type: str) -> None:
        """Valida o tipo de mídia.

        Args:
            media_type: Tipo de mídia a validar

        Raises:
            ValueError: Se o tipo de mídia for inválido
        """
        if media_type not in VALID_MEDIA_TYPES:
            raise ValueError(
                f"media_type inválido: '{media_type}'. "
                f"Valores válidos: {', '.join(sorted(VALID_MEDIA_TYPES))}"
            )

    def _is_cache_expired(self) -> bool:
        """Verifica se o cache de contatos expirou.

        Returns:
            bool: True se o cache expirou ou nunca foi construído, False caso contrário
        """
        if not self._cache_timestamp:
            return True
        return datetime.now() - self._cache_timestamp > self._cache_ttl

    def clear_cache(self) -> None:
        """Limpa o cache de nomes de contatos.

        Este método é útil quando você quer forçar a atualização dos nomes
        dos contatos sem precisar reiniciar o cliente.

        Example:
            client.clear_cache()  # Cache será reconstruído na próxima chamada
        """
        self._contact_names_cache.clear()
        self._cache_timestamp = None
        self._log("Cache de contatos limpo")

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: dict | None = None,
        params: dict | None = None
    ) -> dict[str, Any]:
        """Faz uma requisição HTTP à API.

        Args:
            method: Método HTTP (GET, POST, PUT, DELETE)
            endpoint: Endpoint da API (ex: /chat/findChats/{instanceId})
            data: Dados do corpo da requisição (para POST/PUT)
            params: Parâmetros de query string (para GET)

        Returns:
            dict: Resposta JSON da API

        Raises:
            EvolutionAPIError: Se houver erro na requisição
        """
        # Substitui {instanceId} no endpoint
        endpoint = endpoint.replace('{instanceId}', self.instance_id)
        url = f"{self.base_url}{endpoint}"

        try:
            self._log(f"{method} {endpoint}")

            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data,
                params=params,
                timeout=self.timeout
            )

            # Verifica se a resposta foi bem-sucedida
            response.raise_for_status()

            # Tenta retornar JSON, se houver
            try:
                return response.json()
            except ValueError:
                return {"status": "success", "data": response.text}

        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP {e.response.status_code}: {e.response.text}"
            self._log(error_msg, "ERROR")

            # Detecta erros específicos
            if e.response.status_code == 401:
                raise EvolutionAPIError("Falha de autenticação. Verifique o EVOLUTION_API_TOKEN")
            elif e.response.status_code == 404:
                raise EvolutionAPIError(f"Endpoint não encontrado: {endpoint}")
            else:
                raise EvolutionAPIError(error_msg)

        except requests.exceptions.Timeout:
            raise EvolutionAPIError(
                f"Timeout ao executar {method} {endpoint}. "
                f"Tente novamente ou aumente EVOLUTION_TIMEOUT"
            )

        except requests.exceptions.ConnectionError as e:
            raise EvolutionAPIError(f"Erro de conexão: {str(e)}")

        except Exception as e:
            self._log(f"Erro inesperado: {str(e)}", "ERROR")
            raise EvolutionAPIError(f"Erro em {method} {endpoint}: {str(e)}")

    # =========================================================================
    # CHAT OPERATIONS
    # =========================================================================

    def find_chats(self, enrich_with_names: bool = True) -> dict[str, Any]:
        """Busca todas as conversas ativas.

        Endpoint: POST /chat/findChats/{instanceId}

        Args:
            enrich_with_names: Se True, enriquece conversas com nomes dos contatos quando pushName for null

        Returns:
            dict: Lista de conversas com informações detalhadas

        Raises:
            EvolutionAPIError: Se houver erro na requisição
        """
        self._log("Buscando conversas")
        chats = self._make_request("POST", "/chat/findChats/{instanceId}", data={})

        # Enriquece com nomes de contatos se solicitado
        if enrich_with_names and isinstance(chats, list):
            self._log("Enriquecendo conversas com nomes de contatos")

            # OTIMIZAÇÃO: Busca TODOS os contatos de uma vez ao invés de um por um
            contacts_map = self._build_contacts_map()

            for chat in chats:
                if chat.get("pushName") is None and chat.get("remoteJid"):
                    # Extrai o número do remoteJid
                    remote_jid = chat["remoteJid"]
                    # Ignora grupos (terminam com @g.us)
                    if not remote_jid.endswith("@g.us"):
                        number = remote_jid.replace("@s.whatsapp.net", "")
                        # Lookup local (muito mais rápido que HTTP)
                        clean_number = re.sub(r'\D', '', number)
                        if clean_number in contacts_map:
                            chat["pushName"] = contacts_map[clean_number]
                            chat["_enriched"] = True

        return chats

    def _build_contacts_map(self) -> dict[str, str]:
        """Constrói um mapa de número -> nome a partir de todos os contatos.

        Usa cache com TTL de 5 minutos. Se o cache expirou, reconstrói o mapa.

        Returns:
            dict: Mapeamento de número limpo para nome do contato
        """
        # Se cache não expirou, retorna cache existente
        if not self._is_cache_expired() and self._contact_names_cache:
            self._log("Usando cache de contatos existente")
            return self._contact_names_cache

        try:
            # Cache expirou ou está vazio - reconstrói
            self._log("Reconstruindo cache de contatos...")

            # Busca todos os contatos de uma vez (retorna lista direta)
            contact_list = self.fetch_contacts()
            contacts_map = {}

            for contact in contact_list:
                # Extrai número do remoteJid (formato: 5511999999999@s.whatsapp.net)
                remote_jid = contact.get("remoteJid", "")
                # Ignora grupos (terminam com @g.us)
                if remote_jid.endswith("@g.us"):
                    continue

                number = remote_jid.replace("@s.whatsapp.net", "")
                clean_number = re.sub(r'\D', '', number)

                # Pega o pushName
                name = contact.get("pushName")
                if clean_number and name:
                    contacts_map[clean_number] = name

            # Atualiza cache e timestamp
            self._contact_names_cache = contacts_map
            self._cache_timestamp = datetime.now()

            self._log(f"Cache de contatos atualizado: {len(contacts_map)} contatos")
            return contacts_map

        except Exception as e:
            self._log(f"Erro ao construir mapa de contatos: {e}", "WARNING")
            return {}

    def find_messages(
        self,
        query: str | None = None,
        chat_id: str | None = None,
        limit: int = 50
    ) -> dict[str, Any]:
        """Busca mensagens de uma conversa.

        Endpoint: POST /chat/findMessages/{instanceId}

        Args:
            query: Termo de busca nas mensagens (opcional)
            chat_id: ID do chat específico (ex: 5511999999999@s.whatsapp.net)
            limit: Número máximo de mensagens a retornar

        Returns:
            dict: Lista de mensagens

        Raises:
            EvolutionAPIError: Se houver erro na requisição
        """
        self._log(f"Buscando mensagens (limit={limit})")

        payload = {}
        if query:
            payload["query"] = query
        if chat_id:
            payload["chatId"] = chat_id
        if limit:
            payload["limit"] = limit

        return self._make_request(
            "POST",
            "/chat/findMessages/{instanceId}",
            data=payload
        )

    def get_messages_by_number(
        self,
        number: str,
        limit: int = 50
    ) -> dict[str, Any]:
        """Obtém mensagens de uma conversa por número.

        Args:
            number: Número de telefone
            limit: Número máximo de mensagens

        Returns:
            dict: Mensagens da conversa

        Raises:
            InvalidPhoneNumberError: Se o número for inválido
            EvolutionAPIError: Se houver erro
        """
        clean_number = self.validate_phone_number(number)
        chat_id = f"{clean_number}@s.whatsapp.net"

        return self.find_messages(chat_id=chat_id, limit=limit)

    def fetch_contacts(self, contact_id: str | None = None) -> list[dict[str, Any]]:
        """Busca contatos salvos no WhatsApp com filtros opcionais.

        Endpoint: POST /chat/findContacts/{instanceId}

        Args:
            contact_id: ID do contato específico (ex: 5511999999999@s.whatsapp.net).
                       Se None, retorna todos os contatos.

        Returns:
            list: Lista de contatos com informações completas:
                  - remoteJid: ID do contato
                  - pushName: Nome do contato
                  - isGroup: Se é grupo ou contato individual
                  - profilePicUrl: URL da foto de perfil

        Raises:
            EvolutionAPIError: Se houver erro na requisição

        Example:
            # Buscar todos os contatos
            all_contacts = client.fetch_contacts()

            # Buscar contato específico
            contact = client.fetch_contacts(contact_id="5511999999999@s.whatsapp.net")
        """
        self._log(f"Buscando contatos{' (filtrado)' if contact_id else ''}")

        payload = {}
        if contact_id:
            payload["where"] = {"id": contact_id}

        result = self._make_request(
            "POST",
            "/chat/findContacts/{instanceId}",
            data=payload
        )

        # A API retorna uma lista diretamente, não um objeto com "data"
        if not isinstance(result, list):
            self._log(f"Formato inesperado de resposta: {type(result)}", "WARNING")
            return []

        return result

    def get_contact_name(self, number: str, use_cache: bool = True) -> str | None:
        """Busca o nome de um contato por número.

        Args:
            number: Número de telefone
            use_cache: Se deve usar cache de nomes (padrão: True)

        Returns:
            str | None: Nome do contato ou None se não encontrado

        Raises:
            EvolutionAPIError: Se houver erro
        """
        try:
            clean_number = self.validate_phone_number(number)

            # Verifica cache primeiro (se não expirou)
            if use_cache and not self._is_cache_expired() and clean_number in self._contact_names_cache:
                return self._contact_names_cache[clean_number]

            contact_id = f"{clean_number}@s.whatsapp.net"

            # Tenta buscar contato específico com filtro (retorna lista direta)
            contact_list = self.fetch_contacts(contact_id=contact_id)

            name = None
            if contact_list and len(contact_list) > 0:
                contact = contact_list[0]
                # Retorna pushName
                name = contact.get("pushName")

            # Salva no cache e atualiza timestamp
            if use_cache:
                self._contact_names_cache[clean_number] = name
                if not self._cache_timestamp:
                    self._cache_timestamp = datetime.now()

            return name

        except Exception as e:
            self._log(f"Erro ao buscar nome do contato: {e}", "WARNING")
            return None

    # =========================================================================
    # MESSAGE SENDING
    # =========================================================================

    def send_text(
        self,
        number: str,
        text: str,
        link_preview: bool = True
    ) -> dict[str, Any]:
        """Envia uma mensagem de texto.

        Endpoint: POST /message/sendText/{instanceId}

        Args:
            number: Número de telefone no formato internacional
            text: Texto da mensagem (máximo 65536 caracteres)
            link_preview: Se deve mostrar preview de links

        Returns:
            dict: Resposta da API

        Raises:
            InvalidPhoneNumberError: Se o número for inválido
            ValueError: Se o texto exceder o tamanho máximo
            EvolutionAPIError: Erros da API
        """
        # Validações
        clean_number = self.validate_phone_number(number)
        self.validate_text_length(text, MAX_TEXT_LENGTH, "text")

        self._log(f"Enviando mensagem de texto para {clean_number}")

        payload = {
            "number": clean_number,
            "text": text,
            "linkPreview": link_preview
        }

        return self._make_request(
            "POST",
            "/message/sendText/{instanceId}",
            data=payload
        )

    def send_media(
        self,
        number: str,
        media_url: str,
        media_type: str,
        caption: str | None = None,
        filename: str | None = None
    ) -> dict[str, Any]:
        """Envia mídia (imagem, vídeo, documento, áudio).

        Endpoint: POST /message/sendMedia/{instanceId}

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
            ValueError: Se media_type, URL ou caption forem inválidos
            EvolutionAPIError: Erros da API
        """
        # Validações
        clean_number = self.validate_phone_number(number)
        self.validate_media_type(media_type)
        self.validate_url(media_url, "media_url")
        if caption:
            self.validate_text_length(caption, MAX_CAPTION_LENGTH, "caption")

        self._log(f"Enviando {media_type} para {clean_number}")

        payload = {
            "number": clean_number,
            "mediatype": media_type,
            "media": media_url
        }

        if caption:
            payload["caption"] = caption
        if filename:
            payload["fileName"] = filename

        return self._make_request(
            "POST",
            "/message/sendMedia/{instanceId}",
            data=payload
        )

    # =========================================================================
    # INSTANCE OPERATIONS
    # =========================================================================

    def get_connection_state(self) -> dict[str, Any]:
        """Obtém o estado da conexão da instância.

        Endpoint: GET /instance/connectionState/{instanceId}

        Returns:
            dict: Estado da conexão

        Raises:
            EvolutionAPIError: Se houver erro ao consultar o estado
        """
        self._log("Consultando estado da conexão")

        response = self._make_request(
            "GET",
            "/instance/connectionState/{instanceId}"
        )

        state = response.get('state', 'unknown')
        self._log(f"Estado da conexão: {state}")

        return response

    def set_presence(
        self,
        status: str,
        number: str | None = None
    ) -> dict[str, Any]:
        """Define presença.

        Endpoint: POST /chat/presenceUpdate/{instanceId}

        Args:
            status: Status (available, unavailable, composing, recording)
            number: Número para enviar presença (opcional)

        Returns:
            dict: Resposta

        Raises:
            EvolutionAPIError: Se houver erro
        """
        self._log(f"Definindo presença como '{status}'")

        payload = {
            "presence": status
        }

        if number:
            clean_number = self.validate_phone_number(number)
            payload["number"] = clean_number

        return self._make_request(
            "POST",
            "/chat/presenceUpdate/{instanceId}",
            data=payload
        )

    def get_instance_info(self) -> dict[str, Any]:
        """Obtém informações detalhadas da instância.

        Returns:
            dict: Informações da instância

        Raises:
            EvolutionAPIError: Se houver erro ao consultar
        """
        self._log("Consultando informações da instância")

        # Usa get_connection_state que retorna info da instância
        response = self.get_connection_state()

        return {
            "instance_name": self.instance_id,
            "status": response.get("state", "unknown"),
            "info": response
        }
