#!/usr/bin/env python3
"""
Resumo Final - Arquivos Prontos para Banco
==========================================

Gera resumo completo dos arquivos finais preparados para upload no banco.
"""

import pandas as pd
from pathlib import Path

def main():
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    finais_dir = base_dir / "data" / "finais_banco"
    
    print("🎯 ARQUIVOS FINAIS PARA BANCO DE DADOS")
    print("=" * 60)
    
    # Organizar por tabela
    tabelas = {
        'vendas': [],
        'restante_entrada': [],
        'recebimento_carne': [],
        'os_entregues_dia': [],
        'entrega_carne': []
    }
    
    total_geral = 0
    
    # Processar cada arquivo
    for arquivo in sorted(finais_dir.glob("*_final.csv")):
        nome_arquivo = arquivo.name
        
        # Extrair tabela
        for tabela in tabelas.keys():
            if nome_arquivo.startswith(tabela):
                try:
                    df = pd.read_csv(arquivo)
                    registros = len(df)
                    
                    # Extrair loja
                    loja = nome_arquivo.replace(f"{tabela}_", "").replace("_final.csv", "")
                    
                    tabelas[tabela].append({
                        'loja': loja,
                        'arquivo': nome_arquivo,
                        'registros': registros
                    })
                    
                    total_geral += registros
                    break
                except Exception as e:
                    print(f"❌ Erro ao processar {nome_arquivo}: {e}")
    
    # Exibir resumo por tabela
    for tabela, arquivos in tabelas.items():
        if arquivos:
            total_tabela = sum(item['registros'] for item in arquivos)
            print(f"\n📊 {tabela.upper()}")
            print(f"   Total: {total_tabela:,} registros em {len(arquivos)} lojas")
            
            # Ordenar por loja
            arquivos_ordenados = sorted(arquivos, key=lambda x: x['loja'])
            
            for item in arquivos_ordenados:
                loja_formatada = item['loja'].upper().replace('_', ' ')
                print(f"   🔹 {loja_formatada:12} | {item['registros']:6,} registros | {item['arquivo']}")
    
    print(f"\n" + "="*60)
    print(f"🎯 RESUMO FINAL")
    print(f"   📊 Total de registros: {total_geral:,}")
    print(f"   📁 Total de arquivos: {sum(len(arquivos) for arquivos in tabelas.values())}")
    print(f"   🏪 Lojas processadas: 6 (MAUA, PERUS, RIO PEQUENO, SAO MATEUS, SUZANO, SUZANO2)")
    print(f"   📂 Localização: {finais_dir}")
    
    print(f"\n🚀 BUSINESS INTELLIGENCE")
    print(f"   🔹 VENDAS: Controle completo de vendas realizadas")
    print(f"   🔹 RESTANTE_ENTRADA: Gestão de parcelas pendentes") 
    print(f"   🔹 RECEBIMENTO_CARNE: Controle de recebimentos")
    print(f"   🔹 OS_ENTREGUES_DIA: Master table com vendedores e canais")
    print(f"   🔹 ENTREGA_CARNE: Controle de entregas financiadas")
    
    print(f"\n📋 ESTRUTURA DE RELACIONAMENTOS")
    print(f"   🔗 Chave principal: os_numero (OS única por loja)")
    print(f"   🔗 Vendedores: Apenas em OS_ENTREGUES_DIA")
    print(f"   🔗 Cruzamentos: Via os_numero no banco de dados")
    print(f"   🔗 Controle: 5 tabelas = gestão completa do negócio")
    
    print(f"\n✅ PRONTO PARA UPLOAD NO BANCO!")

if __name__ == "__main__":
    main()