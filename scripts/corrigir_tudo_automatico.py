"""
CORREÇÃO AUTOMÁTICA COMPLETA
Aplica TODAS as correções necessárias no arquivo CLIENTES_OUTRAS_LOJAS.csv
para garantir 100% de compatibilidade com as constraints do banco
"""

import pandas as pd
from pathlib import Path
import re
from datetime import datetime

# Caminhos
BASE_DIR = Path(__file__).parent.parent
FILE_PATH = BASE_DIR / 'dados_processados' / 'originais' / 'clientes' / 'normalizados' / 'CLIENTES_OUTRAS_LOJAS.csv'

print("=" * 80)
print("CORREÇÃO AUTOMÁTICA COMPLETA")
print("=" * 80)

# 1. Ler arquivo
print(f"\n1. Lendo arquivo: {FILE_PATH.name}")
df = pd.read_csv(FILE_PATH, sep=';', dtype=str, encoding='utf-8')
total_original = len(df)
print(f"   ✓ {total_original:,} registros")

# ============================================================================
# CORREÇÃO 1: DATAS INVÁLIDAS
# ============================================================================
print(f"\n2. Corrigindo datas inválidas...")

def validar_data(data_str):
    """Verifica se a data é válida"""
    if pd.isna(data_str) or str(data_str).strip() == '':
        return False
    try:
        if str(data_str).endswith('-00') or '-00-' in str(data_str):
            return False
        data = datetime.strptime(str(data_str), '%Y-%m-%d')
        if data.year < 1900 or data.year > 2025:
            return False
        return True
    except:
        return False

correcoes_datas = 0
for col in ['data_nascimento', 'cliente_desde']:
    if col not in df.columns:
        continue
    
    for idx in range(len(df)):
        if pd.isna(df.at[idx, col]):
            continue
        
        if not validar_data(df.at[idx, col]):
            # Tentar usar data da linha anterior
            if idx > 0 and validar_data(df.at[idx - 1, col]):
                df.at[idx, col] = df.at[idx - 1, col]
                correcoes_datas += 1
            # Se não, tentar próxima linha
            elif idx < len(df) - 1 and validar_data(df.at[idx + 1, col]):
                df.at[idx, col] = df.at[idx + 1, col]
                correcoes_datas += 1
            else:
                df.at[idx, col] = None
                correcoes_datas += 1

print(f"   ✓ {correcoes_datas} datas corrigidas")

# ============================================================================
# CORREÇÃO 2: CPFs INVÁLIDOS
# ============================================================================
print(f"\n3. Limpando CPFs inválidos...")

def cpf_valido(cpf_str):
    """Valida CPF com algoritmo completo de dígitos verificadores"""
    if pd.isna(cpf_str) or str(cpf_str).strip() == '':
        return True  # NULL é válido
    
    cpf = re.sub(r'\D', '', str(cpf_str))
    
    if len(cpf) != 11:
        return False
    
    # Verifica se todos os dígitos são iguais
    if cpf == cpf[0] * 11:
        return False
    
    # Primeiros 2 dígitos devem ser >= 10 (região fiscal válida)
    if int(cpf[:2]) < 10:
        return False
    
    # Lista de CPFs conhecidos como inválidos
    cpfs_invalidos = [
        '00000000000', '11111111111', '22222222222', '33333333333',
        '44444444444', '55555555555', '66666666666', '77777777777',
        '88888888888', '99999999999', '12345678901', '12345678900'
    ]
    
    if cpf in cpfs_invalidos:
        return False
    
    # Validação dos dígitos verificadores
    # Calcula o primeiro dígito verificador
    soma = 0
    for i in range(9):
        soma += int(cpf[i]) * (10 - i)
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto
    
    if int(cpf[9]) != digito1:
        return False
    
    # Calcula o segundo dígito verificador
    soma = 0
    for i in range(10):
        soma += int(cpf[i]) * (11 - i)
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto
    
    if int(cpf[10]) != digito2:
        return False
    
    return True

correcoes_cpf = 0
if 'cpf' in df.columns:
    for idx, cpf in df['cpf'].items():
        if pd.notna(cpf) and not cpf_valido(cpf):
            df.at[idx, 'cpf'] = None
            correcoes_cpf += 1

print(f"   ✓ {correcoes_cpf} CPFs convertidos para NULL")

# ============================================================================
# CORREÇÃO 3: EMAILS INVÁLIDOS
# ============================================================================
print(f"\n4. Limpando emails inválidos...")

def email_valido(email_str):
    """Valida email"""
    if pd.isna(email_str) or str(email_str).strip() == '':
        return True  # NULL é válido
    
    email = str(email_str).strip().upper()
    
    valores_invalidos = [
        'N POSSUI', 'NAO POSSUI', 'NÃO POSSUI', 'SEM EMAIL', 
        'NENHUM', 'NAO TEM', 'NÃO TEM', 'N TEM',
        'S/EMAIL', 'SEM', 'NAO', 'NÃO', 'N',
        'NENHUMA', 'POSSUI', 'TEM', '0', '-'
    ]
    
    if email in valores_invalidos:
        return False
    
    if '@' not in email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email, re.IGNORECASE):
        return False
    
    return True

correcoes_email = 0
if 'email' in df.columns:
    for idx, email in df['email'].items():
        if pd.notna(email):
            # Remove espaços extras no início e fim
            email_limpo = str(email).strip()
            
            # Atualiza se tinha espaço
            if email_limpo != str(email):
                df.at[idx, 'email'] = email_limpo
                correcoes_email += 1
            
            # Valida se é email válido
            if not email_valido(email_limpo):
                df.at[idx, 'email'] = None
                correcoes_email += 1

print(f"   ✓ {correcoes_email} emails corrigidos/convertidos para NULL")

# ============================================================================
# VALIDAÇÃO FINAL
# ============================================================================
print(f"\n5. Validação final...")

erros_finais = 0

# Validar CPFs
if 'cpf' in df.columns:
    cpfs_invalidos = df['cpf'].apply(lambda x: not cpf_valido(x) if pd.notna(x) else False).sum()
    if cpfs_invalidos > 0:
        print(f"   ⚠️ Ainda há {cpfs_invalidos} CPFs inválidos!")
        erros_finais += cpfs_invalidos
    else:
        print(f"   ✅ Todos os CPFs válidos")

# Validar emails
if 'email' in df.columns:
    emails_invalidos = df['email'].apply(lambda x: not email_valido(x) if pd.notna(x) else False).sum()
    if emails_invalidos > 0:
        print(f"   ⚠️ Ainda há {emails_invalidos} emails inválidos!")
        erros_finais += emails_invalidos
    else:
        print(f"   ✅ Todos os emails válidos")

# Validar datas
for col in ['data_nascimento', 'cliente_desde']:
    if col in df.columns:
        datas_invalidas = df[col].apply(lambda x: not validar_data(x) if pd.notna(x) else False).sum()
        if datas_invalidas > 0:
            print(f"   ⚠️ Ainda há {datas_invalidas} {col} inválidas!")
            erros_finais += datas_invalidas
        else:
            print(f"   ✅ Todas as {col} válidas")

# ============================================================================
# SALVAR ARQUIVO
# ============================================================================
print(f"\n6. Salvando arquivo corrigido...")
df.to_csv(FILE_PATH, sep=';', index=False, encoding='utf-8')
print(f"   ✓ Arquivo salvo: {FILE_PATH.name}")
print(f"   ✓ {len(df):,} registros")

# ============================================================================
# RELATÓRIO FINAL
# ============================================================================
print("\n" + "=" * 80)
print("✅ CORREÇÃO AUTOMÁTICA CONCLUÍDA!")
print("=" * 80)

print(f"\nResumo das correções:")
print(f"  - Datas corrigidas: {correcoes_datas}")
print(f"  - CPFs limpos: {correcoes_cpf}")
print(f"  - Emails limpos: {correcoes_email}")
print(f"  - Total de correções: {correcoes_datas + correcoes_cpf + correcoes_email}")

if erros_finais == 0:
    print(f"\n✅ ARQUIVO 100% VALIDADO!")
    print(f"   Pronto para importação no banco sem erros!")
else:
    print(f"\n⚠️ ATENÇÃO: {erros_finais} erros ainda precisam ser corrigidos manualmente")

print("\n" + "=" * 80)
