# Guia de Instalação no Claude Desktop

## Passo 1: Verifique a Configuração

Seu arquivo `.env` já está configurado com:
- **URL**: https://pevo.ntropy.com.br
- **Instância**: personal_pablo_bispo_wpp
- **Token**: Configurado

## Passo 2: Instale no Claude Desktop

Execute o comando:

```bash
uv run mcp install src/evoapi_mcp/server.py
```

**Ou** configure manualmente:

### macOS

Edite `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "evolution-api": {
      "command": "uv",
      "args": [
        "run",
        "mcp",
        "run",
        "/Users/pablofernando/projects/mcp/evoapi-mcp/src/evoapi_mcp/server.py"
      ],
      "env": {
        "EVOLUTION_BASE_URL": "https://pevo.ntropy.com.br",
        "EVOLUTION_API_TOKEN": "9795FDFBB464-495E-A823-28573A5D39EE",
        "EVOLUTION_INSTANCE_NAME": "personal_pablo_bispo_wpp",
        "EVOLUTION_TIMEOUT": "30"
      }
    }
  }
}
```

### Windows

Edite `%APPDATA%/Claude/claude_desktop_config.json` com a configuração acima (ajuste o caminho do projeto).

## Passo 3: Reinicie o Claude Desktop

Feche completamente e abra o Claude Desktop novamente.

## Passo 4: Teste

No Claude Desktop, você pode testar com:

```
Verifique o status da minha conexão WhatsApp
```

Ou:

```
Envie uma mensagem de teste para 5511999999999 dizendo "Olá!"
```

## Verificando se Funcionou

1. Abra o Claude Desktop
2. Procure pelo ícone de ferramentas (🔧) ou o indicador de MCP servers
3. Você deverá ver "evolution-api" listado
4. Todos os tools disponíveis estarão acessíveis

## Troubleshooting

### Server não aparece

1. Verifique se o arquivo `claude_desktop_config.json` está correto
2. Verifique se o caminho do projeto está absoluto (não relativo)
3. Reinicie o Claude Desktop completamente

### Erro de autenticação

1. Verifique se o token está correto no `.env` ou no config
2. Verifique se a instância `personal_pablo_bispo_wpp` existe e está ativa

### Instância desconectada

1. Acesse https://pevo.ntropy.com.br
2. Faça login
3. Reconecte a instância se necessário

## Comandos Úteis

### Testar localmente (modo dev)

```bash
cd /Users/pablofernando/projects/mcp/evoapi-mcp
uv run mcp dev src/evoapi_mcp/server.py
```

Isso abrirá uma interface web onde você pode testar os tools.

### Ver logs

Os logs do servidor aparecem no stderr. Para ver:

```bash
# macOS
tail -f ~/Library/Logs/Claude/mcp*.log
```

### Desinstalar

Se precisar desinstalar:

```bash
uv run mcp uninstall evolution-api
```

Ou remova manualmente a seção do `claude_desktop_config.json`.

## Próximos Passos

1. ✅ Configuração completa
2. ✅ Dependências instaladas
3. ⬜ Instalar no Claude Desktop
4. ⬜ Reiniciar Claude Desktop
5. ⬜ Testar envio de mensagem
6. ⬜ Explorar outros tools

## Documentação Completa

Veja o [README.md](README.md) para:
- Lista completa de tools
- Exemplos de uso
- Troubleshooting detalhado
- Formato de números de telefone

---

**Nota de Segurança:** Nunca compartilhe seu `.env` ou token de API publicamente. O arquivo `.env` está no `.gitignore` para sua segurança.
