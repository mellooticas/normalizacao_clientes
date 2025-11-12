#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corrige erros de validação automaticamente
"""

import pandas as pd
import re
from pathlib import Path
from datetime import datetime

DIR_BASE = Path(__file__).parent.parent
DIR_DADOS = DIR_BASE / 'dados_processados' / 'originais' / 'clientes' / 'normalizados'

ARQUIVO_ENTRADA = DIR_DADOS / 'CLIENTES_OSS_VIXEN_CONSOLIDADO_20251109_131403.csv'
ARQUIVO_SAIDA = DIR_DADOS / f'CLIENTES_OSS_VIXEN_CONSOLIDADO_CORRIGIDO_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'

def corrigir_email(email):
    """Corrige emails inválidos"""
    if pd.isna(email) or email == '':
        return None
    
    email = str(email).strip()
    
    # Remove espaços
    email = email.replace(' ', '')
    
    # Textos que indicam ausência de email
    textos_invalidos = ['NAOPOSSUI', 'SEMMAIL', 'NAOTEM', 'SEMPOSSUI', 
                        'SEEMEMAIL', 'S/EMAIL', 'SEM', 'NAO', 'NÃOPOSSUI']
    
    email_upper = email.upper().replace('Ã', 'A')
    if any(texto in email_upper for texto in textos_invalidos):
        return None
    
    # Verifica se tem @ e .
    if '@' not in email or '.' not in email:
        return None
    
    # Regex básico
    pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    if re.match(pattern, email):
        return email.lower()
    
    return None

def corrigir_nome(nome):
    """Corrige nomes vazios ou inválidos"""
    if pd.isna(nome) or str(nome).strip() == '' or str(nome).strip().upper() == 'NAN':
        return 'CLIENTE SEM NOME'  # Nome padrão
    return str(nome).strip()

def corrigir_data_nascimento(data):
    """Corrige datas futuras"""
    if pd.isna(data) or data == '':
        return None
    
    try:
        data_dt = pd.to_datetime(data)
        hoje = pd.Timestamp.now()
        
        if data_dt > hoje:
            # Se for futura, provavelmente erro de digitação no ano
            # Ex: 2025 pode ser 1925
            if data_dt.year > 2020:
                # Subtrai 100 anos
                data_corrigida = data_dt.replace(year=data_dt.year - 100)
                if 1900 <= data_corrigida.year <= hoje.year:
                    return data_corrigida.strftime('%Y-%m-%d')
            return None  # Se não conseguir corrigir, anula
        
        return data
    except:
        return None

print("="*80)
print("CORREÇÃO AUTOMÁTICA DE ERROS")
print("="*80)

# Lê arquivo
df = pd.read_csv(ARQUIVO_ENTRADA, sep=';', dtype={'cpf': str, 'id_legado': str})
print(f"\nRegistros originais: {len(df)}")

# Estatísticas ANTES
print("\n" + "="*80)
print("ANTES DA CORREÇÃO")
print("="*80)
print(f"Emails válidos: {df['email'].notna().sum()}")
print(f"Nomes válidos: {df['nome'].notna().sum()}")
print(f"Datas válidas: {df['data_nascimento'].notna().sum()}")

# CORREÇÕES
print("\n" + "="*80)
print("APLICANDO CORREÇÕES")
print("="*80)

# 1. Corrige emails
print("\n1. Corrigindo emails...")
df['email'] = df['email'].apply(corrigir_email)
print(f"   ✓ Emails válidos agora: {df['email'].notna().sum()}")

# 2. Corrige nomes vazios
print("\n2. Corrigindo nomes vazios...")
nomes_antes = df['nome'].notna().sum()
df['nome'] = df['nome'].apply(corrigir_nome)
nomes_depois = df['nome'].notna().sum()
print(f"   ✓ Nomes corrigidos: {nomes_depois - nomes_antes}")

# 3. Corrige datas futuras
print("\n3. Corrigindo datas futuras...")
datas_antes = df['data_nascimento'].notna().sum()
df['data_nascimento'] = df['data_nascimento'].apply(corrigir_data_nascimento)
datas_depois = df['data_nascimento'].notna().sum()
print(f"   ✓ Datas válidas: {datas_depois} (antes: {datas_antes})")

# Estatísticas DEPOIS
print("\n" + "="*80)
print("DEPOIS DA CORREÇÃO")
print("="*80)
print(f"Emails válidos: {df['email'].notna().sum()} ({df['email'].notna().sum()/len(df)*100:.1f}%)")
print(f"Nomes válidos: {df['nome'].notna().sum()} ({df['nome'].notna().sum()/len(df)*100:.1f}%)")
print(f"Datas válidas: {df['data_nascimento'].notna().sum()} ({df['data_nascimento'].notna().sum()/len(df)*100:.1f}%)")

# Salva
df.to_csv(ARQUIVO_SAIDA, sep=';', index=False, encoding='utf-8', quoting=0, na_rep='')

print("\n" + "="*80)
print("ARQUIVO CORRIGIDO SALVO")
print("="*80)
print(f"\n✅ {ARQUIVO_SAIDA}")
print(f"\n🎉 Execute o validador novamente para confirmar:")
print(f"   python scripts/validar_antes_importar_supabase.py")
