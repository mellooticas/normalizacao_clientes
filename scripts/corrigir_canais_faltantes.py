#!/usr/bin/env python3
"""
Script para corrigir canais de captação faltantes
"""

import pandas as pd
import json
import os

def corrigir_canais_faltantes():
    """Analisa e corrige canais de captação faltantes"""
    
    print("🔍 ANALISANDO CANAIS FALTANTES")
    print("=" * 50)
    
    # Carregar mapeamento atual
    with open('mapeamento_canais_captacao_uuid.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    canais_uuid = data['canais_captacao_uuid']
    
    # Diretório dos arquivos finais
    dir_arquivos = 'data/originais/oss/finais_com_uuids'
    arquivos = [f for f in os.listdir(dir_arquivos) if f.endswith('_final_completo.csv')]
    
    canais_faltantes = set()
    
    for arquivo in sorted(arquivos):
        print(f"\n📄 Analisando: {arquivo}")
        
        caminho = os.path.join(dir_arquivos, arquivo)
        df = pd.read_csv(caminho)
        
        # Verificar valores únicos da coluna 'COMO CONHECEU '
        valores_unicos = df['COMO CONHECEU '].dropna().unique()
        
        for valor in valores_unicos:
            valor_str = str(valor).strip()
            if valor_str and valor_str not in canais_uuid:
                canais_faltantes.add(valor_str)
                print(f"   ❌ Faltante: '{valor_str}'")
    
    if canais_faltantes:
        print(f"\n🎯 ENCONTRADOS {len(canais_faltantes)} CANAIS FALTANTES:")
        for canal in sorted(canais_faltantes):
            print(f"   • '{canal}'")
        
        # Gerar UUIDs para os faltantes
        import uuid
        
        for canal in sorted(canais_faltantes):
            canais_uuid[canal] = str(uuid.uuid4())
        
        # Atualizar arquivo de mapeamento
        data['canais_captacao_uuid'] = canais_uuid
        data['total_canais'] = len(canais_uuid)
        
        with open('mapeamento_canais_captacao_uuid_completo.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ MAPEAMENTO ATUALIZADO!")
        print(f"   • Total de canais: {len(canais_uuid)}")
        print(f"   • Arquivo: mapeamento_canais_captacao_uuid_completo.json")
        
    else:
        print(f"\n✅ NENHUM CANAL FALTANTE ENCONTRADO!")
        print(f"   • Todos os {len(canais_uuid)} canais estão mapeados")
    
    # Análise detalhada dos valores problemáticos
    print(f"\n🔍 ANÁLISE DETALHADA DE VALORES PROBLEMÁTICOS:")
    
    for arquivo in sorted(arquivos):
        caminho = os.path.join(dir_arquivos, arquivo)
        df = pd.read_csv(caminho)
        
        # Valores nulos
        nulos = df['COMO CONHECEU '].isna().sum()
        if nulos > 0:
            print(f"\n   {arquivo}: {nulos} registros com valor nulo")
        
        # Valores em branco ou espaços
        df_clean = df.dropna(subset=['COMO CONHECEU '])
        brancos = (df_clean['COMO CONHECEU '].str.strip() == '').sum()
        if brancos > 0:
            print(f"   {arquivo}: {brancos} registros com valor em branco")
        
        # Valores únicos problemáticos
        valores_problematicos = df_clean[df_clean['COMO CONHECEU '].str.strip() == '']['COMO CONHECEU '].unique()
        for valor in valores_problematicos:
            print(f"   {arquivo}: Valor problemático: '{repr(valor)}'")

if __name__ == "__main__":
    corrigir_canais_faltantes()