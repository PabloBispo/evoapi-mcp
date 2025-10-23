# ✅ TODO - Evolution API MCP Server

Lista de tarefas pendentes e em progresso.

**Última atualização:** 2025-10-23

---

## 🔥 Urgente (Fazer Hoje)

- [ ] Nenhuma tarefa urgente no momento

---

## 🎯 Próximas Tarefas (Esta Semana)

### Refatoração - Unificar Duplicações

- [ ] Mesclar `fetch_contacts()` e `find_contacts()` em uma única função
  - Localização: `src/evoapi_mcp/client.py:306-358`
  - Criar: `fetch_contacts(contact_id: str | None = None)`
  - Remover: `find_contacts()`

- [ ] Simplificar tools de contatos no server
  - Localização: `src/evoapi_mcp/server.py:293-359`
  - Unificar `get_contacts()` e `find_contact()`
  - Manter apenas: `get_contacts(contact_id=None, limit=None)`

### Validações

- [ ] Adicionar validação de `media_type` em `send_media()`
  - Localização: `src/evoapi_mcp/client.py:442`
  - Validar: `{"image", "video", "document", "audio"}`

- [ ] Adicionar validação de URLs em `send_media()`
  - Verificar se URL começa com `http://` ou `https://`

- [ ] Adicionar validação de tamanho de texto
  - Em `send_text()`: max 65536 chars (limite WhatsApp)

### Cache com TTL

- [ ] Implementar expiração automática do cache de contatos
  - Adicionar `_cache_timestamp: datetime | None`
  - Adicionar `_cache_ttl = timedelta(minutes=5)`
  - Adicionar método `_is_cache_expired()`

- [ ] Criar método `clear_cache()`
  - Limpar `_contact_names_cache`
  - Resetar `_cache_timestamp`

---

## 📋 Backlog (Próximo Mês)

### Type Safety

- [ ] Instalar Pydantic
  - Adicionar `pydantic>=2.0.0` em `pyproject.toml`

- [ ] Criar models:
  - [ ] `Contact`
  - [ ] `Chat`
  - [ ] `Message`
  - [ ] `MediaMessage`

- [ ] Atualizar type hints para usar models

### Error Handling

- [ ] Adicionar retry logic com tenacity
  - Instalar `tenacity>=8.0.0`
  - Adicionar decorator `@retry` em `_make_request()`

- [ ] Sanitizar logs
  - Criar método `_sanitize_error()`
  - Mascarar `self.api_key` nos logs

### Nomenclatura

- [ ] Renomear tools para melhor clareza:
  - `get_chat_messages()` → `get_messages_from_chat()`
  - `find_messages()` → `search_messages_globally()`

---

## 🚀 Futuro (Próximos 3 Meses)

### Novas Funcionalidades

- [ ] Grupos
  - [ ] Criar grupo
  - [ ] Adicionar/remover participantes
  - [ ] Listar membros

- [ ] Gestão de mensagens
  - [ ] Deletar mensagem
  - [ ] Editar mensagem
  - [ ] Reagir com emoji
  - [ ] Marcar como lida

- [ ] Upload/Download
  - [ ] Upload de arquivo local
  - [ ] Download de mídia recebida

### Testes

- [ ] Setup pytest
- [ ] Testes unitários (client.py)
- [ ] Testes de integração (com mocks)
- [ ] Coverage > 80%

### CI/CD

- [ ] GitHub Actions
- [ ] Pre-commit hooks
- [ ] Auto-publish no PyPI

### Documentação

- [ ] README.md completo
- [ ] CHANGELOG.md
- [ ] CONTRIBUTING.md
- [ ] API Reference

---

## ✅ Concluído (Últimos 7 Dias)

### 2025-10-23

- ✅ Corrigido endpoint de contatos (`/chat/contacts` → `/chat/findContacts`)
- ✅ Corrigido processamento de resposta (lista direta, não `{"data": [...]}`)
- ✅ Otimizado busca de nomes (bulk fetch ao invés de N+1 requests)
- ✅ Implementado cache de nomes em memória
- ✅ Adicionado enriquecimento automático de chats com nomes

### 2025-10-22

- ✅ Migrado de biblioteca `evolutionapi` para HTTP direto com `requests`
- ✅ Implementados todos endpoints principais da Evolution API
- ✅ Adicionado suporte a contatos e nomes
- ✅ Criados tools MCP completos
- ✅ Adicionados parâmetros `limit` em todos os tools de listagem

---

## 📝 Notas

### Formato de Tarefas

```markdown
- [ ] Descrição da tarefa
  - Localização: arquivo:linha
  - Contexto adicional
  - Impacto esperado
```

### Prioridades

- 🔥 **Urgente**: Fazer hoje
- 🎯 **Alta**: Esta semana
- 📋 **Média**: Este mês
- 🚀 **Baixa**: Próximos 3 meses

### Como Marcar Tarefa como Concluída

1. Mover de "Próximas Tarefas" para "Concluído"
2. Adicionar data: `### YYYY-MM-DD`
3. Trocar `- [ ]` por `- ✅`
4. Adicionar commit hash se aplicável

---

**Dica:** Use `Ctrl+F` para buscar tarefas específicas por arquivo ou funcionalidade.
