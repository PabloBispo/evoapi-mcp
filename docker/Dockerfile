# Dockerfile para Evolution API MCP Server (HTTP mode)
# Multi-stage build para imagem otimizada

# =============================================================================
# Stage 1: Builder
# =============================================================================
FROM python:3.11-slim as builder

WORKDIR /build

# Instalar dependências de build
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar arquivos de dependências
COPY pyproject.toml ./
COPY README.md ./

# Copiar código fonte
COPY src/ ./src/

# Instalar dependências em virtualenv
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Instalar projeto e dependências
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e .

# =============================================================================
# Stage 2: Runtime
# =============================================================================
FROM python:3.11-slim

# Metadata
LABEL maintainer="Pablo Bispo <pablo@example.com>"
LABEL description="Evolution API MCP Server - HTTP Mode"
LABEL version="1.0.0"

# Instalar apenas runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Criar usuário não-root
RUN useradd -m -u 1000 evoapi && \
    mkdir -p /app && \
    chown -R evoapi:evoapi /app

# Copiar virtualenv do builder
COPY --from=builder /opt/venv /opt/venv

# Copiar código fonte
COPY --chown=evoapi:evoapi src/ /app/src/
COPY --chown=evoapi:evoapi pyproject.toml /app/
COPY --chown=evoapi:evoapi README.md /app/

WORKDIR /app

# Configurar PATH para usar virtualenv
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Mudar para usuário não-root
USER evoapi

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

# Expor porta HTTP
EXPOSE 3000

# Comando padrão: rodar servidor HTTP
CMD ["uvicorn", "evoapi_mcp.http_server:app", "--host", "0.0.0.0", "--port", "3000"]
