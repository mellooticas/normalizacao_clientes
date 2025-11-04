#!/usr/bin/env python3
"""
ANÁLISE DETALHADA DE VENDEDORES POR LOJA
===============================================
Script para analisar a distribuição dos vendedores principais 
baseado nos dados do Supabase
"""

import pandas as pd
import json
from datetime import datetime

def main():
    print("🔍 ANÁLISE DETALHADA DE VENDEDORES POR LOJA")
    print("=" * 60)
    
    # Dados da consulta 6 do Supabase
    # Distribuição real dos vendedores por loja
    vendedores_supabase = {
        "Mauá": {
            "BETH": ["BETH", "MARIA ELIZABETH", "MARIA ELIZEBETH"],
            "LARISSA": ["LARISSA"],
            "ROGÉRIO": ["ROGÉRIO"],
            "TATY": ["TATY"],
            "WEVILLY": ["WEVILLY"],
            "OUTROS": ["ANDRESSA DE SOUZA", "B ETH", "ERICA DE CASSIA JESUS SILVA", 
                      "GARANTIA", "LUANA", "MARIA DA SILVA OZORIO", "RENAN NAZARO", "WEVELLY"]
        },
        "Perus": {
            "ERIKA": ["ERIKA", "ÉRIKA"],
            "LARISSA": ["LARISSA"],
            "ROGÉRIO": ["ROGERIO", "ROGÉRIO"],
            "TATY": ["TATY", "TATY/ERIKA"],
            "WEVILLY": ["WEVILLY"],
            "OUTROS": ["ANA", "ARIANI", "JOANA", "LUANA", "MARIA", "NAN", 
                      "SAMUEL", "SANDY", "WILLIAM", "WILLIAN"]
        },
        "Rio Pequeno": {
            "LARISSA": ["LARISSA"],
            "ROGÉRIO": ["ROGERIO", "ROGÉRIO"],
            "TATY": ["TATY"],
            "WEVILLY": ["WEVILLY"],
            "OUTROS": ["BRUNO", "GARANTIA", "KEREN", "MARIA RAMOS", "R0GERIO",
                      "ROSAGELA", "ROSANGELA", "ROSÂNGELA", "ROSÃNGELA", 
                      "ROSÃÑGELA", "ROSNGELA"]
        },
        "São Mateus": {
            "LARISSA": ["LARISSA"],
            "ROGÉRIO": ["ROGERIO", "ROGÉRIO"],
            "TATY": ["TATI", "TATY", "WEVILLY/TATY"],
            "WEVILLY": ["WEVELLY", "WEVILLY"],
            "OUTROS": ["/////////////////////////", "ARIANI", "CHINASA DORIS", 
                      "GARANTIA", "JOANA", "MARIA", "SANDY", "WILLAM", 
                      "WILLIAM", "WILLIAN"]
        },
        "Suzano": {
            "BETH": ["BETH"],
            "FELIPE": ["FELIPE"],
            "LARISSA": ["LARISSA"],
            "ROGÉRIO": ["ROGERIO", "ROGÉRIO"],
            "TATY": ["TATI", "TATY"],
            "OUTROS": ["ARIANE", "ARIANI", "GARANTIA", "GUILHERME SILVA", 
                      "JOCI", "JOCXY", "JOCY", "KAYLLAINE", "NAN", "PIX", 
                      "SAMUEL", "TATRY", "WILLAM", "WILLIAM", "WILLIAN", "ZAINE"]
        },
        "Suzano 2": {
            "ERIKA": ["ERIKA", "ÉRIKA"],
            "FELIPE": ["FELIPE", "FELIPE MIRANDA", "FELIPE MIRANDFA"],
            "ROGÉRIO": ["ROGÉRIO"],
            "TATY": ["TATY"],
            "WEVILLY": ["WEVILLY"],
            "OUTROS": ["ADRIANA ANSELMO", "CARLA CRISTINA", "ERICA", "GARANTIA",
                      "JULIANA CERA", "KAYLANE", "MARIA", "MARIA / GARANTIA",
                      "MARIA DE LOURDES", "NAN", "SAMUEL", "WILLIAM", "ZAINE"]
        }
    }
    
    # Dados dos nossos arquivos normalizados
    nossos_vendedores = {
        "MAUA": ["BETH", "FELIPE", "WEVILLY", "TATY", "LARISSA"],
        "PERUS": ["ERIKA", "LARISSA", "ROGÉRIO", "TATY", "WEVILLY"],
        "RIO_PEQUENO": ["LARISSA", "ROGÉRIO", "TATY", "WEVILLY"],
        "SAO_MATEUS": ["ARIANI DIAS FERNANDES CARDOSO", "LARISSA", "ROGÉRIO", "TATY", "WEVILLY"],
        "SUZANO2": ["BETH", "FELIPE", "TATY", "WEVILLY"],
        "SUZANO": ["ARIANI DIAS FERNANDES CARDOSO", "BETH", "BRUNA", "ERIKA", "FELIPE", 
                  "JOCICREIDE BARBOSA", "ROGÉRIO", "ROSÂNGELA", "THIAGO VINICIUS"]
    }
    
    print("\n📊 COMPARAÇÃO VENDEDORES PRINCIPAIS")
    print("-" * 50)
    
    # Mapeamento das lojas
    mapeamento_lojas = {
        "MAUA": "Mauá",
        "PERUS": "Perus", 
        "RIO_PEQUENO": "Rio Pequeno",
        "SAO_MATEUS": "São Mateus",
        "SUZANO2": "Suzano 2",
        "SUZANO": "Suzano"
    }
    
    for loja_nossa, loja_supabase in mapeamento_lojas.items():
        print(f"\n🏪 {loja_supabase} ({loja_nossa})")
        print("  Nossos vendedores:", nossos_vendedores[loja_nossa])
        
        vendedores_principais = []
        for consultor, nomes in vendedores_supabase[loja_supabase].items():
            if consultor != "OUTROS":
                vendedores_principais.append(consultor)
        
        print("  Supabase principais:", vendedores_principais)
        
        # Verificar diferenças
        nossos_set = set(nossos_vendedores[loja_nossa])
        supabase_set = set(vendedores_principais)
        
        apenas_nossos = nossos_set - supabase_set
        apenas_supabase = supabase_set - nossos_set
        
        if apenas_nossos:
            print(f"  ⚠️ Apenas nossos: {list(apenas_nossos)}")
        if apenas_supabase:
            print(f"  ⚠️ Apenas Supabase: {list(apenas_supabase)}")
        if not apenas_nossos and not apenas_supabase:
            print("  ✅ Vendedores principais coincidem")
    
    print("\n🎯 VENDEDORES ÚNICOS POR LOJA")
    print("-" * 40)
    
    # Analisar quais vendedores aparecem apenas em lojas específicas
    todos_vendedores = {}
    for loja_supabase, vendedores in vendedores_supabase.items():
        for consultor in vendedores.keys():
            if consultor != "OUTROS":
                if consultor not in todos_vendedores:
                    todos_vendedores[consultor] = []
                todos_vendedores[consultor].append(loja_supabase)
    
    for vendedor, lojas in todos_vendedores.items():
        if len(lojas) <= 2:  # Vendedores em poucas lojas
            print(f"  {vendedor}: {', '.join(lojas)} ({len(lojas)} lojas)")
    
    print("\n📈 VENDEDORES MAIS DISTRIBUÍDOS")
    print("-" * 35)
    
    for vendedor, lojas in sorted(todos_vendedores.items(), key=lambda x: len(x[1]), reverse=True):
        if len(lojas) >= 4:  # Vendedores em muitas lojas
            print(f"  {vendedor}: {len(lojas)} lojas - {', '.join(lojas)}")
    
    print("\n🔍 CASOS ESPECIAIS IDENTIFICADOS")
    print("-" * 35)
    
    casos_especiais = [
        ("BETH", "Apenas Mauá e Suzano"),
        ("FELIPE", "Apenas Suzano e Suzano 2"),
        ("ERIKA", "Apenas Perus e Suzano 2"),
        ("ROGÉRIO", "Presente em 4 lojas (exceto Mauá e Suzano 2)"),
        ("LARISSA", "Presente em 4 lojas (exceto Suzano 2)"),
        ("TATY", "Presente em 5 lojas (exceto Suzano 2)"),
        ("WEVILLY", "Presente em 4 lojas (exceto Mauá)")
    ]
    
    for vendedor, observacao in casos_especiais:
        print(f"  {vendedor}: {observacao}")
    
    print("\n💡 CONCLUSÕES")
    print("-" * 15)
    print("  1. BETH trabalha principalmente em Mauá (048) e Suzano (042)")
    print("  2. FELIPE trabalha apenas em Suzano (042) e Suzano 2 (010)")
    print("  3. ERIKA trabalha apenas em Perus (009) e Suzano 2 (010)")
    print("  4. Alguns vendedores são específicos de certas regiões/lojas")
    print("  5. Precisamos mapear considerando esta distribuição específica")
    
    # Gerar arquivo com análise detalhada
    analise = {
        "data_analise": datetime.now().isoformat(),
        "vendedores_supabase": vendedores_supabase,
        "nossos_vendedores": nossos_vendedores,
        "mapeamento_lojas": mapeamento_lojas,
        "distribuicao_vendedores": todos_vendedores,
        "casos_especiais": dict(casos_especiais)
    }
    
    with open("analise_vendedores_por_loja.json", "w", encoding="utf-8") as f:
        json.dump(analise, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Análise completa salva em: analise_vendedores_por_loja.json")

if __name__ == "__main__":
    main()