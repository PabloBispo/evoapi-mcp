# 🐳 Evolution API MCP Server - Docker Deployment

Deploy completo da stack Evolution API + MCP HTTP Server usando Docker Compose.

---

## 📦 O que está incluído

Esta stack Docker Compose contém:

- **PostgreSQL 15** - Banco de dados para Evolution API
- **Redis 7** - Cache e queue para otimização
- **Evolution API** - Gateway WhatsApp oficial
- **MCP HTTP Server** - Nosso servidor com API REST

---

## 🚀 Quick Start

### 1. Preparar Ambiente

```bash
# Navegar para o diretório docker
cd docker/

# Copiar template de variáveis de ambiente
cp .env.docker.example .env.docker

# Editar com suas credenciais
nano .env.docker  # ou vim, code, etc
```

### 2. Gerar Credenciais Seguras

```bash
# Gerar senha PostgreSQL
openssl rand -base64 24

# Gerar API Key
openssl rand -hex 32

# Gerar senha Redis
openssl rand -base64 24
```

Copie e cole as senhas geradas no arquivo `.env.docker`.

### 3. Iniciar Stack

```bash
# Iniciar todos os serviços
docker-compose up -d

# Ver logs em tempo real
docker-compose logs -f

# Ver logs de um serviço específico
docker-compose logs -f evolution-api
docker-compose logs -f evoapi-mcp-http
```

### 4. Verificar Status

```bash
# Ver status dos containers
docker-compose ps

# Ver saúde dos serviços
docker-compose ps
```

**Saída esperada:**
```
NAME                  STATUS         PORTS
evolution-postgres    Up (healthy)   5432/tcp
evolution-redis       Up (healthy)   6379/tcp
evolution-api         Up (healthy)   0.0.0.0:8080->8080/tcp
evoapi-mcp-http       Up (healthy)   0.0.0.0:3000->3000/tcp
```

---

## 🔧 Primeira Configuração

### Acessar Evolution API Manager

Abra no navegador: http://localhost:8080

O Evolution API possui uma interface web básica para gerenciar instâncias.

### Criar Instância WhatsApp (via API)

```bash
# Criar instância chamada "default_instance"
curl -X POST http://localhost:8080/instance/create \
  -H "apikey: SUA_API_KEY_AQUI" \
  -H "Content-Type: application/json" \
  -d '{
    "instanceName": "default_instance",
    "qrcode": true,
    "integration": "WHATSAPP-BAILEYS"
  }'
```

**Resposta esperada:**
```json
{
  "instance": {
    "instanceName": "default_instance",
    "status": "created"
  },
  "qrcode": {
    "code": "data:image/png;base64,..."
  }
}
```

### Conectar WhatsApp (QR Code)

```bash
# Buscar QR Code
curl http://localhost:8080/instance/connect/default_instance \
  -H "apikey: SUA_API_KEY_AQUI"
```

**O QR code será retornado em base64.** Você pode:

1. **Via Browser:** Colar o base64 em https://codebeautify.org/base64-to-image-converter
2. **Via Terminal:** Salvar como imagem e abrir
3. **Via Evolution API UI:** Acessar http://localhost:8080

**Escaneie o QR code com WhatsApp:**
- WhatsApp → Configurações → Aparelhos conectados → Conectar aparelho

---

## 📡 Testar MCP HTTP Server

### Health Check

```bash
curl http://localhost:3000/health
```

**Resposta:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "instance": "default_instance"
}
```

### API Documentation (Swagger)

Abra no navegador: http://localhost:3000/docs

Você verá todos os 14 endpoints disponíveis com documentação interativa!

### Enviar Mensagem de Teste

```bash
curl -X POST http://localhost:3000/messages/text \
  -H "Content-Type: application/json" \
  -d '{
    "number": "5511999999999",
    "text": "Olá! Mensagem de teste via MCP HTTP 🚀",
    "link_preview": true
  }'
```

### Listar Contatos

```bash
curl http://localhost:3000/contacts?limit=10
```

### Buscar Conversas

```bash
curl http://localhost:3000/chats?limit=20
```

---

## 🔌 URLs e Portas

| Serviço | URL | Descrição |
|---------|-----|-----------|
| **Evolution API** | http://localhost:8080 | WhatsApp Gateway |
| **MCP HTTP API** | http://localhost:3000 | Nosso servidor REST |
| **MCP Swagger UI** | http://localhost:3000/docs | Documentação interativa |
| **MCP ReDoc** | http://localhost:3000/redoc | Documentação alternativa |
| **PostgreSQL** | localhost:5432 | Database (interno) |
| **Redis** | localhost:6379 | Cache (interno) |

---

## 📋 Comandos Úteis

### Gerenciar Containers

```bash
# Parar todos os serviços
docker-compose down

# Parar e remover volumes (⚠️  APAGA DADOS!)
docker-compose down -v

# Reiniciar serviço específico
docker-compose restart evoapi-mcp-http

# Rebuild após mudanças no código
docker-compose up -d --build evoapi-mcp-http

# Ver recursos consumidos
docker stats
```

### Ver Logs

```bash
# Logs de todos os serviços
docker-compose logs -f

# Logs de serviço específico (últimas 100 linhas)
docker-compose logs --tail=100 -f evolution-api

# Logs sem follow
docker-compose logs evoapi-mcp-http
```

### Inspecionar Containers

```bash
# Entrar no container do MCP
docker exec -it evoapi-mcp-http /bin/sh

# Entrar no PostgreSQL
docker exec -it evolution-postgres psql -U evolution -d evolution

# Ver variáveis de ambiente
docker exec evoapi-mcp-http env
```

### Gerenciar Volumes

```bash
# Listar volumes
docker volume ls | grep evolution

# Inspecionar volume
docker volume inspect evolution_postgres_data

# Backup do banco PostgreSQL
docker exec evolution-postgres pg_dump -U evolution evolution > backup.sql

# Restaurar backup
cat backup.sql | docker exec -i evolution-postgres psql -U evolution evolution
```

---

## 🔒 Segurança

### Variáveis de Ambiente Sensíveis

**NUNCA commite o arquivo `.env.docker`!**

Ele já está no `.gitignore`, mas sempre verifique:

```bash
git status
# .env.docker NÃO deve aparecer
```

### Alterar Credenciais

Se precisar alterar credenciais após deploy:

```bash
# 1. Parar stack
docker-compose down

# 2. Editar .env.docker
nano .env.docker

# 3. Recriar containers (sem apagar volumes)
docker-compose up -d --force-recreate
```

### Produção

Para ambientes de produção:

1. **Use HTTPS** - Configure reverse proxy (Nginx/Traefik)
2. **Firewall** - Bloqueie portas não essenciais
3. **Secrets** - Use Docker Secrets ou Vault
4. **Backup** - Configure backup automático dos volumes
5. **Monitoring** - Adicione Prometheus + Grafana

---

## 🐛 Troubleshooting

### Container não inicia

```bash
# Ver logs de erro
docker-compose logs evolution-api

# Verificar healthcheck
docker inspect evolution-api | grep Health -A 10

# Verificar conectividade
docker exec evoapi-mcp-http curl -f http://evolution-api:8080/health
```

### PostgreSQL não conecta

```bash
# Verificar se está rodando
docker-compose ps postgres

# Testar conexão
docker exec evolution-postgres pg_isready -U evolution

# Ver logs
docker-compose logs postgres
```

### Evolution API retorna 401

```bash
# Verificar se API key está correta
echo $EVOLUTION_API_KEY

# Deve ser a mesma em .env.docker
cat .env.docker | grep EVOLUTION_API_KEY
```

### QR Code expirou

```bash
# Buscar novo QR code
curl http://localhost:8080/instance/connect/default_instance \
  -H "apikey: SUA_API_KEY"
```

### MCP HTTP retorna 503

```bash
# Verificar se Evolution API está pronto
curl http://evolution-api:8080/health

# Verificar logs do MCP
docker-compose logs evoapi-mcp-http

# Reiniciar MCP
docker-compose restart evoapi-mcp-http
```

### Resetar tudo (⚠️  APAGA DADOS!)

```bash
# Parar e remover tudo
docker-compose down -v

# Remover imagens
docker-compose down --rmi all

# Iniciar do zero
docker-compose up -d
```

---

## 📊 Monitoramento

### Ver métricas

```bash
# CPU, memória, network, disco
docker stats

# Apenas containers desta stack
docker stats $(docker-compose ps -q)
```

### Healthchecks

```bash
# Ver status de saúde
docker inspect evolution-api | jq '.[0].State.Health'

# Ver últimos checks
docker inspect evoapi-mcp-http | jq '.[0].State.Health.Log[-3:]'
```

---

## 🔄 Atualizar Stack

### Atualizar Evolution API

```bash
# Baixar nova versão
docker pull atendai/evolution-api:latest

# Recriar container
docker-compose up -d evolution-api
```

### Atualizar MCP HTTP

```bash
# Rebuild após mudar código
docker-compose up -d --build evoapi-mcp-http
```

---

## 💾 Backup e Restore

### Backup Completo

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

# Backup PostgreSQL
docker exec evolution-postgres pg_dump -U evolution evolution > $BACKUP_DIR/postgres.sql

# Backup volumes
docker run --rm \
  -v evolution_instances:/data \
  -v $BACKUP_DIR:/backup \
  alpine tar czf /backup/instances.tar.gz -C /data .

echo "✅ Backup salvo em: $BACKUP_DIR"
```

### Restore

```bash
#!/bin/bash
# restore.sh

BACKUP_DIR=$1

# Restore PostgreSQL
cat $BACKUP_DIR/postgres.sql | docker exec -i evolution-postgres psql -U evolution evolution

# Restore instances
docker run --rm \
  -v evolution_instances:/data \
  -v $BACKUP_DIR:/backup \
  alpine tar xzf /backup/instances.tar.gz -C /data

echo "✅ Restore concluído!"
```

---

## 📚 Referências

- [Evolution API Docs](https://doc.evolution-api.com/)
- [Docker Compose Docs](https://docs.docker.com/compose/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)

---

## 🆘 Suporte

Problemas? Abra uma issue: https://github.com/PabloBispo/evoapi-mcp/issues

---

**Feito com ❤️ por Pablo Bispo**
