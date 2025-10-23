# 🐛 Known Issues - Evolution API MCP Server

Problemas conhecidos, limitações e workarounds.

**Última atualização:** 2025-10-23

---

## 🔴 Crítico

### Issue #1: Duplicação de Código - fetch_contacts vs find_contacts

**Status:** 🔴 Aberto
**Prioridade:** Alta
**Arquivo:** `src/evoapi_mcp/client.py:306-358`

**Descrição:**
Duas funções fazem essencialmente a mesma coisa:

```python
# Linha 306
def fetch_contacts(self) -> list[dict[str, Any]]:
    result = self._make_request("POST", "/chat/findContacts/{instanceId}", data={})
    ...

# Linha 327
def find_contacts(self, contact_id: str | None = None) -> list[dict[str, Any]]:
    payload = {}
    if contact_id:
        payload["where"] = {"id": contact_id}
    result = self._make_request("POST", "/chat/findContacts/{instanceId}", data=payload)
    ...
```

Ambas chamam o mesmo endpoint, apenas com filtros diferentes.

**Impacto:**
- Código duplicado
- Confunde o LLM ao escolher qual ferramenta usar
- Mais difícil de manter

**Solução Proposta:**
```python
def fetch_contacts(
    self,
    contact_id: str | None = None,
    filters: dict | None = None
) -> list[dict[str, Any]]:
    """Busca contatos com filtros opcionais.

    Args:
        contact_id: ID específico do contato
        filters: Filtros adicionais (where, limit, etc)
    """
    payload = {}
    if contact_id:
        payload["where"] = {"id": contact_id}
    if filters:
        payload.update(filters)

    result = self._make_request("POST", "/chat/findContacts/{instanceId}", data=payload)
    # ... resto da lógica
```

**Workaround Atual:**
Nenhum necessário, ambas funcionam.

---

### Issue #2: Cache de Contatos Nunca Expira

**Status:** 🔴 Aberto
**Prioridade:** Alta
**Arquivo:** `src/evoapi_mcp/client.py:58`

**Descrição:**
O cache de nomes de contatos é criado na inicialização e nunca expira:

```python
def __init__(self, config: EvolutionConfig):
    # ...
    self._contact_names_cache: dict[str, str | None] = {}
```

Se um contato mudar o nome no WhatsApp, o cache fica desatualizado até reiniciar o Claude Desktop.

**Impacto:**
- Nomes desatualizados podem aparecer
- Único jeito de atualizar é reiniciar o Claude Desktop

**Solução Proposta:**
Adicionar TTL (Time To Live) no cache:

```python
from datetime import datetime, timedelta

class EvolutionClient:
    def __init__(self, config):
        self._contact_names_cache = {}
        self._cache_timestamp: datetime | None = None
        self._cache_ttl = timedelta(minutes=5)

    def _is_cache_expired(self) -> bool:
        if not self._cache_timestamp:
            return True
        return datetime.now() - self._cache_timestamp > self._cache_ttl

    def _build_contacts_map(self):
        if self._is_cache_expired():
            # Recarrega
            ...
            self._cache_timestamp = datetime.now()
        return self._contact_cache
```

**Workaround Atual:**
Reiniciar o Claude Desktop para limpar o cache.

---

### Issue #3: Sem Validação de media_type em send_media()

**Status:** 🔴 Aberto
**Prioridade:** Alta
**Arquivo:** `src/evoapi_mcp/client.py:442`

**Descrição:**
A função `send_media()` aceita qualquer string como `media_type`:

```python
def send_media(
    self,
    number: str,
    media_url: str,
    media_type: str,  # ❌ Sem validação!
    caption: str | None = None,
    filename: str | None = None
):
    payload = {
        "mediatype": media_type,  # Vai direto pra API
        ...
    }
```

Valores inválidos só são detectados quando a API retorna erro.

**Impacto:**
- Erro tarde demais (após chamada HTTP)
- Mensagem de erro genérica da API
- Pior experiência do desenvolvedor

**Exemplo do Problema:**
```python
# Isso não dá erro até chamar a API:
client.send_media(
    number="5511999999999",
    media_url="https://example.com/file.pdf",
    media_type="pdf"  # ❌ Deveria ser "document"
)
```

**Solução Proposta:**
```python
VALID_MEDIA_TYPES = {"image", "video", "document", "audio"}

def send_media(self, ..., media_type: str, ...):
    if media_type not in VALID_MEDIA_TYPES:
        raise ValueError(
            f"media_type inválido: '{media_type}'. "
            f"Valores válidos: {', '.join(VALID_MEDIA_TYPES)}"
        )
    ...
```

**Workaround Atual:**
Verificar manualmente antes de chamar a função.

---

## 🟡 Médio

### Issue #4: Type Hints Muito Genéricos

**Status:** 🟡 Aberto
**Prioridade:** Média
**Arquivo:** `src/evoapi_mcp/client.py` (vários locais)

**Descrição:**
Muitas funções retornam `dict[str, Any]`, o que não ajuda o desenvolvedor:

```python
def find_chats(...) -> dict[str, Any]:  # O que tem nesse dict?
def send_text(...) -> dict[str, Any]:   # E nesse?
def fetch_contacts(...) -> list[dict[str, Any]]:  # E aqui?
```

**Impacto:**
- Sem autocomplete no IDE
- Não detecta erros em tempo de desenvolvimento
- Código menos type-safe

**Solução Proposta:**
Usar Pydantic para criar models:

```python
from pydantic import BaseModel

class Contact(BaseModel):
    remote_jid: str
    push_name: str | None
    is_group: bool
    profile_pic_url: str | None

class Chat(BaseModel):
    remote_jid: str
    push_name: str | None
    last_message: dict | None
    unread_count: int

def find_chats(...) -> list[Chat]:  # ✅ Type-safe!
def fetch_contacts(...) -> list[Contact]:  # ✅ Type-safe!
```

**Workaround Atual:**
Consultar documentação ou código-fonte para saber o formato.

---

### Issue #5: Sem Retry em Falhas Temporárias

**Status:** 🟡 Aberto
**Prioridade:** Média
**Arquivo:** `src/evoapi_mcp/client.py:99-168`

**Descrição:**
A função `_make_request()` não tenta novamente em caso de falhas temporárias:

```python
def _make_request(self, ...):
    response = requests.request(...)  # ❌ Se falhar → erro imediato
    response.raise_for_status()
```

**Impacto:**
- Falhas temporárias de rede causam erro
- Usuário precisa tentar novamente manualmente

**Exemplo do Problema:**
```python
# Se a rede estiver instável:
client.send_text(...)  # Pode falhar com ConnectionError
# Usuário precisa executar comando novamente
```

**Solução Proposta:**
Usar biblioteca `tenacity` para retry automático:

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((ConnectionError, Timeout))
)
def _make_request(self, ...):
    ...
```

**Workaround Atual:**
Usuário tenta novamente manualmente.

---

### Issue #6: Logs Podem Expor API Key

**Status:** 🟡 Aberto
**Prioridade:** Média
**Arquivo:** `src/evoapi_mcp/client.py:146`

**Descrição:**
Ao logar erros HTTP, o response.text pode conter informações sensíveis:

```python
except requests.exceptions.HTTPError as e:
    error_msg = f"HTTP {e.response.status_code}: {e.response.text}"
    self._log(error_msg, "ERROR")  # ⚠️ Pode ter API key!
```

Algumas APIs retornam headers ou detalhes que incluem credenciais.

**Impacto:**
- Risco de segurança
- API key pode aparecer em logs

**Solução Proposta:**
Sanitizar response antes de logar:

```python
def _sanitize_error(self, text: str) -> str:
    """Remove informações sensíveis."""
    return text.replace(self.api_key, "***APIKEY***")

except requests.exceptions.HTTPError as e:
    error_msg = f"HTTP {e.response.status_code}: {e.response.text}"
    self._log(self._sanitize_error(error_msg), "ERROR")
```

**Workaround Atual:**
Não compartilhar logs públicos.

---

## 🟢 Baixo

### Issue #7: Timeout Muito Alto (30s)

**Status:** 🟢 Aberto
**Prioridade:** Baixa
**Arquivo:** `src/evoapi_mcp/config.py:21`

**Descrição:**
Timeout padrão é 30 segundos:

```python
timeout: int = 30  # Muito tempo para usuário esperar
```

Se a API estiver lenta, usuário fica esperando 30 segundos antes de ver erro.

**Impacto:**
- Experiência ruim quando API está lenta
- Usuário acha que travou

**Solução Proposta:**
Reduzir para 10-15 segundos:

```python
timeout: int = 15  # Mais razoável
```

**Workaround Atual:**
Configurar `EVOLUTION_TIMEOUT=15` no `.env`.

---

### Issue #8: Nomenclatura Confusa para LLM

**Status:** 🟢 Aberto
**Prioridade:** Baixa
**Arquivo:** `src/evoapi_mcp/server.py`

**Descrição:**
Alguns tools têm nomes similares que podem confundir o LLM:

```python
get_chat_messages()  # Mensagens de um chat
find_messages()      # Busca em todos os chats

get_contacts()       # Lista contatos
find_contact()       # Busca contatos (mesma coisa?)
```

**Impacto:**
- LLM pode escolher tool errado
- Usuário recebe resultado inesperado

**Solução Proposta:**
Renomear para maior clareza:

```python
get_messages_from_chat()      # Claro que é de um chat específico
search_messages_globally()    # Claro que busca em todos
```

**Workaround Atual:**
Docstrings bem detalhadas ajudam o LLM a escolher certo.

---

## 📊 Estatísticas

### Por Prioridade
- 🔴 Crítico: 3 issues
- 🟡 Médio: 3 issues
- 🟢 Baixo: 2 issues

### Por Status
- 🔴 Aberto: 8 issues
- ✅ Resolvido: 0 issues

---

## 🔄 Issues Resolvidas

*(Nenhuma ainda)*

---

## 📝 Como Reportar Nova Issue

1. Adicione seção com título descritivo
2. Defina Status (🔴/🟡/🟢)
3. Defina Prioridade (Alta/Média/Baixa)
4. Informe arquivo e linha
5. Descreva o problema com código
6. Explique o impacto
7. Proponha solução
8. Documente workaround se existir

**Template:**
```markdown
### Issue #X: Título Descritivo

**Status:** 🔴 Aberto
**Prioridade:** Alta
**Arquivo:** `path/to/file.py:123`

**Descrição:**
...código exemplo...

**Impacto:**
- ...

**Solução Proposta:**
...código proposto...

**Workaround Atual:**
...
```

---

**Última revisão:** 2025-10-23
