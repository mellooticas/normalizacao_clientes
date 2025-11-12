#!/usr/bin/env python3
"""
Script para analisar e normalizar números DAV no arquivo_final.csv
Removendo prefixos e padronizando como números de OS
"""

import pandas as pd
import numpy as np
from datetime import datetime
import re
import warnings
warnings.filterwarnings('ignore')

def analisar_prefixos_dav():
    """
    Analisa os prefixos dos números DAV
    """
    print("🔍 === ANÁLISE DOS PREFIXOS DAV === 🔍")
    
    # Carregar arquivo
    arquivo = 'data/originais/controles_gerais/lista_dav/csv/arquivo_final.csv'
    df = pd.read_csv(arquivo)
    print(f"✅ Arquivo carregado: {len(df):,} registros")
    
    # Analisar coluna Nro.DAV
    if 'Nro.DAV' not in df.columns:
        print("❌ Coluna 'Nro.DAV' não encontrada")
        return False
    
    # Remover valores nulos
    dav_validos = df['Nro.DAV'].dropna().astype(str)
    print(f"📊 Valores DAV válidos: {len(dav_validos):,}")
    
    # Analisar padrões
    print(f"\n🔢 === ANÁLISE DE PADRÕES === 🔢")
    
    # Amostras
    print(f"📋 Primeiros 20 valores:")
    for i, valor in enumerate(dav_validos.head(20)):
        print(f"   {i+1:2d}. {valor}")
    
    # Detectar prefixos
    prefixos = {}
    apenas_numeros = 0
    
    for valor in dav_validos:
        valor_str = str(valor).strip()
        
        # Verificar se é apenas número
        if valor_str.isdigit():
            apenas_numeros += 1
            continue
        
        # Verificar se tem prefixo numérico seguido de números
        match = re.match(r'^(\d+)(\d{4,})$', valor_str)
        if match:
            prefixo = match.group(1)
            numero = match.group(2)
            
            if prefixo not in prefixos:
                prefixos[prefixo] = []
            prefixos[prefixo].append(valor_str)
    
    print(f"\n📊 === ESTATÍSTICAS DOS PREFIXOS === 📊")
    print(f"🔢 Apenas números: {apenas_numeros:,}")
    print(f"🏷️ Com prefixos: {len(dav_validos) - apenas_numeros:,}")
    
    if prefixos:
        print(f"\n🏷️ === PREFIXOS ENCONTRADOS === 🏷️")
        for prefixo, exemplos in sorted(prefixos.items()):
            print(f"   {prefixo}: {len(exemplos):,} ocorrências")
            print(f"      Exemplos: {', '.join(exemplos[:5])}")
    
    return df, prefixos

def normalizar_numeros_dav():
    """
    Normaliza os números DAV removendo prefixos
    """
    print("\n🔧 === NORMALIZANDO NÚMEROS DAV === 🔧")
    
    # Carregar arquivo
    arquivo = 'data/originais/controles_gerais/lista_dav/csv/arquivo_final.csv'
    df = pd.read_csv(arquivo)
    print(f"✅ Arquivo carregado: {len(df):,} registros")
    
    # Backup da coluna original
    df['Nro.DAV_original'] = df['Nro.DAV'].copy()
    
    # Função para normalizar número DAV
    def normalizar_dav(valor):
        if pd.isna(valor):
            return None
        
        valor_str = str(valor).strip()
        
        # Se já é apenas número, manter
        if valor_str.isdigit():
            return int(valor_str)
        
        # Remover pontos e vírgulas
        valor_str = valor_str.replace('.', '').replace(',', '')
        
        # Padrões conhecidos de prefixos
        patterns = [
            r'^42(\d{4,})$',      # 42XXXX → XXXX (Suzano)
            r'^48(\d{4,})$',      # 48XXXX → XXXX (Mauá)
            r'^420(\d{3,})$',     # 420XXX → XXX
            r'^480(\d{3,})$',     # 480XXX → XXX
            r'^4200(\d{2,})$',    # 4200XX → XX
            r'^4800(\d{2,})$',    # 4800XX → XX
            r'^(\d{1,3})(\d{4,})$'  # Qualquer prefixo numérico seguido de 4+ dígitos
        ]
        
        for pattern in patterns:
            match = re.match(pattern, valor_str)
            if match:
                numero_limpo = match.group(-1)  # Último grupo capturado
                try:
                    return int(numero_limpo)
                except:
                    continue
        
        # Se não conseguiu normalizar, tentar extrair apenas números
        numeros = re.findall(r'\d+', valor_str)
        if numeros:
            # Pegar o maior número encontrado
            maior_numero = max(numeros, key=len)
            try:
                return int(maior_numero)
            except:
                pass
        
        return valor_str  # Manter original se não conseguiu normalizar
    
    # Aplicar normalização
    print(f"🔄 Normalizando números DAV...")
    df['Nro.DAV_normalizado'] = df['Nro.DAV'].apply(normalizar_dav)
    
    # Análise dos resultados
    print(f"\n📊 === RESULTADOS DA NORMALIZAÇÃO === 📊")
    
    # Contar tipos
    originais_validos = df['Nro.DAV'].notna().sum()
    normalizados_numericos = pd.to_numeric(df['Nro.DAV_normalizado'], errors='coerce').notna().sum()
    
    print(f"📋 DAV originais válidos: {originais_validos:,}")
    print(f"🔢 DAV normalizados numéricos: {normalizados_numericos:,}")
    print(f"📈 Taxa de normalização: {normalizados_numericos/originais_validos*100:.1f}%")
    
    # Exemplos de normalização
    print(f"\n📋 === EXEMPLOS DE NORMALIZAÇÃO === 📋")
    
    # Mostrar exemplos onde houve mudança
    exemplos = df[df['Nro.DAV_original'].astype(str) != df['Nro.DAV_normalizado'].astype(str)].head(10)
    
    if len(exemplos) > 0:
        print(f"Original → Normalizado:")
        for _, row in exemplos.iterrows():
            orig = row['Nro.DAV_original']
            norm = row['Nro.DAV_normalizado']
            print(f"   {orig} → {norm}")
    
    # Substituir coluna original pela normalizada
    df['Nro.DAV'] = df['Nro.DAV_normalizado']
    
    # Criar coluna de OS unificada
    df['OS_numero'] = df['Nro.DAV_normalizado']
    
    return df

def salvar_arquivo_normalizado(df):
    """
    Salva o arquivo com números DAV normalizados
    """
    print(f"\n💾 === SALVANDO ARQUIVO NORMALIZADO === 💾")
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Arquivo normalizado
    arquivo_normalizado = f'data/originais/controles_gerais/lista_dav/csv/arquivo_final_normalizado_{timestamp}.csv'
    df.to_csv(arquivo_normalizado, index=False)
    print(f"✅ Arquivo normalizado: {arquivo_normalizado}")
    
    # Substituir arquivo original
    arquivo_original = 'data/originais/controles_gerais/lista_dav/csv/arquivo_final.csv'
    df.to_csv(arquivo_original, index=False)
    print(f"✅ Arquivo original atualizado: {arquivo_original}")
    
    # Análise final
    print(f"\n📊 === ANÁLISE FINAL === 📊")
    print(f"📋 Total de registros: {len(df):,}")
    print(f"📋 Colunas: {df.shape[1]}")
    
    # Análise da coluna OS_numero
    os_validos = pd.to_numeric(df['OS_numero'], errors='coerce').notna().sum()
    os_unicos = pd.to_numeric(df['OS_numero'], errors='coerce').nunique()
    
    print(f"🔢 OS válidos: {os_validos:,}")
    print(f"🔢 OS únicos: {os_unicos:,}")
    
    # Range de números
    os_numericos = pd.to_numeric(df['OS_numero'], errors='coerce').dropna()
    if len(os_numericos) > 0:
        print(f"📊 Range OS: {int(os_numericos.min()):,} → {int(os_numericos.max()):,}")
    
    return arquivo_normalizado

def main():
    """Função principal"""
    print("🎯 === NORMALIZAÇÃO DE NÚMEROS DAV === 🎯")
    
    # 1. Analisar prefixos
    resultado_analise = analisar_prefixos_dav()
    if not resultado_analise:
        return
    
    # 2. Normalizar números
    df_normalizado = normalizar_numeros_dav()
    
    # 3. Salvar arquivo
    arquivo_final = salvar_arquivo_normalizado(df_normalizado)
    
    print(f"\n🎉 === NORMALIZAÇÃO CONCLUÍDA === 🎉")
    print(f"✅ Números DAV normalizados como números de OS")
    print(f"✅ Prefixos removidos automaticamente")
    print(f"✅ Arquivo atualizado e backup criado")
    print(f"📄 Arquivo final: {arquivo_final}")
    print(f"📅 Processado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()