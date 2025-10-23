# 🗺️ Roadmap - Evolution API MCP Server

Plano de melhorias e funcionalidades futuras para o projeto.

**Status:** 🟢 Ativo | **Última atualização:** 2025-10-23

---

## 📊 Visão Geral

### Estado Atual
- ✅ Integração HTTP direta funcionando
- ✅ Envio de mensagens (texto, mídia)
- ✅ Listagem de chats e contatos
- ✅ Busca de mensagens
- ✅ Cache de nomes em memória
- ✅ Performance otimizada (bulk fetch)

### Problemas Conhecidos
- 🔴 Duplicação de código (fetch_contacts vs find_contacts)
- 🔴 Validações fracas (media_type, URLs)
- 🔴 Cache nunca expira
- 🟡 Type safety fraca (dict[str, Any])
- 🟡 Error handling genérico
- 🟡 Nomenclatura confusa para LLM

---

## 🎯 FASE 1 - Correções Críticas

> **Objetivo:** Eliminar problemas que afetam estabilidade e qualidade do código
> **Prioridade:** 🔴 ALTA
> **Prazo:** Curto prazo (1-2 dias)

### 1.1 Unificar Duplicações

- [ ] **Mesclar fetch_contacts() e find_contacts()**
  - Criar método único: `fetch_contacts(contact_id: str | None = None)`
  - Remover método duplicado `find_contacts()`
  - Atualizar chamadas no server.py

- [ ] **Simplificar tools de contatos**
  - Unificar `get_contacts()` e `find_contact()` em um único tool
  - Manter apenas `get_contacts(contact_id=None, limit=None)`
  - Atualizar docstrings para clareza

**Impacto:** Reduz confusão do LLM, remove código redundante

---

### 1.2 Adicionar Validações Robustas

- [ ] **Validar media_type em send_media()**
  ```python
  VALID_MEDIA_TYPES = {"image", "video", "document", "audio"}
  if media_type not in VALID_MEDIA_TYPES:
      raise ValueError(...)
  ```

- [ ] **Validar URLs antes de enviar**
  ```python
  if not url.startswith(("http://", "https://")):
      raise ValueError("URL deve começar com http:// ou https://")
  ```

- [ ] **Validar tamanho de texto**
  ```python
  MAX_TEXT_LENGTH = 65536  # 64KB (limite WhatsApp)
  if len(text) > MAX_TEXT_LENGTH:
      raise ValueError(f"Texto muito longo: {len(text)} chars")
  ```

- [ ] **Validar status de presença**
  - Já implementado em server.py:432
  - ✅ Validação no server, falta no client

**Impacto:** Evita erros antes de chamar API, melhores mensagens de erro

---

### 1.3 Implementar TTL no Cache

- [ ] **Cache com expiração automática**
  ```python
  from datetime import datetime, timedelta

  class EvolutionClient:
      _cache_ttl = timedelta(minutes=5)
      _cache_timestamp: datetime | None = None
  ```

- [ ] **Método para limpar cache manualmente**
  ```python
  def clear_cache(self) -> None:
      """Limpa cache de nomes de contatos."""
      self._contact_names_cache.clear()
      self._cache_timestamp = None
  ```

- [ ] **Verificação automática de expiração**
  - Em `_build_contacts_map()`: checar se expirou
  - Recarregar automaticamente se necessário

**Impacto:** Cache atualizado, evita nomes desatualizados

---

## 🔧 FASE 2 - Melhorias de Qualidade

> **Objetivo:** Melhorar robustez, type safety e experiência do desenvolvedor
> **Prioridade:** 🟡 MÉDIA
> **Prazo:** Médio prazo (1-2 semanas)

### 2.1 Type Safety com Pydantic

- [ ] **Criar models para dados da API**
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

  class Message(BaseModel):
      key: dict
      message_timestamp: int
      message: dict
      push_name: str | None
  ```

- [ ] **Retornar objetos tipados**
  ```python
  def find_chats(...) -> list[Chat]:  # Em vez de dict[str, Any]
  def fetch_contacts(...) -> list[Contact]:
  ```

- [ ] **Validação automática de respostas**
  - Parse JSON → Pydantic models
  - Detecta mudanças na API automaticamente

**Impacto:** Autocomplete no IDE, detecta erros em tempo de desenvolvimento

---

### 2.2 Retry Logic e Resilência

- [ ] **Adicionar dependência tenacity**
  ```toml
  dependencies = [
      "tenacity>=8.0.0",
  ]
  ```

- [ ] **Implementar retry com backoff**
  ```python
  from tenacity import retry, stop_after_attempt, wait_exponential

  @retry(
      stop=stop_after_attempt(3),
      wait=wait_exponential(multiplier=1, min=2, max=10)
  )
  def _make_request(self, ...):
      ...
  ```

- [ ] **Retry apenas em erros temporários**
  - 5xx: Retry (erro do servidor)
  - 429: Retry com backoff (rate limit)
  - 4xx: Não retry (erro do cliente)

**Impacto:** Mais resiliente a falhas temporárias de rede

---

### 2.3 Segurança em Logs

- [ ] **Sanitizar API keys em logs**
  ```python
  def _sanitize_error(self, text: str) -> str:
      """Remove informações sensíveis dos logs."""
      sanitized = text.replace(self.api_key, "***APIKEY***")
      # Remove outros padrões sensíveis
      return sanitized
  ```

- [ ] **Níveis de log configuráveis**
  ```python
  LOG_LEVEL = os.getenv("EVOLUTION_LOG_LEVEL", "INFO")
  # DEBUG, INFO, WARNING, ERROR
  ```

- [ ] **Não logar payloads sensíveis**
  - Mensagens de usuários
  - Números de telefone
  - Conteúdo de mídias

**Impacto:** Segurança, compliance com LGPD/GDPR

---

### 2.4 Melhorar Nomenclatura

- [ ] **Renomear tools para clareza**
  ```python
  # Antes → Depois
  get_chat_messages() → get_messages_from_chat()
  find_messages() → search_messages_globally()
  ```

- [ ] **Docstrings mais explícitas**
  - Adicionar seção "When to use this vs X"
  - Exemplos de casos de uso específicos

**Impacto:** LLM escolhe tool correto mais frequentemente

---

## 🚀 FASE 3 - Novas Funcionalidades

> **Objetivo:** Expandir capacidades do servidor
> **Prioridade:** 🟢 BAIXA
> **Prazo:** Longo prazo (1+ mês)

### 3.1 Gerenciamento de Grupos

- [ ] **Criar grupo**
  ```python
  def create_group(name: str, participants: list[str]) -> dict
  ```

- [ ] **Adicionar/remover participantes**
  ```python
  def add_participant(group_id: str, number: str) -> dict
  def remove_participant(group_id: str, number: str) -> dict
  ```

- [ ] **Atualizar informações do grupo**
  ```python
  def update_group_info(group_id: str, name: str, description: str) -> dict
  ```

- [ ] **Listar membros do grupo**
  ```python
  def get_group_members(group_id: str) -> list[Contact]
  ```

**Impacto:** Gerenciar grupos pelo MCP

---

### 3.2 Gestão Avançada de Mensagens

- [ ] **Deletar mensagens**
  ```python
  def delete_message(message_id: str, for_everyone: bool = False) -> dict
  ```

- [ ] **Editar mensagens**
  ```python
  def edit_message(message_id: str, new_text: str) -> dict
  ```

- [ ] **Reagir com emoji**
  ```python
  def react_to_message(message_id: str, emoji: str) -> dict
  ```

- [ ] **Marcar como lida**
  ```python
  def mark_as_read(chat_id: str) -> dict
  ```

- [ ] **Encaminhar mensagem**
  ```python
  def forward_message(message_id: str, to_number: str) -> dict
  ```

**Impacto:** Funcionalidades completas de mensageria

---

### 3.3 Upload e Download de Mídias

- [ ] **Upload de arquivo local**
  ```python
  def upload_media(file_path: str) -> dict:
      """Upload arquivo local e retorna URL."""
      with open(file_path, 'rb') as f:
          # POST multipart/form-data
          ...
  ```

- [ ] **Download de mídia recebida**
  ```python
  def download_media(message_id: str, save_path: str) -> str:
      """Baixa mídia de mensagem recebida."""
      ...
  ```

**Impacto:** Não depende de URLs públicas para enviar mídias

---

### 3.4 Status (Stories)

- [ ] **Postar status**
  ```python
  def post_status(text: str | None, media_url: str | None) -> dict
  ```

- [ ] **Ver status de contatos**
  ```python
  def get_statuses() -> list[dict]
  ```

**Impacto:** Gerenciar status pelo MCP

---

## 🧪 FASE 4 - Qualidade e DevOps

> **Objetivo:** Garantir qualidade e facilitar manutenção
> **Prioridade:** 🟢 BAIXA
> **Prazo:** Contínuo

### 4.1 Testes Automatizados

- [ ] **Setup pytest**
  ```bash
  pip install pytest pytest-cov pytest-mock
  ```

- [ ] **Testes unitários**
  ```
  tests/
    ├── unit/
    │   ├── test_client.py
    │   ├── test_validation.py
    │   ├── test_cache.py
    │   └── test_models.py
  ```

- [ ] **Testes de integração (com mocks)**
  ```
    ├── integration/
    │   ├── test_api_mock.py
    │   └── test_mcp_tools.py
  ```

- [ ] **Coverage > 80%**
  ```bash
  pytest --cov=src/evoapi_mcp --cov-report=html
  ```

**Impacto:** Confiança em mudanças, menos bugs

---

### 4.2 CI/CD

- [ ] **GitHub Actions**
  ```yaml
  .github/workflows/test.yml:
    - Run pytest
    - Check coverage
    - Lint with ruff
    - Type check with mypy
  ```

- [ ] **Pre-commit hooks**
  ```yaml
  .pre-commit-config.yaml:
    - ruff (linting)
    - black (formatting)
    - mypy (type checking)
  ```

**Impacto:** Qualidade automática, menos erros em produção

---

### 4.3 Documentação Completa

- [ ] **README.md detalhado**
  - Instalação
  - Configuração
  - Exemplos de uso
  - Troubleshooting
  - FAQ

- [ ] **CHANGELOG.md**
  - Seguir [Keep a Changelog](https://keepachangelog.com/)
  - Versionamento semântico

- [ ] **CONTRIBUTING.md**
  - Como contribuir
  - Code of Conduct
  - Processo de PR

- [ ] **API Reference**
  - Documentação auto-gerada dos tools
  - Exemplos de cada endpoint

**Impacto:** Onboarding mais fácil, menos suporte

---

## 📈 Métricas de Sucesso

### Objetivos Quantitativos
- [ ] Cobertura de testes > 80%
- [ ] Tempo de resposta < 2s (95th percentile)
- [ ] Zero duplicação de código
- [ ] 100% dos endpoints validados

### Objetivos Qualitativos
- [ ] Type hints em 100% das funções públicas
- [ ] Logs sanitizados (sem dados sensíveis)
- [ ] Documentação completa
- [ ] LLM escolhe tool correto em >95% dos casos

---

## 🤝 Como Contribuir

Para implementar um item deste roadmap:

1. Crie uma issue referenciando o item
2. Faça um fork do projeto
3. Implemente a funcionalidade
4. Adicione testes
5. Atualize a documentação
6. Abra um Pull Request

---

## 📝 Notas

### Decisões Técnicas

**Por que não usar a lib evolutionapi?**
- Biblioteca incompleta (v0.1.2)
- API incompatível com endpoints reais
- HTTP direto dá mais controle

**Por que cache em memória?**
- Simples e eficaz para uso de desktop
- Não precisa de dependências extras
- Limpa automaticamente ao reiniciar

**Por que Pydantic?**
- Validação automática
- Type safety
- Boa integração com FastAPI (futuro)

---

**Última revisão:** 2025-10-23
**Versão:** 1.0.0
