#!/usr/bin/env python3
"""
Script para analisar e mapear os canais de captação (COMO CONHECEU)
"""

import pandas as pd
import uuid
import json
from pathlib import Path
from collections import Counter

def analisar_canais_captacao():
    """Analisa todos os valores únicos do campo COMO CONHECEU"""
    
    finais_dir = Path("data/originais/oss/finais_com_uuids")
    
    print("🔍 ANÁLISE DOS CANAIS DE CAPTAÇÃO (COMO CONHECEU)")
    print("=" * 60)
    
    todos_canais = []
    estatisticas_por_loja = {}
    
    # Processar cada arquivo
    for csv_file in finais_dir.glob("*_final_completo.csv"):
        loja_nome = csv_file.stem.replace("_final_completo", "")
        
        print(f"\n📊 Analisando {loja_nome}...")
        
        try:
            # Ler CSV
            df = pd.read_csv(csv_file, encoding='utf-8')
            
            # Extrair valores únicos do campo "COMO CONHECEU"
            canais_loja = df['COMO CONHECEU '].dropna().unique()
            
            # Contar frequências
            contadores = df['COMO CONHECEU '].value_counts()
            
            estatisticas_por_loja[loja_nome] = {
                'total_registros': len(df),
                'canais_unicos': len(canais_loja),
                'top_canais': contadores.head(10).to_dict()
            }
            
            print(f"   • Total de registros: {len(df):,}")
            print(f"   • Canais únicos: {len(canais_loja)}")
            print(f"   • Top 5 canais:")
            for canal, qtd in contadores.head(5).items():
                print(f"     - '{canal}': {qtd} registros")
            
            # Adicionar à lista geral
            todos_canais.extend(canais_loja)
            
        except Exception as e:
            print(f"   • ❌ Erro: {e}")
    
    # Análise consolidada
    print("\n" + "=" * 60)
    print("📈 ANÁLISE CONSOLIDADA:")
    
    canais_unicos = list(set(todos_canais))
    contador_geral = Counter(todos_canais)
    
    print(f"   • Total de canais únicos: {len(canais_unicos)}")
    print(f"   • Top 10 canais mais frequentes:")
    
    for i, (canal, qtd) in enumerate(contador_geral.most_common(10), 1):
        print(f"     {i:2d}. '{canal}': {qtd:,} registros")
    
    # Salvar análise completa
    analise_completa = {
        'canais_unicos': sorted(canais_unicos),
        'contador_geral': dict(contador_geral.most_common()),
        'estatisticas_por_loja': estatisticas_por_loja,
        'total_canais_unicos': len(canais_unicos)
    }
    
    with open('analise_canais_captacao.json', 'w', encoding='utf-8') as f:
        json.dump(analise_completa, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Análise salva em: analise_canais_captacao.json")
    
    return canais_unicos

def gerar_mapeamento_canais_uuid():
    """Gera mapeamento de canais para UUIDs"""
    
    print("\n🔗 GERANDO MAPEAMENTO DE UUIDs PARA CANAIS...")
    print("=" * 50)
    
    # Analisar canais
    canais_unicos = analisar_canais_captacao()
    
    # Gerar UUIDs para cada canal
    mapeamento_canais = {}
    
    for canal in sorted(canais_unicos):
        if pd.notna(canal) and str(canal).strip():  # Evitar valores vazios
            canal_limpo = str(canal).strip()
            mapeamento_canais[canal_limpo] = str(uuid.uuid4())
    
    # Salvar mapeamento
    mapeamento_final = {
        'canais_captacao_uuid': mapeamento_canais,
        'total_canais': len(mapeamento_canais),
        'data_geracao': '2025-10-29'
    }
    
    with open('mapeamento_canais_captacao_uuid.json', 'w', encoding='utf-8') as f:
        json.dump(mapeamento_final, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Mapeamento gerado para {len(mapeamento_canais)} canais únicos")
    print(f"💾 Salvo em: mapeamento_canais_captacao_uuid.json")
    
    # Exibir alguns exemplos
    print(f"\n📋 EXEMPLOS DE MAPEAMENTO:")
    for i, (canal, uuid_canal) in enumerate(list(mapeamento_canais.items())[:10], 1):
        print(f"   {i:2d}. '{canal}' -> {uuid_canal}")
    
    if len(mapeamento_canais) > 10:
        print(f"   ... e mais {len(mapeamento_canais) - 10} canais")
    
    return mapeamento_canais

if __name__ == "__main__":
    mapeamento_canais = gerar_mapeamento_canais_uuid()