# 🚀 Evolution API MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-1.1.2-green.svg)](https://modelcontextprotocol.io/)

**MCP Server para Evolution API** - Integração completa do WhatsApp com Claude Desktop via Model Context Protocol (MCP).

Este servidor permite que o Claude Desktop interaja com o WhatsApp através da [Evolution API](https://evolution-api.com/), possibilitando envio de mensagens, gerenciamento de conversas, busca de contatos e muito mais.

---

## ✨ Features

### 📤 Envio de Mensagens
- ✅ Mensagens de texto com preview de links
- ✅ Imagens com legendas
- ✅ Vídeos com legendas
- ✅ Documentos (PDF, DOCX, XLSX, etc)
- ✅ Áudios

### 💬 Gerenciamento de Conversas
- ✅ Listar conversas ativas com nomes
- ✅ Buscar mensagens por texto
- ✅ Obter mensagens de conversa específica
- ✅ Enriquecimento automático com nomes de contatos

### 👥 Gerenciamento de Contatos
- ✅ Listar contatos salvos
- ✅ Buscar contatos por ID
- ✅ Obter nome de contato por número
- ✅ Cache inteligente de nomes (5min TTL)

### ⚡ Performance
- ✅ Bulk fetch de contatos (1 request vs N+1)
- ✅ Cache em memória para nomes
- ✅ Enriquecimento automático de chats

### 🛡️ Qualidade
- ✅ Validação de números de telefone
- ✅ Type hints completos
- ✅ Error handling robusto
- ✅ Logs estruturados

---

## 📋 Pré-requisitos

1. **Python 3.10+** (para uso local)
2. **Claude Desktop** instalado (para modo MCP stdio)
3. **Docker & Docker Compose** (para deploy completo)
4. **Instância Evolution API** rodando (ou use nosso Docker Compose)
   - Você precisa de:
     - URL base da API (ex: `https://api.example.com`)
     - API Token (apikey)
     - Nome da instância (instance name)

---

## 🐳 Quick Start com Docker (Recomendado!)

**Deploy completo Evolution API + MCP HTTP Server em 3 comandos:**

```bash
cd docker/
cp .env.docker.example .env.docker
# Edite .env.docker com suas credenciais
docker-compose up -d
```

**Resultado:**
- ✅ PostgreSQL rodando
- ✅ Redis rodando
- ✅ Evolution API em http://localhost:8080
- ✅ MCP HTTP Server em http://localhost:3000
- ✅ Swagger UI em http://localhost:3000/docs

**Documentação completa:** [docker/README.md](docker/README.md)

---

## 🔧 Instalação Local (Modo MCP Stdio)

### 1. Clone o Repositório

```bash
git clone https://github.com/PabloBispo/evoapi-mcp.git
cd evoapi-mcp
```

### 2. Instale as Dependências

```bash
# Usando uv (recomendado)
uv sync

# OU usando pip
pip install -e .
```

### 3. Configure as Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```bash
# Evolution API Configuration
EVOLUTION_BASE_URL=https://your-evolution-api.com
EVOLUTION_API_TOKEN=your-api-token-here
EVOLUTION_INSTANCE_NAME=your-instance-name

# Optional: Timeout (default: 30 seconds)
EVOLUTION_TIMEOUT=30
```

**Exemplo real:**
```bash
EVOLUTION_BASE_URL=https://pevo.ntropy.com.br
EVOLUTION_API_TOKEN=9795FDFBB464-495E-A823-28573A5D39EE
EVOLUTION_INSTANCE_NAME=personal_pablo_bispo_wpp
EVOLUTION_TIMEOUT=15
```

### 4. Configure o Claude Desktop

Edite o arquivo de configuração do Claude Desktop:

**macOS:**
```bash
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows:**
```bash
%APPDATA%\Claude\claude_desktop_config.json
```

Adicione o servidor MCP:

```json
{
  "mcpServers": {
    "evolution-api": {
      "command": "uv",
      "args": [
        "--directory",
        "/caminho/completo/para/evoapi-mcp",
        "run",
        "evoapi-mcp"
      ],
      "env": {
        "EVOLUTION_BASE_URL": "https://your-evolution-api.com",
        "EVOLUTION_API_TOKEN": "your-api-token-here",
        "EVOLUTION_INSTANCE_NAME": "your-instance-name"
      }
    }
  }
}
```

**⚠️ IMPORTANTE:** Use o caminho **absoluto** completo para o diretório do projeto!

### 5. Reinicie o Claude Desktop

Feche completamente (⌘Q no macOS) e reabra o Claude Desktop.

---

## 🎯 Como Usar

### Exemplos de Comandos no Claude Desktop

#### 📤 Enviar Mensagens

```
Envie uma mensagem "Olá! Tudo bem?" para o número 5511999999999
```

```
Envie a imagem https://example.com/foto.jpg com legenda "Confira!" para 5511987654321
```

```
Envie o documento https://example.com/relatorio.pdf para 5511999999999
```

#### 💬 Consultar Conversas

```
Liste as 10 conversas mais recentes do meu WhatsApp
```

```
Mostre as últimas 50 mensagens do número 5511999999999
```

```
Busque mensagens que contenham a palavra "reunião"
```

#### 👥 Gerenciar Contatos

```
Liste os primeiros 20 contatos do meu WhatsApp
```

```
Qual é o nome do contato 5511987654321?
```

```
Mostre informações do contato 5511999999999
```

#### ℹ️ Status da Conexão

```
Verifique o status da conexão do WhatsApp
```

```
Mostre informações da instância
```

---

## 🛠️ Tools Disponíveis

### Envio de Mensagens

| Tool | Descrição | Parâmetros |
|------|-----------|------------|
| `send_text_message` | Envia mensagem de texto | `number`, `text`, `link_preview` |
| `send_image` | Envia imagem | `number`, `image_url`, `caption` |
| `send_video` | Envia vídeo | `number`, `video_url`, `caption` |
| `send_document` | Envia documento | `number`, `document_url`, `filename`, `caption` |
| `send_audio` | Envia áudio | `number`, `audio_url` |

### Conversas e Mensagens

| Tool | Descrição | Parâmetros |
|------|-----------|------------|
| `list_chats` | Lista conversas ativas | `limit` |
| `get_chat_messages` | Obtém mensagens de conversa | `number`, `limit` |
| `find_messages` | Busca mensagens por termo | `query`, `chat_id`, `limit` |

### Contatos

| Tool | Descrição | Parâmetros |
|------|-----------|------------|
| `get_contacts` | Lista contatos salvos | `limit` |
| `find_contact` | Busca contato específico | `contact_id`, `limit` |
| `get_contact_name_by_number` | Obtém nome por número | `number` |

### Status e Presença

| Tool | Descrição | Parâmetros |
|------|-----------|------------|
| `get_connection_status` | Verifica status da conexão | - |
| `get_instance_info` | Informações da instância | - |
| `set_presence` | Define status de presença | `status`, `number` |

---

## 🌐 Modos de Uso

Este projeto suporta **dois modos de operação**:

### 1. Modo Stdio (Claude Desktop)
- Comunicação via stdio (stdin/stdout)
- Integração nativa com Claude Desktop
- Melhor para uso pessoal local
- Configuração em `claude_desktop_config.json`

### 2. Modo HTTP (Docker/Servidor)
- API REST com Swagger UI
- Deploy em containers Docker
- Acesso remoto via HTTP
- Ideal para produção e equipes
- Swagger docs em `/docs`

**Você pode usar ambos simultaneamente!** 🎉

---

## 🔍 Troubleshooting

### ❌ Erro: "ModuleNotFoundError: No module named 'evoapi_mcp'"

**Solução:**
- Verifique se o caminho no `claude_desktop_config.json` é **absoluto** (não relativo)
- Use `pwd` para obter o caminho completo: `cd evoapi-mcp && pwd`

### ❌ Erro: "HTTP 401: Unauthorized"

**Solução:**
- Verifique se o `EVOLUTION_API_TOKEN` está correto
- Confirme que o token tem permissões necessárias

### ❌ Erro: "HTTP 404: Endpoint não encontrado"

**Solução:**
- Verifique se o `EVOLUTION_BASE_URL` está correto
- Confirme se a Evolution API está rodando
- Teste manualmente: `curl https://your-api.com/instance/connectionState/instance-name -H "apikey: your-token"`

### ❌ Os nomes dos contatos não aparecem

**Solução:**
- Reinicie o Claude Desktop para limpar o cache
- Verifique se os contatos estão salvos no WhatsApp
- Cache expira automaticamente após 5 minutos

### ❌ Listagem de conversas muito lenta

**Solução:**
- Já otimizado! Usa bulk fetch de contatos (2 requests ao invés de N+1)
- Se ainda estiver lento, verifique a conexão com a Evolution API

### 🔍 Como Ver os Logs

Os logs aparecem no **stderr** do processo MCP. Para vê-los:

**macOS/Linux:**
```bash
# Logs do Claude Desktop
tail -f ~/Library/Logs/Claude/mcp*.log
```

**Ou rode manualmente para debug:**
```bash
cd evoapi-mcp
uv run evoapi-mcp
# Depois teste chamando tools via stdin
```

---

## 🗺️ Roadmap

Veja o arquivo [ROADMAP.md](ROADMAP.md) para planos futuros:

### 🔴 FASE 1 - Correções Críticas (Curto Prazo)
- [ ] Unificar duplicações de código
- [ ] Adicionar validações robustas
- [ ] Cache com TTL

### 🟡 FASE 2 - Melhorias de Qualidade (Médio Prazo)
- [ ] Type safety com Pydantic
- [ ] Retry logic automático
- [ ] Sanitização de logs

### 🟢 FASE 3 - Novas Funcionalidades (Longo Prazo)
- [ ] Gerenciamento de grupos
- [ ] Deletar/editar mensagens
- [ ] Upload de arquivos locais
- [ ] Download de mídias recebidas
- [ ] Status (stories)

### 🧪 FASE 4 - DevOps
- [ ] Testes automatizados
- [ ] CI/CD com GitHub Actions
- [ ] Documentação completa

---

## 📚 Documentação Adicional

- **[ROADMAP.md](ROADMAP.md)** - Plano de desenvolvimento futuro
- **[TODO.md](TODO.md)** - Tarefas pendentes organizadas
- **[KNOWN_ISSUES.md](KNOWN_ISSUES.md)** - Problemas conhecidos e soluções
- **[FIXES.md](FIXES.md)** - Histórico de correções aplicadas

---

## 🤝 Contribuindo

Contribuições são bem-vindas! 🎉

### Como Contribuir

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/amazing-feature`)
3. Commit suas mudanças (`git commit -m 'Add amazing feature'`)
4. Push para a branch (`git push origin feature/amazing-feature`)
5. Abra um Pull Request

### Diretrizes

- Adicione testes para novas funcionalidades
- Atualize a documentação
- Siga o estilo de código existente
- Use commits semânticos

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 🙏 Agradecimentos

- [Evolution API](https://evolution-api.com/) - API de WhatsApp incrível
- [Model Context Protocol](https://modelcontextprotocol.io/) - Protocolo MCP
- [Anthropic](https://anthropic.com/) - Claude Desktop
- [FastMCP](https://github.com/jlowin/fastmcp) - Framework Python para MCP

---

## 📞 Suporte

- 🐛 **Issues:** [GitHub Issues](https://github.com/PabloBispo/evoapi-mcp/issues)
- 💬 **Discussões:** [GitHub Discussions](https://github.com/PabloBispo/evoapi-mcp/discussions)

---

## ⭐ Star History

Se este projeto foi útil, considere dar uma estrela! ⭐

[![Star History Chart](https://api.star-history.com/svg?repos=PabloBispo/evoapi-mcp&type=Date)](https://star-history.com/#PabloBispo/evoapi-mcp&Date)

---

**Feito com ❤️ usando Claude Code**
