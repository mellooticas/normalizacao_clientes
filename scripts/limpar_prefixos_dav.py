#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Remove prefixos de lojas da coluna Nro.DAV
Prefixos comuns: 10, 11, 12, 13, etc (primeiros 2 dígitos)
"""

import pandas as pd

arquivo_entrada = '1_normalizacao/dados_processados/originais/controles_gerais/lista_dav/lista_sem_dav.csv'
arquivo_saida = '1_normalizacao/dados_processados/originais/controles_gerais/lista_dav/lista_sem_dav_limpo.csv'

print("="*80)
print("🔧 REMOVENDO PREFIXOS DE LOJAS - Nro.DAV")
print("="*80)

# Ler CSV
print("\n📖 Lendo arquivo...")
df = pd.read_csv(arquivo_entrada, sep=';', encoding='utf-8')
print(f"✅ {len(df):,} linhas carregadas")

print(f"\n📊 Exemplos ANTES da limpeza:")
print(df['Nro.DAV'].head(10).tolist())

# Função para remover prefixo da loja
def remover_prefixo_loja(nro_dav):
    """
    Remove o prefixo da loja do número DAV
    Prefixos conhecidos: 9, 10, 11, 12, 42, 48, etc
    """
    if pd.isna(nro_dav):
        return None
    
    # Converter para string e limpar
    nro_str = str(nro_dav).strip()
    
    # Remover caracteres não numéricos (exceto números)
    nro_str = ''.join(c for c in nro_str if c.isdigit())
    
    if not nro_str:
        return None
    
    # Lista de prefixos conhecidos (do maior para o menor)
    prefixos_conhecidos = ['48', '42', '12', '11', '10', '9']
    
    for prefixo in prefixos_conhecidos:
        if nro_str.startswith(prefixo):
            # Remover o prefixo
            numero_sem_prefixo = nro_str[len(prefixo):]
            return numero_sem_prefixo if numero_sem_prefixo else nro_str
    
    # Se não encontrou prefixo conhecido, retornar como está
    return nro_str

# Aplicar limpeza
print(f"\n🔧 Removendo prefixos...")
df['Nro.DAV_original'] = df['Nro.DAV'].copy()
df['Nro.DAV'] = df['Nro.DAV'].apply(remover_prefixo_loja)

print(f"\n📊 Exemplos DEPOIS da limpeza:")
for idx in range(min(10, len(df))):
    original = df.loc[idx, 'Nro.DAV_original']
    limpo = df.loc[idx, 'Nro.DAV']
    print(f"   {original} → {limpo}")

# Remover coluna auxiliar
df = df.drop(columns=['Nro.DAV_original'])

# Salvar
print(f"\n💾 Salvando arquivo...")
df.to_csv(arquivo_saida, index=False, sep=';', encoding='utf-8')

print(f"\n✅ Arquivo salvo: {arquivo_saida}")
print(f"📊 {len(df):,} linhas processadas")

print("\n" + "="*80)
print("✅ LIMPEZA CONCLUÍDA!")
print("="*80)
