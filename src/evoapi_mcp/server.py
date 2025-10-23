"""MCP Server para Evolution API."""

import sys
from mcp.server.fastmcp import FastMCP
from .config import load_config
from .client import EvolutionClient

# Inicializa o MCP server
mcp = FastMCP("Evolution API")

# Carrega configuração e inicializa cliente
try:
    config = load_config()
    client = EvolutionClient(config)
except Exception as e:
    print(f"Falha ao inicializar o servidor: {e}", file=sys.stderr)
    sys.exit(1)


# ============================================================================
# TOOLS - Envio de Mensagens
# ============================================================================

@mcp.tool()
def send_text_message(
    number: str,
    text: str,
    link_preview: bool = True
) -> dict:
    """Envia uma mensagem de texto para um número WhatsApp.

    Args:
        number: Número no formato internacional sem '+' (ex: 5511999999999)
        text: Texto da mensagem a ser enviada
        link_preview: Se deve mostrar preview de links (padrão: True)

    Returns:
        dict: Resposta com message_id, status e timestamp da mensagem enviada

    Raises:
        InvalidPhoneNumberError: Se o número for inválido
        InstanceDisconnectedError: Se a instância estiver desconectada
        EvolutionAPIError: Outros erros da API

    Example:
        send_text_message(
            number="5511999999999",
            text="Olá! Esta é uma mensagem de teste."
        )
    """
    return client.send_text(
        number=number,
        text=text,
        link_preview=link_preview
    )


@mcp.tool()
def get_connection_status() -> dict:
    """Verifica o status da conexão da instância WhatsApp.

    Returns:
        dict: Estado da conexão contendo:
            - state: Estado atual (open, close, connecting, etc.)
            - instance: Nome da instância
            - qrcode: QR code se disponível (estado 'connecting')

    Raises:
        EvolutionAPIError: Se houver erro ao consultar o status

    Example:
        status = get_connection_status()
        # Verifica se está conectado
        if status['state'] == 'open':
            print("WhatsApp conectado!")
    """
    return client.get_connection_state()


@mcp.tool()
def send_image(
    number: str,
    image_url: str,
    caption: str | None = None
) -> dict:
    """Envia uma imagem para um número WhatsApp.

    Args:
        number: Número no formato internacional sem '+' (ex: 5511999999999)
        image_url: URL pública da imagem (jpg, png, etc.)
        caption: Legenda da imagem (opcional)

    Returns:
        dict: Resposta com message_id, status e timestamp

    Raises:
        InvalidPhoneNumberError: Se o número for inválido
        EvolutionAPIError: Erros da API

    Example:
        send_image(
            number="5511999999999",
            image_url="https://example.com/image.jpg",
            caption="Confira esta imagem!"
        )
    """
    return client.send_media(
        number=number,
        media_url=image_url,
        media_type="image",
        caption=caption
    )


@mcp.tool()
def send_document(
    number: str,
    document_url: str,
    filename: str | None = None,
    caption: str | None = None
) -> dict:
    """Envia um documento para um número WhatsApp.

    Args:
        number: Número no formato internacional sem '+' (ex: 5511999999999)
        document_url: URL pública do documento (pdf, docx, xlsx, etc.)
        filename: Nome do arquivo a ser exibido (opcional)
        caption: Legenda do documento (opcional)

    Returns:
        dict: Resposta com message_id, status e timestamp

    Raises:
        InvalidPhoneNumberError: Se o número for inválido
        EvolutionAPIError: Erros da API

    Example:
        send_document(
            number="5511999999999",
            document_url="https://example.com/relatorio.pdf",
            filename="Relatório Mensal.pdf",
            caption="Segue o relatório solicitado"
        )
    """
    return client.send_media(
        number=number,
        media_url=document_url,
        media_type="document",
        caption=caption,
        filename=filename
    )


@mcp.tool()
def send_video(
    number: str,
    video_url: str,
    caption: str | None = None
) -> dict:
    """Envia um vídeo para um número WhatsApp.

    Args:
        number: Número no formato internacional sem '+' (ex: 5511999999999)
        video_url: URL pública do vídeo (mp4, etc.)
        caption: Legenda do vídeo (opcional)

    Returns:
        dict: Resposta com message_id, status e timestamp

    Raises:
        InvalidPhoneNumberError: Se o número for inválido
        EvolutionAPIError: Erros da API

    Example:
        send_video(
            number="5511999999999",
            video_url="https://example.com/video.mp4",
            caption="Veja este vídeo"
        )
    """
    return client.send_media(
        number=number,
        media_url=video_url,
        media_type="video",
        caption=caption
    )


@mcp.tool()
def send_audio(
    number: str,
    audio_url: str
) -> dict:
    """Envia um áudio para um número WhatsApp.

    Args:
        number: Número no formato internacional sem '+' (ex: 5511999999999)
        audio_url: URL pública do áudio (mp3, ogg, etc.)

    Returns:
        dict: Resposta com message_id, status e timestamp

    Raises:
        InvalidPhoneNumberError: Se o número for inválido
        EvolutionAPIError: Erros da API

    Example:
        send_audio(
            number="5511999999999",
            audio_url="https://example.com/audio.mp3"
        )
    """
    return client.send_media(
        number=number,
        media_url=audio_url,
        media_type="audio"
    )


@mcp.tool()
def send_location(
    number: str,
    latitude: float,
    longitude: float,
    name: str | None = None,
    address: str | None = None
) -> dict:
    """Envia uma localização para um número WhatsApp.

    Args:
        number: Número no formato internacional sem '+' (ex: 5511999999999)
        latitude: Latitude da localização (ex: -23.550520)
        longitude: Longitude da localização (ex: -46.633308)
        name: Nome do local (opcional, ex: "Avenida Paulista")
        address: Endereço do local (opcional, ex: "São Paulo, SP")

    Returns:
        dict: Resposta com message_id, status e timestamp

    Raises:
        InvalidPhoneNumberError: Se o número for inválido
        EvolutionAPIError: Erros da API

    Example:
        send_location(
            number="5511999999999",
            latitude=-23.550520,
            longitude=-46.633308,
            name="Avenida Paulista",
            address="São Paulo, SP"
        )
    """
    try:
        clean_number = client.validate_phone_number(number)

        client._log(f"Enviando localização para {clean_number}")

        # TODO: Verificar API exata da evolutionapi para location
        response = client._client.messages.send_location(
            instance=client.instance_name,
            number=clean_number,
            latitude=latitude,
            longitude=longitude,
            name=name,
            address=address
        )

        return response

    except Exception as e:
        client._handle_error(e, "send_location")


@mcp.tool()
def send_contact(
    number: str,
    contact_name: str,
    contact_phone: str,
    contact_organization: str | None = None
) -> dict:
    """Envia um contato para um número WhatsApp.

    Args:
        number: Número destinatário no formato internacional (ex: 5511999999999)
        contact_name: Nome completo do contato a ser compartilhado
        contact_phone: Telefone do contato no formato internacional
        contact_organization: Organização/empresa do contato (opcional)

    Returns:
        dict: Resposta com message_id, status e timestamp

    Raises:
        InvalidPhoneNumberError: Se o número for inválido
        EvolutionAPIError: Erros da API

    Example:
        send_contact(
            number="5511999999999",
            contact_name="João Silva",
            contact_phone="5511888888888",
            contact_organization="Empresa XYZ"
        )
    """
    try:
        clean_number = client.validate_phone_number(number)
        clean_contact_phone = client.validate_phone_number(contact_phone)

        client._log(f"Enviando contato para {clean_number}")

        # TODO: Verificar API exata da evolutionapi para contact
        response = client._client.messages.send_contact(
            instance=client.instance_name,
            number=clean_number,
            contact_name=contact_name,
            contact_phone=clean_contact_phone,
            contact_organization=contact_organization
        )

        return response

    except Exception as e:
        client._handle_error(e, "send_contact")


# ============================================================================
# TOOLS - Gerenciamento de Chats e Mensagens
# ============================================================================

@mcp.tool()
def list_chats(limit: int = 50) -> dict:
    """Lista as conversas/chats ativos da instância.

    Args:
        limit: Número máximo de chats a retornar (padrão: 50)

    Returns:
        dict: Lista de chats com informações como:
            - chat_id: ID do chat
            - name: Nome do contato/grupo
            - last_message: Última mensagem
            - unread_count: Mensagens não lidas
            - timestamp: Data da última interação

    Raises:
        EvolutionAPIError: Se houver erro ao listar chats

    Example:
        chats = list_chats(limit=20)
        for chat in chats['chats']:
            print(f"{chat['name']}: {chat['unread_count']} não lidas")
    """
    try:
        client._log(f"Listando chats (limit: {limit})")

        # TODO: Verificar API exata da evolutionapi
        response = client._client.chat.list_chats(
            instance=client.instance_name,
            limit=limit
        )

        return response

    except Exception as e:
        client._handle_error(e, "list_chats")


@mcp.tool()
def get_chat_messages(
    chat_id: str,
    limit: int = 50
) -> dict:
    """Obtém mensagens de uma conversa específica.

    Args:
        chat_id: ID do chat/conversa
        limit: Número máximo de mensagens a retornar (padrão: 50)

    Returns:
        dict: Lista de mensagens com:
            - message_id: ID da mensagem
            - from: Remetente
            - body: Conteúdo da mensagem
            - timestamp: Data/hora
            - type: Tipo (text, image, video, etc.)
            - is_from_me: Se foi enviada pela instância

    Raises:
        EvolutionAPIError: Se houver erro ao buscar mensagens

    Example:
        messages = get_chat_messages(
            chat_id="5511999999999@s.whatsapp.net",
            limit=30
        )
    """
    try:
        client._log(f"Obtendo mensagens do chat {chat_id}")

        # TODO: Verificar API exata da evolutionapi
        response = client._client.chat.get_messages(
            instance=client.instance_name,
            chat_id=chat_id,
            limit=limit
        )

        return response

    except Exception as e:
        client._handle_error(e, "get_chat_messages")


@mcp.tool()
def get_chat_by_number(number: str) -> dict:
    """Obtém informações de um chat a partir de um número de telefone.

    Args:
        number: Número no formato internacional sem '+' (ex: 5511999999999)

    Returns:
        dict: Informações do chat incluindo chat_id

    Raises:
        InvalidPhoneNumberError: Se o número for inválido
        EvolutionAPIError: Se houver erro

    Example:
        chat = get_chat_by_number("5511999999999")
        chat_id = chat['chat_id']
    """
    try:
        clean_number = client.validate_phone_number(number)

        # Formato padrão de chat_id no WhatsApp
        chat_id = f"{clean_number}@s.whatsapp.net"

        return {
            "chat_id": chat_id,
            "number": clean_number
        }

    except Exception as e:
        client._handle_error(e, "get_chat_by_number")


@mcp.tool()
def get_unread_messages() -> dict:
    """Obtém todas as mensagens não lidas da instância.

    Returns:
        dict: Lista de mensagens não lidas agrupadas por chat

    Raises:
        EvolutionAPIError: Se houver erro

    Example:
        unread = get_unread_messages()
        total = sum(chat['unread_count'] for chat in unread['chats'])
        print(f"Total de mensagens não lidas: {total}")
    """
    try:
        client._log("Obtendo mensagens não lidas")

        # TODO: Verificar API exata da evolutionapi
        response = client._client.chat.get_unread_messages(
            instance=client.instance_name
        )

        return response

    except Exception as e:
        client._handle_error(e, "get_unread_messages")


@mcp.tool()
def mark_chat_as_read(chat_id: str) -> dict:
    """Marca todas as mensagens de um chat como lidas.

    Args:
        chat_id: ID do chat a marcar como lido

    Returns:
        dict: Confirmação da operação

    Raises:
        EvolutionAPIError: Se houver erro

    Example:
        mark_chat_as_read("5511999999999@s.whatsapp.net")
    """
    try:
        client._log(f"Marcando chat {chat_id} como lido")

        # TODO: Verificar API exata da evolutionapi
        response = client._client.chat.mark_as_read(
            instance=client.instance_name,
            chat_id=chat_id
        )

        return response

    except Exception as e:
        client._handle_error(e, "mark_chat_as_read")


# ============================================================================
# TOOLS - Presença e Informações da Instância
# ============================================================================

@mcp.tool()
def set_presence(status: str) -> dict:
    """Define o status de presença da instância WhatsApp.

    Args:
        status: Status de presença. Valores válidos:
            - "available": Disponível/Online
            - "unavailable": Indisponível/Offline
            - "composing": Digitando...
            - "recording": Gravando áudio...

    Returns:
        dict: Confirmação da alteração de presença

    Raises:
        EvolutionAPIError: Se houver erro ao definir presença

    Example:
        set_presence("available")  # Fica online
        set_presence("unavailable")  # Fica offline
    """
    valid_statuses = ["available", "unavailable", "composing", "recording"]

    if status not in valid_statuses:
        raise ValueError(
            f"Status inválido: '{status}'. "
            f"Valores válidos: {', '.join(valid_statuses)}"
        )

    try:
        client._log(f"Definindo presença como '{status}'")

        # TODO: Verificar API exata da evolutionapi
        response = client._client.instance.set_presence(
            instance=client.instance_name,
            status=status
        )

        return response

    except Exception as e:
        client._handle_error(e, "set_presence")


@mcp.tool()
def get_instance_info() -> dict:
    """Obtém informações detalhadas da instância WhatsApp.

    Returns:
        dict: Informações completas da instância:
            - instance_name: Nome da instância
            - phone_number: Número conectado
            - status: Status da conexão
            - profile_name: Nome do perfil
            - profile_picture: URL da foto de perfil

    Raises:
        EvolutionAPIError: Se houver erro ao consultar

    Example:
        info = get_instance_info()
        print(f"Conectado como: {info['phone_number']}")
        print(f"Status: {info['status']}")
    """
    return client.get_instance_info()


# ============================================================================
# Entry Point
# ============================================================================

if __name__ == "__main__":
    # Executa o servidor MCP
    mcp.run()
