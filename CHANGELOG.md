# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

---

## [1.0.0] - 2025-10-24

### 🎉 Primeira Release Estável!

Esta é a primeira release production-ready do Evolution API MCP Server, com todas as issues críticas resolvidas e funcionalidade completa.

### ✨ Adicionado

#### Core Features
- **14 ferramentas MCP** para integração completa com WhatsApp via Evolution API:
  - `get_chats` - Lista conversas recentes com enriquecimento de nomes
  - `get_contacts` - Busca contatos (unificado com filtros opcionais)
  - `get_messages` - Busca mensagens de uma conversa
  - `send_text` - Envia mensagens de texto
  - `send_media` - Envia mídias (imagem, vídeo, documento, áudio)
  - `get_instance_status` - Status da instância
  - `set_presence` - Define presença (online, offline, etc)
  - `mark_as_read` - Marca mensagem como lida
  - `archive_chat` - Arquiva conversa
  - `delete_chat` - Deleta conversa
  - `get_profile_picture` - Busca foto de perfil
  - `get_profile_status` - Busca status/bio
  - `check_number` - Verifica se número está no WhatsApp
  - `get_business_profile` - Busca perfil comercial

#### Otimizações de Performance
- **Cache inteligente de contatos** com TTL de 5 minutos
- **Enriquecimento automático** de nomes em conversas (bulk fetch)
- **Método `clear_cache()`** para limpeza manual do cache
- Redução de N+1 requests para 2 requests fixos

#### Validações Robustas
- Validação de `media_type` contra tipos permitidos
- Validação de URLs (HTTP/HTTPS) para mídias
- Validação de tamanho de texto (65KB limit do WhatsApp)
- Validação de tamanho de caption (1024 caracteres)
- Mensagens de erro descritivas antes de chamar a API

#### Documentação Completa
- README.md com instalação, configuração e exemplos
- ROADMAP.md com plano de desenvolvimento de 4 fases
- TODO.md com tarefas granulares
- KNOWN_ISSUES.md com issues documentadas e soluções
- LICENSE (MIT)
- Este CHANGELOG.md

### 🔧 Corrigido

#### Issue #1: Duplicação de Código ✅
- **Problema:** Funções `fetch_contacts()` e `find_contacts()` duplicadas
- **Solução:** Unificadas em `fetch_contacts(contact_id=None)`
- **Impacto:** Código mais limpo, menos confusão para LLM

#### Issue #2: Cache Sem Expiração ✅
- **Problema:** Cache de nomes nunca expirava, causando nomes desatualizados
- **Solução:** Implementado TTL de 5 minutos com auto-refresh
- **Impacto:** Nomes sempre atualizados sem necessidade de restart

#### Issue #3: Validações Ausentes ✅
- **Problema:** Validações só na API, erros tardios e genéricos
- **Solução:** Validações client-side com mensagens descritivas
- **Impacto:** Erros detectados imediatamente com feedback claro

#### Issue #4: Endpoint Incorreto de Contatos ✅
- **Problema:** Endpoint `/chat/contacts/{instanceId}` retornava 404
- **Solução:** Corrigido para `/chat/findContacts/{instanceId}`
- **Impacto:** Nomes de contatos aparecendo corretamente

#### Issue #5: Formato de Resposta Incorreto ✅
- **Problema:** Esperava `{"data": [...]}` mas recebia lista direta
- **Solução:** Atualizado parsing para aceitar lista direta
- **Impacto:** 923 contatos detectados e 922 nomes mapeados

### 🧪 Testado

- **Suite de testes automáticos** (`test_phase1.py`)
- **11 testes, 100% de sucesso:**
  - 6 testes de validação
  - 3 testes de cache
  - 2 testes de deduplicação
- Testado com instância real (1170+ contatos)

### 📚 Documentação

#### Arquivos Criados
- `README.md` - Guia completo de uso
- `ROADMAP.md` - Planejamento de 4 fases
- `TODO.md` - Tarefas granulares
- `KNOWN_ISSUES.md` - Documentação de issues
- `LICENSE` - MIT License
- `CHANGELOG.md` - Este arquivo

#### Documentação de Código
- Docstrings completas em todas funções
- Type hints em Python 3.10+
- Exemplos de uso em docstrings
- Comentários explicativos em lógica complexa

### 🏗️ Estrutura Técnica

```
evoapi-mcp/
├── src/evoapi_mcp/
│   ├── __init__.py
│   ├── server.py        # MCP Server (14 tools)
│   ├── client.py        # HTTP Client com validações
│   └── config.py        # Configuração
├── test_phase1.py       # Suite de testes
├── README.md
├── ROADMAP.md
├── TODO.md
├── KNOWN_ISSUES.md
├── CHANGELOG.md
├── LICENSE
└── pyproject.toml
```

### 🔒 Segurança

- API key nunca exposta em logs
- Validação de URLs para prevenir SSRF
- Validação de inputs antes de processar
- Timeout configurável para prevenir DoS

### 📦 Dependências

- `fastmcp >= 0.6.0` - Framework MCP
- `requests >= 2.32.3` - HTTP client
- `python-dotenv >= 1.0.1` - Gerenciamento de .env

### 🎯 Compatibilidade

- **Python:** 3.10+
- **Evolution API:** v2.x
- **Claude Desktop:** Latest
- **OS:** macOS, Linux, Windows

### 📊 Estatísticas

- **14 ferramentas MCP** implementadas
- **5 issues críticas** resolvidas
- **1170+ contatos** testados em produção
- **922 nomes** enriquecidos automaticamente
- **100% testes** passando

---

## [0.1.0] - 2025-10-23

### Versão Inicial (Pré-Release)

- Implementação inicial do MCP Server
- Integração básica com Evolution API
- 14 ferramentas funcionais
- Documentação básica

---

## Links

- [GitHub Repository](https://github.com/PabloBispo/evoapi-mcp)
- [Evolution API Documentation](https://doc.evolution-api.com/)
- [Model Context Protocol](https://modelcontextprotocol.io/)

---

## Convenções de Versionamento

Este projeto usa [Semantic Versioning](https://semver.org/):

- **MAJOR** (1.x.x): Mudanças incompatíveis na API
- **MINOR** (x.1.x): Novas funcionalidades compatíveis
- **PATCH** (x.x.1): Correções de bugs compatíveis

## Tipos de Mudanças

- `Adicionado` - Novas funcionalidades
- `Modificado` - Mudanças em funcionalidades existentes
- `Descontinuado` - Funcionalidades que serão removidas
- `Removido` - Funcionalidades removidas
- `Corrigido` - Correções de bugs
- `Segurança` - Correções de vulnerabilidades
