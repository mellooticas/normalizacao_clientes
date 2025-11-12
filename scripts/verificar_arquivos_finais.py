#!/usr/bin/env python3
"""
Verificar arquivos finais prontos para o banco
"""

import pandas as pd
import os

def verificar_arquivos_finais():
    """Verifica os arquivos finais gerados"""
    
    print("🎯 VERIFICAÇÃO DOS ARQUIVOS FINAIS PARA O BANCO")
    print("=" * 60)
    
    # Arquivo consolidado
    arquivo_consolidado = "data/finais_banco/OS_ENTREGUES_DIA_TODAS_LOJAS_FINAL_BANCO.csv"
    
    if os.path.exists(arquivo_consolidado):
        df = pd.read_csv(arquivo_consolidado)
        
        print(f"📊 ESTATÍSTICAS CONSOLIDADAS:")
        print(f"   • Total de registros: {len(df):,}")
        print(f"   • Colunas: {len(df.columns)}")
        print(f"   • Lojas: {df['loja_nome'].nunique()}")
        print(f"   • Vendedores únicos: {df['vendedor_nome_normalizado'].nunique()}")
        print(f"   • UUID Coverage: {(df['vendedor_uuid'].notna().sum() / len(df) * 100):.1f}%")
        
        print(f"\n🏪 REGISTROS POR LOJA:")
        for loja, count in df['loja_nome'].value_counts().items():
            print(f"   • {loja}: {count:,} registros")
        
        print(f"\n📋 COLUNAS ESSENCIAIS:")
        colunas_essenciais = ['os_numero', 'vendedor', 'vendedor_uuid', 'vendedor_nome_normalizado', 
                            'data_movimento', 'loja_nome', 'loja_id', 'canal_captacao_uuid']
        
        for coluna in colunas_essenciais:
            if coluna in df.columns:
                validos = df[coluna].notna().sum()
                percentual = (validos / len(df) * 100)
                print(f"   • {coluna}: {validos:,} válidos ({percentual:.1f}%)")
        
        # Verificar arquivos individuais
        print(f"\n📁 ARQUIVOS INDIVIDUAIS:")
        finais_dir = "data/finais_banco"
        
        for arquivo in os.listdir(finais_dir):
            if arquivo.endswith('_FINAL_BANCO.csv') and 'TODAS_LOJAS' not in arquivo:
                caminho = os.path.join(finais_dir, arquivo)
                df_loja = pd.read_csv(caminho)
                loja = arquivo.replace('os_entregues_dia_', '').replace('_FINAL_BANCO.csv', '')
                print(f"   📄 {loja}: {len(df_loja):,} registros")
        
        print(f"\n✅ ARQUIVOS PRONTOS PARA UPLOAD NO SUPABASE!")
        print(f"📁 Localização: data/finais_banco/")
        print(f"🎯 Use o arquivo consolidado ou arquivos individuais por loja")
        
    else:
        print("❌ Arquivo consolidado não encontrado!")

if __name__ == "__main__":
    verificar_arquivos_finais()