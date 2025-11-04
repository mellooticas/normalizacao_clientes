#!/usr/bin/env python3
"""
Análise completa de vendedores das OSs e Vixen
Para identificar todos os nomes únicos e suas variações
"""

import pandas as pd
import json
from pathlib import Path
from collections import defaultdict, Counter

def analisar_vendedores_completo():
    """
    Analisa todos os vendedores das OSs e Vixen para identificar padrões
    """
    print("🔍 ANÁLISE COMPLETA DE VENDEDORES")
    print("="*60)
    
    # Estruturas para coleta de dados
    vendedores_por_fonte = {}
    vendedores_unicos = set()
    vendedores_por_loja = defaultdict(set)
    contador_vendedores = Counter()
    
    # === 1. ANALISAR OSs NORMALIZADAS ===
    print("\n📊 Analisando OSs normalizadas...")
    dir_oss = Path("data/originais/oss/normalizadas")
    
    vendedores_oss = set()
    if dir_oss.exists():
        for arquivo in dir_oss.glob("*.csv"):
            try:
                df = pd.read_csv(arquivo)
                # A coluna é "             CONSULTOR  " (com espaços)
                coluna_consultor = None
                for col in df.columns:
                    if 'CONSULTOR' in col.upper():
                        coluna_consultor = col
                        break
                
                if coluna_consultor:
                    vendedores_arquivo = df[coluna_consultor].dropna().unique()
                    for vendedor in vendedores_arquivo:
                        vendedor_clean = str(vendedor).strip()
                        if vendedor_clean and vendedor_clean != 'nan':
                            vendedores_oss.add(vendedor_clean)
                            vendedores_unicos.add(vendedor_clean)
                            contador_vendedores[vendedor_clean] += len(df[df[coluna_consultor] == vendedor])
                            
                            # Extrair loja do nome do arquivo
                            loja = arquivo.stem.replace('_normalizado', '').replace('_uuid', '')
                            vendedores_por_loja[loja].add(vendedor_clean)
                    
                    print(f"  {arquivo.name}: {len(vendedores_arquivo)} vendedores únicos")
                else:
                    print(f"  ❌ {arquivo.name}: Coluna CONSULTOR não encontrada")
                    
            except Exception as e:
                print(f"  ❌ Erro em {arquivo.name}: {e}")
    
    vendedores_por_fonte['OSs'] = sorted(vendedores_oss)
    print(f"Total OSs: {len(vendedores_oss)} vendedores únicos")
    
    # === 2. ANALISAR VIXEN ===
    print(f"\n📊 Analisando dados Vixen...")
    arquivo_vixen = Path("data_backup/marketing_origens_vixen_correto.csv")
    
    vendedores_vixen = set()
    if arquivo_vixen.exists():
        try:
            df_vixen = pd.read_csv(arquivo_vixen)
            if 'consultor' in df_vixen.columns:
                vendedores_vixen_raw = df_vixen['consultor'].dropna().unique()
                for vendedor in vendedores_vixen_raw:
                    vendedor_clean = str(vendedor).strip()
                    if vendedor_clean and vendedor_clean != 'nan':
                        vendedores_vixen.add(vendedor_clean)
                        vendedores_unicos.add(vendedor_clean)
                        contador_vendedores[vendedor_clean] += len(df_vixen[df_vixen['consultor'] == vendedor])
                        
                        # Vixen tem lojas numeradas
                        for loja_num in df_vixen[df_vixen['consultor'] == vendedor]['loja'].unique():
                            vendedores_por_loja[f"LOJA_{loja_num}"].add(vendedor_clean)
                
                print(f"  Vixen: {len(vendedores_vixen)} vendedores únicos")
            else:
                print(f"  ❌ Vixen: Coluna 'consultor' não encontrada")
                
        except Exception as e:
            print(f"  ❌ Erro no Vixen: {e}")
    else:
        print(f"  ❌ Arquivo Vixen não encontrado: {arquivo_vixen}")
    
    vendedores_por_fonte['Vixen'] = sorted(vendedores_vixen)
    
    # === 3. ANÁLISE COMPARATIVA ===
    print(f"\n📈 ANÁLISE COMPARATIVA")
    print(f"="*40)
    print(f"Total vendedores únicos (OSs): {len(vendedores_oss)}")
    print(f"Total vendedores únicos (Vixen): {len(vendedores_vixen)}")
    print(f"Total vendedores únicos (Geral): {len(vendedores_unicos)}")
    
    # Vendedores em comum
    comuns = vendedores_oss.intersection(vendedores_vixen)
    apenas_oss = vendedores_oss - vendedores_vixen
    apenas_vixen = vendedores_vixen - vendedores_oss
    
    print(f"\nVendedores em comum: {len(comuns)}")
    if comuns:
        for v in sorted(comuns):
            print(f"  ✅ {v}")
    
    print(f"\nApenas nas OSs: {len(apenas_oss)}")
    if apenas_oss:
        for v in sorted(apenas_oss):
            print(f"  📋 {v}")
    
    print(f"\nApenas no Vixen: {len(apenas_vixen)}")
    if apenas_vixen:
        for v in sorted(apenas_vixen):
            print(f"  🔷 {v}")
    
    # === 4. RANKING POR QUANTIDADE DE VENDAS ===
    print(f"\n🏆 RANKING DE VENDEDORES (por quantidade de vendas)")
    print(f"="*50)
    for vendedor, qtd in contador_vendedores.most_common(20):
        print(f"  {vendedor}: {qtd} vendas")
    
    # === 5. VENDEDORES POR LOJA ===
    print(f"\n🏪 VENDEDORES POR LOJA")
    print(f"="*30)
    for loja, vendedores_loja in sorted(vendedores_por_loja.items()):
        print(f"\n{loja}: {len(vendedores_loja)} vendedores")
        for v in sorted(vendedores_loja):
            qtd = contador_vendedores.get(v, 0)
            print(f"  - {v} ({qtd} vendas)")
    
    # === 6. IDENTIFICAR POSSÍVEIS DUPLICATAS ===
    print(f"\n🔍 ANÁLISE DE POSSÍVEIS DUPLICATAS")
    print(f"="*35)
    
    # Agrupar por similaridade de nome
    grupos_similares = defaultdict(list)
    vendedores_lista = list(vendedores_unicos)
    
    for vendedor in vendedores_lista:
        nome_base = vendedor.upper().split()[0]  # Primeiro nome
        grupos_similares[nome_base].append(vendedor)
    
    # Mostrar grupos com múltiplos nomes
    for nome_base, grupo in grupos_similares.items():
        if len(grupo) > 1:
            print(f"\n📋 Grupo '{nome_base}':")
            for v in sorted(grupo):
                qtd = contador_vendedores.get(v, 0)
                fontes = []
                if v in vendedores_oss:
                    fontes.append("OSs")
                if v in vendedores_vixen:
                    fontes.append("Vixen")
                print(f"  - {v} ({qtd} vendas) [{', '.join(fontes)}]")
    
    # === 7. SALVAR RELATÓRIO ===
    relatorio = {
        'total_vendedores_unicos': len(vendedores_unicos),
        'vendedores_por_fonte': vendedores_por_fonte,
        'vendedores_comuns': sorted(comuns),
        'apenas_oss': sorted(apenas_oss),
        'apenas_vixen': sorted(apenas_vixen),
        'ranking_vendas': dict(contador_vendedores.most_common()),
        'vendedores_por_loja': {k: sorted(v) for k, v in vendedores_por_loja.items()},
        'grupos_similares': {k: v for k, v in grupos_similares.items() if len(v) > 1}
    }
    
    # Salvar em JSON
    with open('analise_vendedores_completa.json', 'w', encoding='utf-8') as f:
        json.dump(relatorio, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Relatório salvo em: analise_vendedores_completa.json")
    
    return relatorio

if __name__ == "__main__":
    relatorio = analisar_vendedores_completo()
    
    print(f"\n" + "="*60)
    print("✅ ANÁLISE CONCLUÍDA!")
    print("Agora podemos trabalhar vendedor por vendedor para normalizar.")
    print("="*60)