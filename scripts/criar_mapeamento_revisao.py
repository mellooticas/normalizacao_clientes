#!/usr/bin/env python3
"""
MAPEAMENTO VENDEDORES SUPABASE PARA REVISÃO
==========================================
Este arquivo extrai todos os vendedores principais do Supabase
organizados por loja para revisão manual
"""

import json
from datetime import datetime

def main():
    print("📋 CRIANDO MAPEAMENTO VENDEDORES SUPABASE")
    print("=" * 50)
    
    # Dados extraídos da consulta 6 do Supabase
    # Vendedores principais organizados por loja
    vendedores_por_loja = {
        "048_MAUA": {
            "nome_loja": "Mauá",
            "codigo": "048",
            "vendedores_principais": {
                "BETH": {
                    "nomes_encontrados": ["BETH", "MARIA ELIZABETH", "MARIA ELIZEBETH"],
                    "uuids": ["52e39d37-863c-4357-9509-24684e841a81", 
                             "82a9f82b-17e1-4584-99f3-6dd6c806ccc7", 
                             "bb644c43-baf1-40b0-beaf-101af26190f4"]
                },
                "LARISSA": {
                    "nomes_encontrados": ["LARISSA"],
                    "uuids": ["3a4d103f-ffe8-4e41-9315-4468f7c199a0"]
                },
                "ROGÉRIO": {
                    "nomes_encontrados": ["ROGÉRIO"],
                    "uuids": ["622b7b77-8c8b-4737-aa40-c1038663fb25"]
                },
                "TATY": {
                    "nomes_encontrados": ["TATY"],
                    "uuids": ["cfb63f0a-704d-4516-8914-e6f1e6c3ee4d"]
                },
                "WEVILLY": {
                    "nomes_encontrados": ["WEVILLY"],
                    "uuids": ["143dc77e-f690-43c4-a60f-f68bd4b106fb"]
                }
            }
        },
        
        "009_PERUS": {
            "nome_loja": "Perus",
            "codigo": "009",
            "vendedores_principais": {
                "ERIKA": {
                    "nomes_encontrados": ["ERIKA", "ÉRIKA"],
                    "uuids": ["c7b7f501-d028-4c09-b7d3-e6158799f972", 
                             "50355131-bdef-4a51-a74d-f74cde751fcc"]
                },
                "LARISSA": {
                    "nomes_encontrados": ["LARISSA"],
                    "uuids": ["d8e4dee6-b890-4d13-9e31-82c15e7b485f"]
                },
                "ROGÉRIO": {
                    "nomes_encontrados": ["ROGERIO", "ROGÉRIO"],
                    "uuids": ["31e51089-f7d4-4596-98f8-431096c6a098", 
                             "2664f78d-695e-4ade-b773-1349de311040"]
                },
                "TATY": {
                    "nomes_encontrados": ["TATY", "TATY/ERIKA"],
                    "uuids": ["56e4e9d9-6fa9-428b-a791-0a4995601c25", 
                             "341c825f-4429-4358-a93f-f081c497545c"]
                },
                "WEVILLY": {
                    "nomes_encontrados": ["WEVILLY"],
                    "uuids": ["73f2eee1-b8dd-4b82-bef0-032370a612bc"]
                }
            }
        },
        
        "011_RIO_PEQUENO": {
            "nome_loja": "Rio Pequeno",
            "codigo": "011",
            "vendedores_principais": {
                "LARISSA": {
                    "nomes_encontrados": ["LARISSA"],
                    "uuids": ["d9e18eee-c304-42ef-b5c4-7cbce900ed61"]
                },
                "ROGÉRIO": {
                    "nomes_encontrados": ["ROGERIO", "ROGÉRIO"],
                    "uuids": ["a372478f-4731-4462-a1db-2a877de7f4f4", 
                             "57d3affd-bc68-4eff-bcb4-a4ac252407ba"]
                },
                "TATY": {
                    "nomes_encontrados": ["TATY"],
                    "uuids": ["68a501bc-9d4f-4053-b431-94f7cb2d1438"]
                },
                "WEVILLY": {
                    "nomes_encontrados": ["WEVILLY"],
                    "uuids": ["ac0244dd-6356-4d19-88b0-2b01e3b9e0ac"]
                }
            }
        },
        
        "012_SAO_MATEUS": {
            "nome_loja": "São Mateus",
            "codigo": "012",
            "vendedores_principais": {
                "LARISSA": {
                    "nomes_encontrados": ["LARISSA"],
                    "uuids": ["fa5349d2-1f56-43a8-bb75-3d2c4e412688"]
                },
                "ROGÉRIO": {
                    "nomes_encontrados": ["ROGERIO", "ROGÉRIO"],
                    "uuids": ["9dfe3659-8c52-4d33-ab40-03d50f2c6464", 
                             "91c3475f-d68c-4840-9012-c9285fc1c745"]
                },
                "TATY": {
                    "nomes_encontrados": ["TATI", "TATY", "WEVILLY/TATY"],
                    "uuids": ["84ad4af0-543c-443e-8e9f-5d773a87d73e", 
                             "b2b47e57-6273-4c47-8d7e-bd5f0e407c40", 
                             "7d216690-1f60-4468-ba86-e3e7b219eb1e"]
                },
                "WEVILLY": {
                    "nomes_encontrados": ["WEVELLY", "WEVILLY"],
                    "uuids": ["ec66a9e7-b50f-4049-85d0-6b7cd04397b7", 
                             "a8bdcfb9-ace9-4e34-802a-6275c7629761"]
                }
            }
        },
        
        "042_SUZANO": {
            "nome_loja": "Suzano",
            "codigo": "042",
            "vendedores_principais": {
                "BETH": {
                    "nomes_encontrados": ["BETH"],
                    "uuids": ["70559d08-b0e6-4f35-8f92-363e287367e8"]
                },
                "FELIPE": {
                    "nomes_encontrados": ["FELIPE"],
                    "uuids": ["a95b631e-b28e-410a-90ee-95f69bb01391"]
                },
                "LARISSA": {
                    "nomes_encontrados": ["LARISSA"],
                    "uuids": ["39a1e217-ff8f-4cb1-9a0a-ef19f6228661"]
                },
                "ROGÉRIO": {
                    "nomes_encontrados": ["ROGERIO", "ROGÉRIO"],
                    "uuids": ["e6417905-e42b-459d-89c7-c9ce7bfd3a60", 
                             "e08d6338-c703-4138-8091-8c4c3e2d6306"]
                },
                "TATY": {
                    "nomes_encontrados": ["TATI", "TATY"],
                    "uuids": ["7c765fa7-cabe-4cd0-b5bf-a47b3cc5f1db", 
                             "56a56b51-4e26-41ea-b539-ef8e16b477de"]
                }
            }
        },
        
        "010_SUZANO2": {
            "nome_loja": "Suzano 2",
            "codigo": "010",
            "vendedores_principais": {
                "ERIKA": {
                    "nomes_encontrados": ["ERIKA", "ÉRIKA"],
                    "uuids": ["7765bfa5-5879-43ab-9ce8-e3c132f3bcd1", 
                             "945a932e-6eeb-4ac3-bcbf-83f69c71bb03"]
                },
                "FELIPE": {
                    "nomes_encontrados": ["FELIPE", "FELIPE MIRANDA", "FELIPE MIRANDFA"],
                    "uuids": ["12b38538-ef1d-4703-909c-f3c56e21605e", 
                             "6d0bf47a-d374-43de-9b1b-e849f0854fa4", 
                             "8d29b29a-3718-48b4-a003-9a196408afab"]
                },
                "ROGÉRIO": {
                    "nomes_encontrados": ["ROGÉRIO"],
                    "uuids": ["e407dc34-ecc5-46e1-a232-d337bc055f9a"]
                },
                "TATY": {
                    "nomes_encontrados": ["TATY"],
                    "uuids": ["b292be85-0d60-47aa-b36b-19a647496b04"]
                },
                "WEVILLY": {
                    "nomes_encontrados": ["WEVILLY"],
                    "uuids": ["0d6b6515-a548-47a6-b847-8a6aab21ecc4"]
                }
            }
        }
    }
    
    # Nossos vendedores normalizados por loja
    nossos_vendedores = {
        "048_MAUA": ["BETH", "FELIPE", "WEVILLY", "TATY", "LARISSA"],
        "009_PERUS": ["ERIKA", "LARISSA", "ROGÉRIO", "TATY", "WEVILLY"],
        "011_RIO_PEQUENO": ["LARISSA", "ROGÉRIO", "TATY", "WEVILLY"],
        "012_SAO_MATEUS": ["ARIANI DIAS FERNANDES CARDOSO", "LARISSA", "ROGÉRIO", "TATY", "WEVILLY"],
        "042_SUZANO": ["ARIANI DIAS FERNANDES CARDOSO", "BETH", "BRUNA", "ERIKA", "FELIPE", 
                      "JOCICREIDE BARBOSA", "ROGÉRIO", "ROSÂNGELA", "THIAGO VINICIUS"],
        "010_SUZANO2": ["BETH", "FELIPE", "TATY", "WEVILLY"]
    }
    
    # Criar arquivo de revisão
    arquivo_revisao = {
        "metadata": {
            "criado_em": datetime.now().isoformat(),
            "objetivo": "Revisão e correção do mapeamento de vendedores por loja",
            "instrucoes": [
                "Para cada loja, revise os vendedores listados",
                "Corrija os vendedores conforme a realidade",
                "Adicione ou remova vendedores conforme necessário",
                "Mantenha apenas os vendedores que realmente trabalham em cada loja"
            ]
        },
        "lojas": {}
    }
    
    # Processar cada loja
    for codigo_loja, dados_supabase in vendedores_por_loja.items():
        vendedores_supabase = list(dados_supabase["vendedores_principais"].keys())
        vendedores_nossos = nossos_vendedores.get(codigo_loja, [])
        
        arquivo_revisao["lojas"][codigo_loja] = {
            "nome_loja": dados_supabase["nome_loja"],
            "codigo": dados_supabase["codigo"],
            "vendedores_supabase": vendedores_supabase,
            "vendedores_nossos_dados": vendedores_nossos,
            "discrepancias": {
                "apenas_supabase": list(set(vendedores_supabase) - set(vendedores_nossos)),
                "apenas_nossos": list(set(vendedores_nossos) - set(vendedores_supabase))
            },
            "vendedores_corretos": vendedores_supabase,  # Inicializar com Supabase
            "observacoes": ""
        }
    
    # Salvar arquivo para revisão
    nome_arquivo = "REVISAO_VENDEDORES_POR_LOJA.json"
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        json.dump(arquivo_revisao, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Arquivo criado: {nome_arquivo}")
    print("\n📋 INSTRUÇÕES:")
    print("1. Abra o arquivo REVISAO_VENDEDORES_POR_LOJA.json")
    print("2. Para cada loja, revise o campo 'vendedores_corretos'")
    print("3. Adicione/remova vendedores conforme a realidade")
    print("4. Adicione observações no campo 'observacoes' se necessário")
    print("5. Salve o arquivo e me informe quando estiver pronto")
    
    print("\n🔍 RESUMO DAS DISCREPÂNCIAS ENCONTRADAS:")
    print("-" * 45)
    
    for codigo_loja, dados in arquivo_revisao["lojas"].items():
        print(f"\n🏪 {dados['nome_loja']} ({dados['codigo']})")
        print(f"   Supabase: {dados['vendedores_supabase']}")
        print(f"   Nossos:   {dados['vendedores_nossos_dados']}")
        
        if dados['discrepancias']['apenas_supabase']:
            print(f"   ⚠️ Faltando: {dados['discrepancias']['apenas_supabase']}")
        if dados['discrepancias']['apenas_nossos']:
            print(f"   ⚠️ Extras: {dados['discrepancias']['apenas_nossos']}")
        if not dados['discrepancias']['apenas_supabase'] and not dados['discrepancias']['apenas_nossos']:
            print("   ✅ Coincidentes")

if __name__ == "__main__":
    main()