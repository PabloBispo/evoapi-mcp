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
    """Obtém mensagens de uma conversa específica por número de telefone.

    Use esta ferramenta quando o usuário pedir:
    - "mostre as mensagens do número X"
    - "últimas 20 mensagens de fulano"
    - "conversa com 5511999999999"

    Args:
        number: Número no formato internacional sem '+' (ex: 5511999999999)
        limit: Número máximo de mensagens a retornar. SEMPRE ajuste este valor
               quando o usuário especificar quantidade (ex: "últimas 20", "50 mensagens")
               Padrão: 50 mensagens

    Returns:
        dict: Lista de mensagens da conversa

    Example:
        # Últimas 50 mensagens (padrão)
        messages = get_chat_messages(number="5511999999999")

        # Últimas 20 mensagens
        messages = get_chat_messages(number="5511999999999", limit=20)
    """
    return client.get_messages_by_number(number=number, limit=limit)


@mcp.tool()
def list_chats(limit: int | None = None) -> list:
    """Lista conversas ativas do WhatsApp ordenadas por data de atualização.

    Use esta ferramenta quando o usuário pedir:
    - "liste minhas conversas"
    - "mostre minhas conversas mais recentes"
    - "quais são meus últimos chats"

    Args:
        limit: Número máximo de conversas a retornar. SEMPRE use este parâmetro
               quando o usuário especificar uma quantidade (ex: "5 conversas", "10 chats")

    Returns:
        list: Lista de conversas, cada uma com:
              - remoteJid: ID do chat
              - pushName: Nome do contato (ou null)
              - lastMessage: Última mensagem trocada
              - unreadCount: Número de mensagens não lidas

    Example:
        # Listar todas as conversas
        chats = list_chats()

        # Listar apenas as 10 mais recentes (IMPORTANTE: sempre passar limit quando especificado)
        chats = list_chats(limit=10)
    """
    chats = client.find_chats()

    # Aplica limit se fornecido
    if limit is not None and isinstance(chats, list):
        chats = chats[:limit]

    return chats


@mcp.tool()
def find_messages(
    query: str | None = None,
    chat_id: str | None = None,
    limit: int = 50
) -> dict:
    """Busca mensagens com filtros avançados em todas as conversas.

    Use esta ferramenta quando o usuário pedir:
    - "busque mensagens com a palavra X"
    - "encontre mensagens sobre pedido"
    - "mensagens que contenham reunião"

    Args:
        query: Termo de busca nas mensagens. Use quando o usuário pedir para
               buscar/encontrar mensagens com palavras específicas
        chat_id: ID do chat específico no formato WhatsApp (ex: 5511999999999@s.whatsapp.net)
                 Raramente usado - prefira usar number com get_chat_messages()
        limit: Número máximo de mensagens a retornar. SEMPRE ajuste quando
               o usuário especificar quantidade
               Padrão: 50 mensagens

    Returns:
        dict: Lista de mensagens encontradas

    Example:
        # Buscar por termo em todas as conversas
        messages = find_messages(query="pedido")

        # Buscar apenas 10 mensagens com "reunião"
        messages = find_messages(query="reunião", limit=10)

        # Buscar em chat específico
        messages = find_messages(chat_id="5511999999999@s.whatsapp.net", limit=20)
    """
    return client.find_messages(query=query, chat_id=chat_id, limit=limit)


@mcp.tool()
def get_contacts(
    contact_id: str | None = None,
    limit: int | None = None
) -> list:
    """Busca contatos salvos no WhatsApp com filtros opcionais.

    Use esta ferramenta quando o usuário pedir:
    - "liste meus contatos"
    - "mostre 10 contatos"
    - "quais são meus contatos salvos"
    - "busque o contato 5511999999999"
    - "mostre informações do contato X"

    Args:
        contact_id: ID específico do contato (ex: 5511999999999@s.whatsapp.net).
                   Use quando buscar um contato específico.
                   Se None, retorna todos os contatos.

        limit: Número máximo de contatos a retornar. SEMPRE use este parâmetro
               quando o usuário especificar uma quantidade (ex: "10 contatos", "5 primeiros")
               Se não especificado, retorna TODOS os contatos (pode ser muitos!)

    Returns:
        list: Lista de contatos onde cada contato tem:
              - remoteJid: ID do contato (ex: 5511999999999@s.whatsapp.net)
              - pushName: Nome do contato
              - isGroup: Se é grupo ou contato individual
              - profilePicUrl: URL da foto de perfil

    Example:
        # Buscar todos os contatos (pode retornar centenas!)
        contacts = get_contacts()

        # Buscar apenas os primeiros 10 contatos (RECOMENDADO quando há quantidade)
        contacts = get_contacts(limit=10)

        # Buscar contato específico
        contact = get_contacts(contact_id="5511999999999@s.whatsapp.net")

        # Buscar contato específico (apenas 1 resultado)
        contact = get_contacts(contact_id="5511999999999@s.whatsapp.net", limit=1)
    """
    contacts = client.fetch_contacts(contact_id=contact_id)

    # Aplica limit se fornecido
    if limit is not None and isinstance(contacts, list):
        contacts = contacts[:limit]

    return contacts


@mcp.tool()
def get_contact_name_by_number(number: str) -> dict:
    """Obtém o nome de um contato pelo número de telefone.

    Args:
        number: Número no formato internacional sem '+' (ex: 5511999999999)

    Returns:
        dict: {"number": "5511999999999", "name": "Nome do Contato" ou None}

    Example:
        info = get_contact_name_by_number("5511999999999")
        if info['name']:
            print(f"Contato: {info['name']}")
        else:
            print(f"Número não salvo: {info['number']}")
    """
    name = client.get_contact_name(number)
    return {
        "number": number,
        "name": name
    }


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
