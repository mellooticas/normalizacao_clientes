#!/usr/bin/env python3
"""
Script para investigar problemas de conversão de datas
"""

import pandas as pd
import os

def investigar_problemas_conversao():
    """Investiga problemas na conversão de datas"""
    
    print("🔍 INVESTIGANDO PROBLEMAS DE CONVERSÃO DE DATAS")
    print("=" * 60)
    
    # Verificar arquivo com problemas
    arquivo_problema = 'data/originais/oss/finais_completos_com_todos_uuids/RIO_PEQUENO_final_todos_uuids.csv'
    
    if os.path.exists(arquivo_problema):
        print(f"\n📄 Investigando: {os.path.basename(arquivo_problema)}")
        
        df = pd.read_csv(arquivo_problema, nrows=10)
        
        # Verificar colunas de data
        colunas_data = [
            '            DATA DE COMPRA         ',
            'DT NASC',
            'PREV DE ENTR'
        ]
        
        for coluna in colunas_data:
            if coluna in df.columns:
                print(f"\n   📊 Coluna: '{coluna}'")
                valores_unicos = df[coluna].dropna().unique()[:10]
                
                for valor in valores_unicos:
                    print(f"      • '{valor}' (tipo: {type(valor).__name__})")
                    
                    # Tentar identificar o formato
                    valor_str = str(valor).strip()
                    if valor_str.replace('.', '').replace('-', '').isdigit():
                        print(f"        → Numérico: {valor_str}")
                    elif '/' in valor_str:
                        print(f"        → Com barra: {valor_str}")
                    elif '-' in valor_str:
                        print(f"        → Com hífen: {valor_str}")
                    else:
                        print(f"        → Formato desconhecido: {valor_str}")
    
    # Verificar arquivo que funcionou bem
    arquivo_sucesso = 'data/originais/oss/finais_completos_com_todos_uuids/PERUS_final_todos_uuids.csv'
    
    if os.path.exists(arquivo_sucesso):
        print(f"\n📄 Comparando com sucesso: {os.path.basename(arquivo_sucesso)}")
        
        df_sucesso = pd.read_csv(arquivo_sucesso, nrows=5)
        
        for coluna in colunas_data:
            if coluna in df_sucesso.columns:
                print(f"\n   📊 Coluna: '{coluna}'")
                valores_unicos = df_sucesso[coluna].dropna().unique()[:5]
                
                for valor in valores_unicos:
                    print(f"      • '{valor}' (tipo: {type(valor).__name__})")

if __name__ == "__main__":
    investigar_problemas_conversao()