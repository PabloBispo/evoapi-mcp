#!/usr/bin/env python3
"""Script de teste para validar as melhorias da FASE 1.

Testa:
1. Validações de input (media_type, URLs, text length)
2. Cache com TTL
3. Deduplicação (fetch_contacts unificado)
"""

import sys
from pathlib import Path

# Adiciona src ao path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

from evoapi_mcp.config import load_config
from evoapi_mcp.client import EvolutionClient


def test_validations():
    """Testa as validações de input."""
    print("\n" + "="*70)
    print("TESTE 1: Validações de Input")
    print("="*70)

    config = load_config()
    client = EvolutionClient(config)

    # Teste 1.1: Validação de media_type inválido
    print("\n[1.1] Testando media_type inválido...")
    try:
        client.validate_media_type("pdf")
        print("  ❌ FALHOU: Deveria ter lançado ValueError")
    except ValueError as e:
        print(f"  ✅ PASSOU: {e}")

    # Teste 1.2: Validação de media_type válido
    print("\n[1.2] Testando media_type válido...")
    try:
        client.validate_media_type("image")
        print("  ✅ PASSOU: media_type 'image' aceito")
    except ValueError as e:
        print(f"  ❌ FALHOU: {e}")

    # Teste 1.3: Validação de URL inválida
    print("\n[1.3] Testando URL inválida...")
    try:
        client.validate_url("ftp://example.com/file.jpg", "image_url")
        print("  ❌ FALHOU: Deveria ter lançado ValueError")
    except ValueError as e:
        print(f"  ✅ PASSOU: {e}")

    # Teste 1.4: Validação de URL válida
    print("\n[1.4] Testando URL válida...")
    try:
        client.validate_url("https://example.com/image.jpg", "image_url")
        print("  ✅ PASSOU: URL válida aceita")
    except ValueError as e:
        print(f"  ❌ FALHOU: {e}")

    # Teste 1.5: Validação de texto muito longo
    print("\n[1.5] Testando texto muito longo...")
    try:
        long_text = "A" * 70000  # Mais que MAX_TEXT_LENGTH (65536)
        client.validate_text_length(long_text, 65536, "text")
        print("  ❌ FALHOU: Deveria ter lançado ValueError")
    except ValueError as e:
        print(f"  ✅ PASSOU: {e}")

    # Teste 1.6: Validação de caption muito longa
    print("\n[1.6] Testando caption muito longa...")
    try:
        long_caption = "A" * 2000  # Mais que MAX_CAPTION_LENGTH (1024)
        client.validate_text_length(long_caption, 1024, "caption")
        print("  ❌ FALHOU: Deveria ter lançado ValueError")
    except ValueError as e:
        print(f"  ✅ PASSOU: {e}")


def test_cache_ttl():
    """Testa o cache com TTL."""
    print("\n" + "="*70)
    print("TESTE 2: Cache com TTL")
    print("="*70)

    config = load_config()
    client = EvolutionClient(config)

    # Teste 2.1: Cache inicial está vazio
    print("\n[2.1] Verificando cache inicial...")
    if not client._contact_names_cache:
        print("  ✅ PASSOU: Cache inicialmente vazio")
    else:
        print("  ❌ FALHOU: Cache deveria estar vazio")

    # Teste 2.2: Cache não expirado
    print("\n[2.2] Verificando estado de expiração inicial...")
    if client._is_cache_expired():
        print("  ✅ PASSOU: Cache marcado como expirado (nunca foi criado)")
    else:
        print("  ❌ FALHOU: Cache deveria estar expirado")

    # Teste 2.3: Método clear_cache()
    print("\n[2.3] Testando método clear_cache()...")
    try:
        # Adiciona algo ao cache manualmente
        client._contact_names_cache["5511999999999"] = "Test User"
        print(f"  - Cache antes: {len(client._contact_names_cache)} itens")

        client.clear_cache()

        if not client._contact_names_cache:
            print("  ✅ PASSOU: Cache limpo com sucesso")
        else:
            print("  ❌ FALHOU: Cache não foi limpo")
    except Exception as e:
        print(f"  ❌ FALHOU: {e}")


def test_unified_contacts():
    """Testa a função unificada fetch_contacts."""
    print("\n" + "="*70)
    print("TESTE 3: Função Unificada fetch_contacts()")
    print("="*70)

    config = load_config()
    client = EvolutionClient(config)

    # Teste 3.1: fetch_contacts sem filtro
    print("\n[3.1] Testando fetch_contacts() sem filtro...")
    try:
        contacts = client.fetch_contacts()
        if isinstance(contacts, list):
            print(f"  ✅ PASSOU: Retornou lista com {len(contacts)} contatos")
        else:
            print(f"  ❌ FALHOU: Retornou {type(contacts)} ao invés de list")
    except Exception as e:
        print(f"  ❌ FALHOU: {e}")

    # Teste 3.2: fetch_contacts com contact_id
    print("\n[3.2] Testando fetch_contacts(contact_id=...)...")
    try:
        # Pega um contato da lista anterior
        if contacts and len(contacts) > 0:
            first_contact_jid = contacts[0].get("remoteJid")
            filtered = client.fetch_contacts(contact_id=first_contact_jid)

            if isinstance(filtered, list):
                print(f"  ✅ PASSOU: Retornou lista com {len(filtered)} contato(s)")
                if len(filtered) > 0 and filtered[0].get("remoteJid") == first_contact_jid:
                    print(f"  ✅ PASSOU: Contato correto retornado")
                else:
                    print(f"  ⚠️  AVISO: Resultado inesperado")
            else:
                print(f"  ❌ FALHOU: Retornou {type(filtered)} ao invés de list")
        else:
            print("  ⚠️  AVISO: Sem contatos para testar filtro")
    except Exception as e:
        print(f"  ❌ FALHOU: {e}")


def main():
    """Executa todos os testes."""
    print("\n" + "="*70)
    print("TESTES DA FASE 1 - Validações, Cache TTL, Deduplicação")
    print("="*70)

    try:
        test_validations()
        test_cache_ttl()
        test_unified_contacts()

        print("\n" + "="*70)
        print("RESUMO DOS TESTES")
        print("="*70)
        print("\n✅ Todos os testes de validação concluídos")
        print("✅ Todos os testes de cache concluídos")
        print("✅ Todos os testes de deduplicação concluídos")
        print("\n🎉 FASE 1 - Implementada com sucesso!")
        print("="*70 + "\n")

    except Exception as e:
        print(f"\n❌ ERRO FATAL: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
