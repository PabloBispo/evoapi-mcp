"""MCP Server para Evolution API."""

import sys
from pathlib import Path

# Adiciona o diretório src ao path para permitir importações
src_dir = Path(__file__).parent.parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from mcp.server.fastmcp import FastMCP
from evoapi_mcp.config import load_config
from evoapi_mcp.client import EvolutionClient

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
        dict: Resposta da API com informações sobre a mensagem enviada

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
        dict: Resposta da API

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
        dict: Resposta da API

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
        dict: Resposta da API

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
        dict: Resposta da API

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


# ============================================================================
# TOOLS - Gerenciamento de Chats e Mensagens
# ============================================================================

@mcp.tool()
def get_chat_messages(
    number: str,
    limit: int = 50
) -> dict:
    """Obtém mensagens de uma conversa específica por número.

    Args:
        number: Número no formato internacional sem '+' (ex: 5511999999999)
        limit: Número máximo de mensagens a retornar (padrão: 50)

    Returns:
        dict: Lista de mensagens da conversa

    Example:
        messages = get_chat_messages(
            number="5511999999999",
            limit=30
        )
    """
    return client.get_messages_by_number(number=number, limit=limit)


@mcp.tool()
def list_chats() -> dict:
    """Lista todas as conversas ativas do WhatsApp.

    Returns:
        dict: { "data": [lista de chats] } com informações das conversas

    Example:
        chats = list_chats()
        print(f"Total de conversas: {len(chats['data'])}")
    """
    return client.find_chats()


@mcp.tool()
def find_messages(
    query: str | None = None,
    chat_id: str | None = None,
    limit: int = 50
) -> dict:
    """Busca mensagens com filtros avançados.

    Args:
        query: Termo de busca nas mensagens (opcional)
        chat_id: ID do chat específico no formato WhatsApp (ex: 5511999999999@s.whatsapp.net)
        limit: Número máximo de mensagens a retornar (padrão: 50)

    Returns:
        dict: Lista de mensagens encontradas

    Example:
        # Buscar por termo
        messages = find_messages(query="pedido")

        # Buscar em chat específico
        messages = find_messages(chat_id="5511999999999@s.whatsapp.net", limit=20)
    """
    return client.find_messages(query=query, chat_id=chat_id, limit=limit)


# ============================================================================
# TOOLS - Status e Presença
# ============================================================================

@mcp.tool()
def get_connection_status() -> dict:
    """Verifica o status da conexão da instância WhatsApp.

    Returns:
        dict: Estado da conexão contendo informações sobre a instância

    Example:
        status = get_connection_status()
        if status.get('state') == 'open':
            print("WhatsApp conectado!")
    """
    return client.get_connection_state()


@mcp.tool()
def set_presence(
    status: str,
    number: str | None = None
) -> dict:
    """Define o status de presença da instância WhatsApp.

    Args:
        status: Status de presença (available, unavailable, composing, recording)
        number: Número para enviar presença específica (opcional)

    Returns:
        dict: Confirmação da alteração de presença

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

    return client.set_presence(status=status, number=number)


@mcp.tool()
def get_instance_info() -> dict:
    """Obtém informações detalhadas da instância WhatsApp.

    Returns:
        dict: Informações completas da instância incluindo status e configuração

    Example:
        info = get_instance_info()
        print(f"Instância: {info['instance_name']}")
        print(f"Status: {info['status']}")
    """
    return client.get_instance_info()


# ============================================================================
# Entry Point
# ============================================================================

if __name__ == "__main__":
    # Executa o servidor MCP
    mcp.run()
