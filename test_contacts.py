#!/usr/bin/env python3
"""Testa o retorno da API de contatos."""

import sys
from pathlib import Path

src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

from evoapi_mcp.config import load_config
from evoapi_mcp.client import EvolutionClient

config = load_config()
client = EvolutionClient(config)

print("\n=== Testando fetch_contacts() ===")
result = client.fetch_contacts()

print(f"\nTipo do resultado: {type(result)}")
print(f"Keys do resultado: {result.keys() if isinstance(result, dict) else 'N/A'}")

if isinstance(result, dict):
    if "data" in result:
        print(f"Número de contatos em 'data': {len(result['data'])}")
        if result['data']:
            print(f"\nPrimeiro contato: {result['data'][0]}")
    else:
        print(f"Resultado não tem 'data'. Keys: {list(result.keys())[:10]}")
elif isinstance(result, list):
    print(f"Resultado é uma lista com {len(result)} itens")
    if result:
        print(f"\nPrimeiro item: {result[0]}")

print("\n=== Testando _build_contacts_map() ===")
contacts_map = client._build_contacts_map()
print(f"Contatos no mapa: {len(contacts_map)}")
if contacts_map:
    # Mostra os primeiros 5
    for i, (number, name) in enumerate(list(contacts_map.items())[:5]):
        print(f"  {number}: {name}")
