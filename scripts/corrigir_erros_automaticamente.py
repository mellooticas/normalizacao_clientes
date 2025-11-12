#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Correção automática dos erros encontrados na validação
"""

import pandas as pd
import re
from pathlib import Path
from datetime import datetime

# ================================================================================
# CONFIGURAÇÕES
# ================================================================================
DIR_BASE = Path(__file__).parent.parent
ARQUIVO_ENTRADA = DIR_BASE / 'dados_processados' / 'originais' / 'clientes' / 'normalizados' / 'CLIENTES_OSS_VIXEN_CONSOLIDADO_20251109_131403.csv'
ARQUIVO_SAIDA = DIR_BASE / 'dados_processados' / 'originais' / 'clientes' / 'normalizados' / f'CLIENTES_FINAL_CORRIGIDO_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'

print("="*80)
print("CORREÇÃO AUTOMÁTICA DE ERROS")
print("="*80)
print(f"\nArquivo entrada: {ARQUIVO_ENTRADA}")
print(f"Arquivo saída: {ARQUIVO_SAIDA}")

# Lê arquivo
print("\n1. Lendo arquivo...")
df = pd.read_csv(ARQUIVO_ENTRADA, sep=';', dtype={'cpf': str, 'id_legado': str})
print(f"   ✓ {len(df)} registros carregados")

correcoesfeitas = []

# ========================================
# CORREÇÃO 1: NOME NULL
# ========================================
print("\n2. Corrigindo NOME NULL...")
nomes_vazios = df['nome'].isna()
if nomes_vazios.sum() > 0:
    print(f"   Encontrados: {nomes_vazios.sum()}")
    # Preenche com "NOME NÃO INFORMADO" + ID
    for idx in df[nomes_vazios].index:
        df.at[idx, 'nome'] = f"CLIENTE_{df.at[idx, 'id_legado']}"
    print(f"   ✓ Corrigidos: {nomes_vazios.sum()}")
    correcoesfeitas.append(f"NOME: {nomes_vazios.sum()} registros preenchidos")
else:
    print("   ✓ Nenhum erro encontrado")

# ========================================
# CORREÇÃO 2: EMAILS INVÁLIDOS
# ========================================
print("\n3. Corrigindo EMAILS inválidos...")

def validar_email(email):
    """Valida formato de email"""
    if not email or pd.isna(email):
        return True
    email_str = str(email).strip()
    pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    return re.match(pattern, email_str) is not None

emails_preenchidos = df['email'].notna()
emails_invalidos = []

for idx in df[emails_preenchidos].index:
    email = df.at[idx, 'email']
    
    # Remove espaços
    email_limpo = str(email).strip()
    
    # Casos específicos de texto
    if email_limpo.upper() in ['NÃO TEM E-MAIL', 'SEM EMAIL', 'NAO TEM', 'NÃO TEM', 'SEM', 'N TEM']:
        df.at[idx, 'email'] = None
        emails_invalidos.append(idx)
        continue
    
    # Remove espaços no meio do email
    if ' ' in email_limpo:
        email_limpo = email_limpo.replace(' ', '')
    
    # Valida depois de limpar
    if not validar_email(email_limpo):
        df.at[idx, 'email'] = None
        emails_invalidos.append(idx)
    elif email_limpo != email:
        df.at[idx, 'email'] = email_limpo

if emails_invalidos:
    print(f"   ✓ Corrigidos: {len(emails_invalidos)} emails inválidos → NULL")
    correcoesfeitas.append(f"EMAIL: {len(emails_invalidos)} inválidos removidos")
else:
    print("   ✓ Nenhum erro encontrado")

# ========================================
# CORREÇÃO 3: DATAS FUTURAS
# ========================================
print("\n4. Corrigindo DATAS FUTURAS...")

datas_preenchidas = df['data_nascimento'].notna()
datas_futuras = []

for idx in df[datas_preenchidas].index:
    data = df.at[idx, 'data_nascimento']
    try:
        data_obj = pd.to_datetime(data)
        if data_obj > pd.Timestamp.now():
            # Remove datas futuras
            df.at[idx, 'data_nascimento'] = None
            datas_futuras.append(idx)
    except:
        # Data inválida
        df.at[idx, 'data_nascimento'] = None
        datas_futuras.append(idx)

if datas_futuras:
    print(f"   ✓ Corrigidas: {len(datas_futuras)} datas futuras → NULL")
    correcoesfeitas.append(f"DATA_NASCIMENTO: {len(datas_futuras)} datas futuras removidas")
else:
    print("   ✓ Nenhum erro encontrado")

# ========================================
# REMOÇÃO DE COLUNAS TEMPORÁRIAS
# ========================================
print("\n5. Removendo colunas temporárias...")
colunas_temporarias = ['telefone_principal', 'celular']
colunas_remover = [col for col in colunas_temporarias if col in df.columns]

if colunas_remover:
    df = df.drop(columns=colunas_remover)
    print(f"   ✓ Removidas: {colunas_remover}")
    correcoesfeitas.append(f"COLUNAS: {len(colunas_remover)} temporárias removidas")
else:
    print("   ✓ Nenhuma coluna temporária encontrada")

# ========================================
# SALVAR ARQUIVO CORRIGIDO
# ========================================
print("\n6. Salvando arquivo corrigido...")
df.to_csv(ARQUIVO_SAIDA, sep=';', index=False, encoding='utf-8', quoting=0, na_rep='')
print(f"   ✓ Arquivo salvo: {ARQUIVO_SAIDA}")

# ========================================
# RESUMO
# ========================================
print("\n" + "="*80)
print("RESUMO DAS CORREÇÕES")
print("="*80)

if correcoesfeitas:
    print(f"\n✅ {len(correcoesfeitas)} TIPOS DE CORREÇÕES APLICADAS:\n")
    for i, correcao in enumerate(correcoesfeitas, 1):
        print(f"{i}. {correcao}")
else:
    print("\n✓ Nenhuma correção necessária")

print("\n" + "="*80)
print("ESTATÍSTICAS FINAIS")
print("="*80)
print(f"\nTotal de registros: {len(df)}")
print(f"CPF: {df['cpf'].notna().sum()} ({df['cpf'].notna().sum()/len(df)*100:.1f}%)")
print(f"Email: {df['email'].notna().sum()} ({df['email'].notna().sum()/len(df)*100:.1f}%)")
print(f"Data Nasc: {df['data_nascimento'].notna().sum()} ({df['data_nascimento'].notna().sum()/len(df)*100:.1f}%)")
print(f"Sexo: {df['sexo'].notna().sum()} ({df['sexo'].notna().sum()/len(df)*100:.1f}%)")
print(f"Cliente Desde: {df['cliente_desde'].notna().sum()} ({df['cliente_desde'].notna().sum()/len(df)*100:.1f}%)")

print("\n" + "="*80)
print("✅ CORREÇÃO CONCLUÍDA!")
print("="*80)
print("\n⏭️  Próximo passo: Execute o script de validação novamente para confirmar.")
