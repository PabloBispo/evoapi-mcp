# 🔧 Correções Aplicadas

## Problema 1: ModuleNotFoundError ✅ RESOLVIDO

### Erro Original
```
ModuleNotFoundError: No module named 'evolutionapi'
```

### Causa
O comando anterior usava `uv run --with mcp[cli]`, que criava um ambiente temporário apenas com `mcp[cli]`, sem as dependências do projeto (evolutionapi, pydantic-settings, etc.).

### Solução Aplicada

**Antes:**
```json
"command": "uv",
"args": [
  "run",
  "--with",
  "mcp[cli]",
  "mcp",
  "run",
  "/path/to/server.py"
]
```

**Depois:**
```json
"command": "/Users/pablofernando/.local/bin/uv",
"args": [
  "--directory",
  "/Users/pablofernando/projects/mcp/evoapi-mcp",
  "run",
  "python",
  "src/evoapi_mcp/server.py"
]
```

### O Que Mudou

1. ✅ **Usa o ambiente virtual do projeto** (com todas as dependências)
2. ✅ **Executa Python diretamente** (não via `mcp run`)
3. ✅ **Define o diretório de trabalho** com `--directory`

---

## Problema 2: Incompatibilidade com biblioteca evolutionapi ✅ RESOLVIDO

### Erros Reportados

1. `'EvolutionClient' object has no attribute 'instance'`
2. `ChatService.get_messages() got an unexpected keyword argument 'limit'`
3. `MessageService.send_text() got an unexpected keyword argument 'instance'`

### Causa Raiz

A biblioteca Python `evolutionapi` (v0.1.2) possui APIs **incompletas e incompatíveis** com a documentação da Evolution API REST. Métodos essenciais:
- Não existem (ex: `list_chats()`)
- Têm assinaturas diferentes (ex: `get_messages()` sem suporte a `limit`)
- Requerem parâmetros não documentados

### Solução Implementada

**Substituição completa por chamadas HTTP diretas à API REST.**

#### Antes: Dependência da biblioteca Python
```python
# pyproject.toml
dependencies = [
    "evolutionapi>=0.1.0,<=0.1.2",  # ❌ Biblioteca incompleta
]

# client.py
from evolutionapi.client import EvolutionClient as BaseEvolutionClient
from evolutionapi.models.message import TextMessage

self._client = BaseEvolutionClient(
    base_url=config.base_url,
    api_token=config.api_token
)
```

#### Depois: Chamadas HTTP diretas com requests
```python
# pyproject.toml
dependencies = [
    "requests>=2.31.0",  # ✅ HTTP direto
]

# client.py
import requests

self.headers = {
    'apikey': self.api_key,
    'Content-Type': 'application/json'
}

def _make_request(self, method: str, endpoint: str, data: dict | None = None):
    url = f"{self.base_url}{endpoint}"
    response = requests.request(
        method=method,
        url=url,
        headers=self.headers,
        json=data,
        timeout=self.timeout
    )
    return response.json()
```

### Novos Métodos Implementados

| Método | Endpoint | Status |
|--------|----------|--------|
| `find_chats()` | GET /chat/findChats/{instanceId} | ✅ Novo |
| `find_messages()` | POST /chat/findMessages/{instanceId} | ✅ Novo |
| `get_messages_by_number()` | POST /chat/findMessages/{instanceId} | ✅ Novo |
| `send_text()` | POST /message/sendText/{instanceId} | ✅ Corrigido |
| `send_media()` | POST /message/sendMedia/{instanceId} | ✅ Corrigido |
| `get_connection_state()` | GET /instance/connectionState/{instanceId} | ✅ Corrigido |
| `set_presence()` | POST /chat/presenceUpdate/{instanceId} | ✅ Corrigido |

### Novos Tools no MCP Server

Adicionados 2 novos tools ao `server.py`:

1. **`list_chats()`** - Lista todas conversas ativas
   ```python
   @mcp.tool()
   def list_chats() -> dict:
       """Lista todas as conversas ativas do WhatsApp."""
       return client.find_chats()
   ```

2. **`find_messages()`** - Busca avançada de mensagens
   ```python
   @mcp.tool()
   def find_messages(
       query: str | None = None,
       chat_id: str | None = None,
       limit: int = 50
   ) -> dict:
       """Busca mensagens com filtros avançados."""
       return client.find_messages(query=query, chat_id=chat_id, limit=limit)
   ```

### Métodos Corrigidos

**`get_chat_messages()` - Agora com suporte a `limit`**
```python
# Antes (quebrava)
return client.get_messages(number=number, limit=limit)  # ❌ limit não suportado

# Depois (funciona)
return client.get_messages_by_number(number=number, limit=limit)  # ✅ HTTP direto
```

---

## Resumo das Alterações

### Arquivos Modificados

1. **`pyproject.toml`**
   - ❌ Removido: `evolutionapi>=0.1.0,<=0.1.2`
   - ✅ Adicionado: `requests>=2.31.0`

2. **`src/evoapi_mcp/client.py`** (reescrita completa - 413 linhas)
   - ✅ Novo método `_make_request()` - wrapper HTTP genérico
   - ✅ Header `apikey` para autenticação
   - ✅ Endpoints REST seguindo documentação oficial
   - ✅ Error handling robusto (401, 404, timeout, etc.)
   - ✅ Substituição de `{instanceId}` automática nos endpoints
   - ✅ Validação de phone number mantida
   - ✅ Logging para stderr mantido

3. **`src/evoapi_mcp/server.py`**
   - ✅ Corrigido `get_chat_messages()` → usa `get_messages_by_number()`
   - ✅ Adicionado `list_chats()` tool
   - ✅ Adicionado `find_messages()` tool

### Total de Tools Disponíveis: 11

| Categoria | Tools | Status |
|-----------|-------|--------|
| **Envio** | send_text_message, send_image, send_document, send_video, send_audio | ✅ 5 tools |
| **Mensagens** | get_chat_messages, list_chats, find_messages | ✅ 3 tools |
| **Status** | get_connection_status, set_presence, get_instance_info | ✅ 3 tools |

---

## 🔄 Próximo Passo

**Reinicie o Claude Desktop:**

1. Feche completamente (⌘Q)
2. Reabra
3. Teste com comandos:
   - `Liste minhas conversas do WhatsApp`
   - `Quais são minhas últimas mensagens?`
   - `Verifique o status da minha conexão WhatsApp`

---

## ✅ Verificação

Se ainda houver erros, execute manualmente para debug:

```bash
cd /Users/pablofernando/projects/mcp/evoapi-mcp
uv run python src/evoapi_mcp/server.py
```

Ou use o modo de desenvolvimento do MCP:

```bash
uv run mcp dev src/evoapi_mcp/server.py
```

Isso abre interface web para testar cada tool individualmente.

---

## 📊 Referências

- **Código de referência**: [IntuitivePhella/mcp-evolution-api](https://github.com/IntuitivePhella/mcp-evolution-api/blob/main/src/services/evolutionApiService.ts)
- **Documentação Evolution API**: https://doc.evolution-api.com/
- **MCP Protocol**: https://modelcontextprotocol.io/

---

**Status**: ✅ Corrigido - Aguardando teste no Claude Desktop
**Data**: 2025-10-23
**Versão**: 0.2.0 (HTTP Direto)
