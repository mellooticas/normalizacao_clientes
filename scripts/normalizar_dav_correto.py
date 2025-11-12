#!/usr/bin/env python3
"""
Script para normalizar CORRETAMENTE os números DAV
Removendo prefixos específicos 42xxxx e 48xxxx
"""

import pandas as pd
import numpy as np
from datetime import datetime
import re
import warnings
warnings.filterwarnings('ignore')

def normalizar_dav_correto():
    """
    Normaliza os números DAV removendo prefixos conhecidos
    """
    print("🔧 === NORMALIZAÇÃO CORRETA DOS NÚMEROS DAV === 🔧")
    
    # Carregar arquivo
    arquivo = 'data/originais/controles_gerais/lista_dav/csv/arquivo_final.csv'
    df = pd.read_csv(arquivo)
    print(f"✅ Arquivo carregado: {len(df):,} registros")
    
    # Backup da coluna original
    df['Nro.DAV_original'] = df['Nro.DAV'].copy()
    
    # Analisar padrões atuais
    print(f"\n🔍 === ANÁLISE DE PADRÕES === 🔍")
    
    dav_validos = df['Nro.DAV'].dropna()
    print(f"📊 Valores válidos: {len(dav_validos):,}")
    
    # Análise estatística dos números
    numeros_convertidos = pd.to_numeric(dav_validos, errors='coerce').dropna()
    print(f"🔢 Conversíveis para número: {len(numeros_convertidos):,}")
    
    if len(numeros_convertidos) > 0:
        print(f"📊 Range atual: {int(numeros_convertidos.min()):,} → {int(numeros_convertidos.max()):,}")
        print(f"📊 Média: {int(numeros_convertidos.mean()):,}")
    
    # Identificar padrões de prefixos
    print(f"\n🏷️ === IDENTIFICANDO PREFIXOS === 🏷️")
    
    prefixo_42 = 0
    prefixo_48 = 0
    numeros_normais = 0
    outros = 0
    
    for valor in dav_validos:
        valor_str = str(int(float(valor))) if pd.notna(valor) else str(valor)
        
        if valor_str.startswith('42') and len(valor_str) >= 6:
            prefixo_42 += 1
        elif valor_str.startswith('48') and len(valor_str) >= 6:
            prefixo_48 += 1
        elif len(valor_str) <= 5:  # Números "normais" até 99999
            numeros_normais += 1
        else:
            outros += 1
    
    print(f"🏪 Prefixo 42 (Suzano): {prefixo_42:,}")
    print(f"🏪 Prefixo 48 (Mauá): {prefixo_48:,}")
    print(f"🔢 Números normais (≤5 dígitos): {numeros_normais:,}")
    print(f"❓ Outros padrões: {outros:,}")
    
    # Função de normalização melhorada
    def normalizar_numero_dav(valor):
        if pd.isna(valor):
            return None
        
        # Converter para string limpa
        valor_str = str(int(float(valor)))
        
        # Suzano: 42xxxxx → xxxxx
        if valor_str.startswith('42') and len(valor_str) >= 6:
            numero_limpo = valor_str[2:]  # Remove '42'
            # Se sobrou um número muito pequeno, pode ser que precise manter mais dígitos
            if len(numero_limpo) >= 3:
                return int(numero_limpo)
        
        # Mauá: 48xxxxx → xxxxx  
        elif valor_str.startswith('48') and len(valor_str) >= 6:
            numero_limpo = valor_str[2:]  # Remove '48'
            if len(numero_limpo) >= 3:
                return int(numero_limpo)
        
        # Números já normais (≤5 dígitos)
        elif len(valor_str) <= 5:
            return int(valor_str)
        
        # Outros casos - tentar identificar padrão
        else:
            # Se tem mais de 6 dígitos, pode ser um prefixo não identificado
            if len(valor_str) > 6:
                # Tentar extrair últimos 4-5 dígitos
                if len(valor_str) >= 8:
                    return int(valor_str[-5:])  # Últimos 5 dígitos
                else:
                    return int(valor_str[-4:])  # Últimos 4 dígitos
            else:
                return int(valor_str)
    
    # Aplicar normalização
    print(f"\n🔄 === APLICANDO NORMALIZAÇÃO === 🔄")
    
    df['OS_numero'] = df['Nro.DAV'].apply(normalizar_numero_dav)
    
    # Análise dos resultados
    print(f"\n📊 === RESULTADOS === 📊")
    
    os_validos = df['OS_numero'].notna().sum()
    os_unicos = df['OS_numero'].nunique()
    
    print(f"✅ OS normalizados: {os_validos:,}")
    print(f"✅ OS únicos: {os_unicos:,}")
    
    # Novo range
    os_clean = df['OS_numero'].dropna()
    if len(os_clean) > 0:
        print(f"📊 Novo range: {int(os_clean.min()):,} → {int(os_clean.max()):,}")
        print(f"📊 Nova média: {int(os_clean.mean()):,}")
    
    # Exemplos de normalização
    print(f"\n📋 === EXEMPLOS DE NORMALIZAÇÃO === 📋")
    
    # Mostrar transformações por tipo
    exemplos_42 = df[df['Nro.DAV_original'].astype(str).str.startswith('42', na=False)].head(5)
    exemplos_48 = df[df['Nro.DAV_original'].astype(str).str.startswith('48', na=False)].head(5)
    exemplos_normais = df[df['Nro.DAV_original'].astype(str).str.len() <= 5].head(5)
    
    if len(exemplos_42) > 0:
        print(f"🏪 Suzano (42xxxxx):")
        for _, row in exemplos_42.iterrows():
            print(f"   {row['Nro.DAV_original']} → {row['OS_numero']}")
    
    if len(exemplos_48) > 0:
        print(f"🏪 Mauá (48xxxxx):")
        for _, row in exemplos_48.iterrows():
            print(f"   {row['Nro.DAV_original']} → {row['OS_numero']}")
    
    if len(exemplos_normais) > 0:
        print(f"🔢 Números normais:")
        for _, row in exemplos_normais.head(3).iterrows():
            print(f"   {row['Nro.DAV_original']} → {row['OS_numero']}")
    
    return df

def salvar_arquivo_normalizado_correto(df):
    """
    Salva arquivo com normalização correta
    """
    print(f"\n💾 === SALVANDO ARQUIVO NORMALIZADO === 💾")
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Substituir a coluna Nro.DAV pela normalizada
    df['Nro.DAV'] = df['OS_numero']
    
    # Arquivo com backup
    arquivo_backup = f'data/originais/controles_gerais/lista_dav/csv/arquivo_final_backup_antes_normalizacao_{timestamp}.csv'
    
    # Ler arquivo original para backup
    arquivo_original = 'data/originais/controles_gerais/lista_dav/csv/arquivo_final.csv'
    df_original = pd.read_csv(arquivo_original)
    df_original.to_csv(arquivo_backup, index=False)
    print(f"📋 Backup original: {arquivo_backup}")
    
    # Salvar arquivo normalizado
    df.to_csv(arquivo_original, index=False)
    print(f"✅ Arquivo principal atualizado: {arquivo_original}")
    
    # Análise final
    print(f"\n📊 === ANÁLISE FINAL === 📊")
    print(f"📋 Total registros: {len(df):,}")
    print(f"🔢 OS válidos: {df['OS_numero'].notna().sum():,}")
    print(f"🔢 OS únicos: {df['OS_numero'].nunique():,}")
    
    # Distribuição por faixa
    os_nums = df['OS_numero'].dropna()
    
    faixa_1_1000 = (os_nums <= 1000).sum()
    faixa_1k_10k = ((os_nums > 1000) & (os_nums <= 10000)).sum()
    faixa_10k_100k = ((os_nums > 10000) & (os_nums <= 100000)).sum()
    faixa_maior = (os_nums > 100000).sum()
    
    print(f"📊 Distribuição por faixa:")
    print(f"   1-1.000: {faixa_1_1000:,}")
    print(f"   1k-10k: {faixa_1k_10k:,}")
    print(f"   10k-100k: {faixa_10k_100k:,}")
    print(f"   >100k: {faixa_maior:,}")
    
    return arquivo_original

def main():
    """Função principal"""
    print("🎯 === NORMALIZAÇÃO CORRETA DE NÚMEROS DAV === 🎯")
    print("🏪 Removendo prefixos: 42xxxx (Suzano) → xxxx")
    print("🏪 Removendo prefixos: 48xxxx (Mauá) → xxxx")
    
    # Normalizar
    df_normalizado = normalizar_dav_correto()
    
    # Salvar
    arquivo_final = salvar_arquivo_normalizado_correto(df_normalizado)
    
    print(f"\n🎉 === NORMALIZAÇÃO CONCLUÍDA === 🎉")
    print(f"✅ Prefixos 42xxxx e 48xxxx removidos")
    print(f"✅ Números DAV agora são números de OS limpos")
    print(f"✅ Arquivo atualizado: {arquivo_final}")
    print(f"✅ Backup criado da versão anterior")
    print(f"📅 Processado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()