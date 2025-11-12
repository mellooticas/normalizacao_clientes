#!/usr/bin/env python3
"""
Resumo Final - Todas as Estruturas Organizadas
==============================================

Compara estruturas CXS, OSS e VIXEN organizadas uniformemente.
"""

from pathlib import Path
import pandas as pd

def analisar_estrutura(pasta_base, nome):
    print(f"\n📂 {nome.upper()}")
    print("=" * 40)
    
    total_registros = 0
    total_arquivos_finais = 0
    
    for item in sorted(pasta_base.iterdir()):
        if item.is_dir():
            if item.name == "planilhas_originais":
                count_xlsx = len(list(item.glob("*.xlsx")))
                count_xls = len(list(item.glob("*.xls")))
                total_planilhas = count_xlsx + count_xls
                print(f"   📊 {item.name}/ ({total_planilhas} planilhas)")
                
                # Mostrar subpastas se existirem
                for subitem in sorted(item.iterdir()):
                    if subitem.is_dir():
                        sub_count = len(list(subitem.glob("*.xlsx")))
                        if sub_count > 0:
                            print(f"      🔹 {subitem.name}: {sub_count} planilhas")
            
            elif item.name == "extraidos_corrigidos":
                if nome == "CXS":
                    print(f"   📊 {item.name}/ (dados processados)")
                    for subitem in sorted(item.iterdir()):
                        if subitem.is_dir() and not subitem.name.startswith('_'):
                            count = len(list(subitem.glob("*.csv")))
                            if count > 0:
                                print(f"      🔹 {subitem.name}: {count} arquivos")
                else:
                    count = len(list(item.glob("*.csv")))
                    print(f"   📊 {item.name}/ ({count} arquivos)")
            
            elif item.name == "finais_postgresql_prontos":
                arquivos_finais = list(item.glob("*.csv"))
                total_arquivos_finais = len(arquivos_finais)
                
                registros_estrutura = 0
                print(f"   📊 {item.name}/ ({total_arquivos_finais} arquivos finais)")
                
                for arquivo in sorted(arquivos_finais):
                    try:
                        df = pd.read_csv(arquivo)
                        registros = len(df)
                        registros_estrutura += registros
                        
                        # Extrair loja do nome do arquivo
                        nome_arquivo = arquivo.stem
                        if "_" in nome_arquivo:
                            partes = nome_arquivo.split("_")
                            if len(partes) >= 2:
                                loja = partes[-2] if partes[-1] == "final" else partes[-1]
                                print(f"      ✅ {loja.upper()}: {registros:,} registros")
                    except Exception as e:
                        print(f"      ❌ {arquivo.name}: Erro - {e}")
                
                total_registros += registros_estrutura
                print(f"   📈 Subtotal: {registros_estrutura:,} registros")
    
    return total_registros, total_arquivos_finais

def main():
    base_dir = Path("d:/projetos/carne_facil/carne_facil/data/originais")
    
    print("🎯 RESUMO FINAL - TODAS AS ESTRUTURAS")
    print("=" * 60)
    
    estruturas = ["cxs", "oss", "vixen"]
    resumo_geral = {}
    
    for estrutura in estruturas:
        estrutura_dir = base_dir / estrutura
        
        if estrutura_dir.exists():
            total_regs, total_arqs = analisar_estrutura(estrutura_dir, estrutura)
            resumo_geral[estrutura.upper()] = {
                'registros': total_regs,
                'arquivos': total_arqs
            }
        else:
            print(f"\n❌ {estrutura.upper()}: Estrutura não encontrada")
    
    print(f"\n" + "="*60)
    print(f"📊 RESUMO CONSOLIDADO")
    print(f"="*60)
    
    total_geral_registros = 0
    total_geral_arquivos = 0
    
    for estrutura, dados in resumo_geral.items():
        print(f"   🔹 {estrutura:6}: {dados['registros']:8,} registros em {dados['arquivos']:2} arquivos")
        total_geral_registros += dados['registros']
        total_geral_arquivos += dados['arquivos']
    
    print(f"   " + "-"*50)
    print(f"   🎯 TOTAL:   {total_geral_registros:8,} registros em {total_geral_arquivos:2} arquivos")
    
    print(f"\n🚀 INTEGRAÇÃO DE DADOS")
    print(f"   📊 CXS: 5 tabelas de transações financeiras")
    print(f"   📊 OSS: 1 tabela de ordens de serviço normalizadas")
    print(f"   📊 VIXEN: 1 tabela de clientes completos")
    
    print(f"\n🔗 POSSIBILIDADES DE CRUZAMENTO")
    print(f"   🔹 OSS ↔ CXS: Via os_numero (chave única)")
    print(f"   🔹 VIXEN ↔ OSS: Via vendedor ou cliente")
    print(f"   🔹 VIXEN ↔ CXS: Via cliente ou vendedor")
    
    print(f"\n✅ TODAS AS ESTRUTURAS ORGANIZADAS E PRONTAS!")

if __name__ == "__main__":
    main()