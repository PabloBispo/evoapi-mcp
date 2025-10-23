"""Configuração do MCP Evolution API."""

import sys
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class EvolutionConfig(BaseSettings):
    """Configuração para conexão com Evolution API.

    As variáveis de ambiente necessárias são:
    - EVOLUTION_BASE_URL: URL do servidor Evolution API (ex: http://localhost:8080)
    - EVOLUTION_API_TOKEN: Token de autenticação da API
    - EVOLUTION_INSTANCE_NAME: Nome da instância WhatsApp configurada
    - EVOLUTION_TIMEOUT: (Opcional) Timeout para requisições em segundos (padrão: 30)
    """

    base_url: str = Field(
        ...,
        description="URL base do servidor Evolution API"
    )
    api_token: str = Field(
        ...,
        description="Token de autenticação da API"
    )
    instance_name: str = Field(
        ...,
        description="Nome da instância WhatsApp"
    )
    timeout: int = Field(
        default=30,
        description="Timeout para requisições em segundos",
        ge=5,
        le=300
    )

    model_config = SettingsConfigDict(
        env_prefix="EVOLUTION_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    @field_validator("base_url")
    @classmethod
    def validate_base_url(cls, v: str) -> str:
        """Normaliza a URL base removendo trailing slash."""
        return v.rstrip("/")

    @field_validator("api_token", "instance_name")
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """Valida que campos obrigatórios não estão vazios."""
        if not v or not v.strip():
            raise ValueError("Campo não pode estar vazio")
        return v.strip()


def load_config() -> EvolutionConfig:
    """Carrega e valida a configuração.

    Returns:
        EvolutionConfig: Configuração validada

    Raises:
        ValueError: Se a configuração for inválida
        SystemExit: Se variáveis obrigatórias estiverem faltando
    """
    try:
        config = EvolutionConfig()

        # Log da configuração (sem expor o token)
        print(
            f"Configuração carregada:",
            f"  Base URL: {config.base_url}",
            f"  Instância: {config.instance_name}",
            f"  Timeout: {config.timeout}s",
            sep="\n",
            file=sys.stderr
        )

        return config

    except Exception as e:
        print(
            f"Erro ao carregar configuração: {e}",
            "",
            "Variáveis de ambiente necessárias:",
            "  - EVOLUTION_BASE_URL",
            "  - EVOLUTION_API_TOKEN",
            "  - EVOLUTION_INSTANCE_NAME",
            "",
            "Copie .env.example para .env e configure os valores.",
            sep="\n",
            file=sys.stderr
        )
        sys.exit(1)
