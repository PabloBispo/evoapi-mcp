# Evolution API MCP Server

MCP Server para integração com [Evolution API](https://evolution-api.com/), permitindo envio e gerenciamento de mensagens WhatsApp através do Claude.

## Características

- ✅ Envio de mensagens de texto
- ✅ Envio de mídia (imagens, vídeos, documentos, áudios)
- ✅ Envio de localização e contatos
- ✅ Listagem de chats e mensagens
- ✅ Consulta de mensagens não lidas
- ✅ Gerenciamento de presença (online/offline)
- ✅ Validação automática de números de telefone
- ✅ Tratamento robusto de erros
- ✅ Logging detalhado

## Pré-requisitos

- Python 3.10 ou superior
- [uv](https://github.com/astral-sh/uv) (gerenciador de pacotes Python)
- Servidor Evolution API configurado e rodando
- Token de autenticação da Evolution API
- Uma instância WhatsApp criada e conectada

## Instalação

### 1. Clone ou baixe o projeto

```bash
cd /caminho/para/evoapi-mcp
```

### 2. Configure as variáveis de ambiente

Copie o arquivo de exemplo e edite com suas credenciais:

```bash
cp .env.example .env
```

Edite o arquivo `.env`:

```env
EVOLUTION_BASE_URL=http://localhost:8080
EVOLUTION_API_TOKEN=seu-token-aqui
EVOLUTION_INSTANCE_NAME=minha-instancia
```

**Importante:**
- `EVOLUTION_BASE_URL`: URL do seu servidor Evolution API
- `EVOLUTION_API_TOKEN`: Token de autenticação (API Key)
- `EVOLUTION_INSTANCE_NAME`: Nome da instância WhatsApp (deve estar criada e conectada)

### 3. Instale as dependências

```bash
uv sync
```

### 4. Teste localmente (opcional)

Antes de instalar no Claude Desktop, você pode testar o servidor:

```bash
uv run mcp dev src/evoapi_mcp/server.py
```

Isso abrirá uma interface web onde você pode testar os tools disponíveis.

### 5. Instale no Claude Desktop

```bash
uv run mcp install src/evoapi_mcp/server.py
```

Ou configure manualmente editando `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) ou `%APPDATA%/Claude/claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "evolution-api": {
      "command": "uv",
      "args": [
        "run",
        "mcp",
        "run",
        "/caminho/completo/para/evoapi-mcp/src/evoapi_mcp/server.py"
      ],
      "env": {
        "EVOLUTION_BASE_URL": "http://localhost:8080",
        "EVOLUTION_API_TOKEN": "seu-token-aqui",
        "EVOLUTION_INSTANCE_NAME": "minha-instancia"
      }
    }
  }
}
```

**Nota:** Substitua `/caminho/completo/para/evoapi-mcp` pelo caminho absoluto do projeto.

### 6. Reinicie o Claude Desktop

Após a instalação, reinicie o Claude Desktop para carregar o servidor MCP.

## Uso

### Enviando mensagens de texto

```
Claude, envie uma mensagem de texto para 5511999999999 dizendo "Olá! Tudo bem?"
```

### Enviando imagens

```
Claude, envie a imagem https://example.com/imagem.jpg para 5511999999999 com a legenda "Confira isso!"
```

### Enviando documentos

```
Claude, envie o documento https://example.com/relatorio.pdf para 5511999999999
```

### Consultando mensagens não lidas

```
Claude, quais são as minhas mensagens não lidas no WhatsApp?
```

### Listando conversas

```
Claude, liste minhas últimas 20 conversas do WhatsApp
```

### Obtendo mensagens de uma conversa

```
Claude, mostre as últimas 30 mensagens da conversa com o número 5511888888888
```

### Alterando presença

```
Claude, fique online no WhatsApp
```
ou
```
Claude, fique offline no WhatsApp
```

## Tools Disponíveis

### Envio de Mensagens

- **send_text_message** - Envia mensagem de texto
- **send_image** - Envia imagem
- **send_document** - Envia documento (PDF, DOCX, XLSX, etc.)
- **send_video** - Envia vídeo
- **send_audio** - Envia áudio
- **send_location** - Envia localização geográfica
- **send_contact** - Envia contato

### Gerenciamento de Chats

- **list_chats** - Lista conversas ativas
- **get_chat_messages** - Obtém mensagens de uma conversa
- **get_chat_by_number** - Obtém chat_id a partir de um número
- **get_unread_messages** - Lista mensagens não lidas
- **mark_chat_as_read** - Marca chat como lido

### Status e Presença

- **get_connection_status** - Verifica status da conexão
- **set_presence** - Define presença (available/unavailable/composing/recording)
- **get_instance_info** - Obtém informações da instância

## Formato de Números

Todos os números devem estar no formato internacional **sem o sinal de '+'**:

✅ Correto: `5511999999999` (Brasil)
✅ Correto: `1234567890` (EUA)
❌ Errado: `+5511999999999`
❌ Errado: `(11) 99999-9999`

O servidor normaliza automaticamente os números removendo caracteres não numéricos.

## Troubleshooting

### Erro: "Instância desconectada"

A instância WhatsApp perdeu a conexão. Soluções:

1. Verifique se o servidor Evolution API está rodando
2. Reconecte a instância via interface web da Evolution API
3. Use `get_connection_status()` para verificar o estado

### Erro: "Falha de autenticação"

Token de API inválido. Verifique:

1. O token no `.env` está correto
2. O token não expirou
3. O servidor Evolution API está acessível

### Erro: "Número inválido"

O número de telefone não está no formato correto. Use formato internacional sem '+':
- Brasil: `5511999999999`
- EUA: `1234567890`

### Erro: "Timeout"

Operação demorou muito. Possíveis causas:

1. Servidor Evolution API lento ou sobrecarregado
2. Conexão de rede instável
3. Arquivo de mídia muito grande

Solução: Aumente o timeout no `.env`:

```env
EVOLUTION_TIMEOUT=60
```

### Logs do servidor

Os logs do servidor MCP são enviados para `stderr`. Para visualizar:

- macOS/Linux: Verifique o Console do sistema ou logs do Claude Desktop
- Windows: Verifique o Visualizador de Eventos

## Desenvolvimento

### Estrutura do projeto

```
evoapi-mcp/
├── src/
│   └── evoapi_mcp/
│       ├── __init__.py
│       ├── server.py      # Servidor MCP com todos os tools
│       ├── config.py       # Configuração e validação
│       └── client.py       # Wrapper do EvolutionClient
├── tests/                  # Testes (futuro)
├── pyproject.toml          # Dependências e configuração
├── .env.example            # Template de configuração
└── README.md              # Esta documentação
```

### Executando testes

```bash
# Instalar dependências de desenvolvimento
uv sync --dev

# Rodar testes (quando implementados)
uv run pytest
```

### Contribuindo

Contribuições são bem-vindas! Por favor:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## Notas Importantes

### TODOs

Alguns métodos da Evolution API precisam ser verificados/ajustados conforme a API exata da biblioteca `evolutionapi`:

- `send_location()` - Verificar parâmetros corretos
- `send_contact()` - Verificar formato de contato
- `list_chats()` - Verificar estrutura de retorno
- `get_chat_messages()` - Verificar paginação
- `get_unread_messages()` - Verificar formato de retorno
- `set_presence()` - Verificar valores válidos de status

Consulte a [documentação da Evolution API](https://doc.evolution-api.com/) para detalhes específicos.

### Segurança

- **Nunca** commite o arquivo `.env` com suas credenciais
- **Nunca** exponha seu token de API publicamente
- Use HTTPS para o `EVOLUTION_BASE_URL` em produção
- Mantenha seu servidor Evolution API protegido por firewall

## Recursos

- [Evolution API](https://evolution-api.com/) - Site oficial
- [Documentação Evolution API](https://doc.evolution-api.com/)
- [Cliente Python Evolution API](https://github.com/EvolutionAPI/evolution-client-python)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)

## Licença

Este projeto é fornecido "como está", sem garantias. Use por sua conta e risco.

## Suporte

Para problemas ou dúvidas:

1. Verifique a seção [Troubleshooting](#troubleshooting)
2. Consulte a [documentação da Evolution API](https://doc.evolution-api.com/)
3. Abra uma issue no repositório do projeto

---

Desenvolvido para uso com Claude Desktop e Evolution API.
