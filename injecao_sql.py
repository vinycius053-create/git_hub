import asyncio
import httpx

BASE_URL = "https://acheirepublica.com"

# Payloads clássicos de SQL Injection para testar parâmetros de texto
SQL_INJECTION_PAYLOADS = [
    ("Bypass básico com OR", {"address": "' OR '1'='1", "number": "1", "city": "Pouso Alegre", "state": "MG"}),
    ("Comando UNION SELECT", {"address": "Rua Teste' UNION SELECT null, null, null--", "number": "1", "city": "Pouso Alegre", "state": "MG"}),
    ("Comentário SQL (--)", {"address": "Comendador José Garcia'; --", "number": "10", "city": "Pouso Alegre", "state": "MG"}),
    ("Drop Table Simulation", {"address": "Rua Principal'; DROP TABLE properties;--", "number": "1", "city": "Pouso Alegre", "state": "MG"}),
]

async def test_sql_injection():
    print("🛡️ Iniciando Bateria de Testes contra SQL Injection...\n" + "="*60)
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        for name, payload in SQL_INJECTION_PAYLOADS:
            try:
                # Testando na rota de preview de geolocalização / propriedades
                response = await client.get(f"{BASE_URL}/properties/geocode-preview", params=payload)
                status = response.status_code
                body_snippet = response.text[:150]
                
                print(f"🔹 Teste: {name}")
                print(f"   Payload enviado: {payload['address']}")
                print(f"   Status HTTP Retornado: {status}")
                
                if status in (400, 422):
                    print("   [SEGURO] O sistema rejeitou a entrada maliciosa na validação (Pydantic/API).")
                elif status == 500:
                    print("   [ALERTA/FALHA] O servidor retornou Erro 500. Pode indicar que a query quebrou ou vazou exceção do banco!")
                    print(f"   Resposta: {body_snippet}")
                else:
                    print(f"   [RESULTADO] Status {status}. O banco processou sem quebrar (provavelmente tratado pelo ORM).")
                print("-" * 60)
                
            except Exception as exc:
                print(f"   [ERRO DE CONEXÃO] Falha ao testar {name}: {exc}\n" + "-"*60)

if __name__ == "__main__":
    asyncio.run(test_sql_injection())