#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validação COMPLETA do arquivo consolidado contra a estrutura da tabela core.clientes
"""

import pandas as pd
import re
from pathlib import Path
from datetime import datetime

# ================================================================================
# CONFIGURAÇÕES
# ================================================================================
DIR_BASE = Path(__file__).parent.parent
# Busca o arquivo mais recente
import glob
arquivos_possiveis = glob.glob(str(DIR_BASE / 'dados_processados' / 'originais' / 'clientes' / 'normalizados' / 'CLIENTES_FINAL_CORRIGIDO_*.csv'))
if arquivos_possiveis:
    ARQUIVO = Path(max(arquivos_possiveis, key=lambda x: Path(x).stat().st_mtime))
else:
    ARQUIVO = DIR_BASE / 'dados_processados' / 'originais' / 'clientes' / 'normalizados' / 'CLIENTES_OSS_VIXEN_CONSOLIDADO_20251109_131403.csv'

# ================================================================================
# FUNÇÕES DE VALIDAÇÃO
# ================================================================================

def validar_cpf(cpf):
    """Valida CPF com dígito verificador"""
    if not cpf or pd.isna(cpf):
        return True  # NULL é permitido
    
    cpf_str = str(cpf).strip()
    cpf_limpo = re.sub(r'[^\d]', '', cpf_str)
    
    if len(cpf_limpo) != 11:
        return False
    
    # CPFs inválidos conhecidos
    if cpf_limpo in ['00000000000', '11111111111', '22222222222', '33333333333',
                     '44444444444', '55555555555', '66666666666', '77777777777',
                     '88888888888', '99999999999']:
        return False
    
    # Verifica primeiro dígito
    soma = sum(int(cpf_limpo[i]) * (10 - i) for i in range(9))
    digito1 = 0 if (soma % 11) < 2 else 11 - (soma % 11)
    if int(cpf_limpo[9]) != digito1:
        return False
    
    # Verifica segundo dígito
    soma = sum(int(cpf_limpo[i]) * (11 - i) for i in range(10))
    digito2 = 0 if (soma % 11) < 2 else 11 - (soma % 11)
    if int(cpf_limpo[10]) != digito2:
        return False
    
    return True

def validar_email(email):
    """Valida formato de email"""
    if not email or pd.isna(email):
        return True  # NULL é permitido
    
    email_str = str(email).strip()
    pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    return re.match(pattern, email_str) is not None

def validar_data(data):
    """Valida se data não é futura"""
    if not data or pd.isna(data):
        return True  # NULL é permitido
    
    try:
        data_obj = pd.to_datetime(data)
        return data_obj <= pd.Timestamp.now()
    except:
        return False

def validar_sexo(sexo):
    """Valida sexo (M, F, O ou NULL)"""
    if not sexo or pd.isna(sexo):
        return True  # NULL é permitido
    
    return str(sexo).strip().upper() in ['M', 'F', 'O']

def validar_tamanho_campo(valor, max_length):
    """Valida tamanho máximo do campo"""
    if not valor or pd.isna(valor):
        return True
    
    return len(str(valor)) <= max_length

# ================================================================================
# VALIDAÇÃO PRINCIPAL
# ================================================================================

def validar_arquivo():
    print("="*80)
    print("VALIDAÇÃO COMPLETA DO ARQUIVO FINAL")
    print("="*80)
    print(f"\nArquivo: {ARQUIVO}")
    print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Lê arquivo
    print("\n1. Lendo arquivo...")
    df = pd.read_csv(ARQUIVO, sep=';', dtype={'cpf': str, 'id_legado': str})
    print(f"   ✓ {len(df)} registros carregados")
    
    # Lista de erros
    erros = []
    
    print("\n" + "="*80)
    print("VALIDAÇÕES POR COLUNA")
    print("="*80)
    
    # ========================================
    # 1. COLUNAS OBRIGATÓRIAS
    # ========================================
    print("\n1. Validando colunas obrigatórias...")
    
    colunas_esperadas = [
        'id_legado', 'nome', 'cpf', 'rg', 'data_nascimento', 'sexo',
        'email', 'status', 'origem', 'tags', 'observacoes', 'cliente_desde'
    ]
    
    colunas_faltando = [col for col in colunas_esperadas if col not in df.columns]
    if colunas_faltando:
        erros.append(f"Colunas faltando: {colunas_faltando}")
        print(f"   ❌ Colunas faltando: {colunas_faltando}")
    else:
        print(f"   ✓ Todas as colunas obrigatórias presentes")
    
    # Colunas extras (temporárias)
    colunas_extras = [col for col in df.columns if col not in colunas_esperadas]
    if colunas_extras:
        print(f"   ⚠️  Colunas extras (temporárias): {colunas_extras}")
    
    # ========================================
    # 2. NOME (NOT NULL, VARCHAR 200)
    # ========================================
    print("\n2. Validando NOME...")
    nomes_vazios = df['nome'].isna().sum()
    if nomes_vazios > 0:
        erros.append(f"NOME: {nomes_vazios} registros NULL (NOT NULL violado)")
        print(f"   ❌ {nomes_vazios} registros com nome NULL")
    else:
        print(f"   ✓ Todos os nomes preenchidos")
    
    nomes_longos = df[df['nome'].str.len() > 200]
    if len(nomes_longos) > 0:
        erros.append(f"NOME: {len(nomes_longos)} registros > 200 caracteres")
        print(f"   ❌ {len(nomes_longos)} nomes > 200 caracteres")
    else:
        print(f"   ✓ Todos os nomes ≤ 200 caracteres")
    
    # ========================================
    # 3. ID_LEGADO (UNIQUE, VARCHAR 50)
    # ========================================
    print("\n3. Validando ID_LEGADO...")
    id_duplicados = df['id_legado'].duplicated().sum()
    if id_duplicados > 0:
        erros.append(f"ID_LEGADO: {id_duplicados} IDs duplicados (UNIQUE violado)")
        print(f"   ❌ {id_duplicados} IDs duplicados")
        print(f"   Exemplos: {df[df['id_legado'].duplicated()]['id_legado'].head().tolist()}")
    else:
        print(f"   ✓ Todos os IDs únicos")
    
    ids_longos = df[df['id_legado'].str.len() > 50]
    if len(ids_longos) > 0:
        erros.append(f"ID_LEGADO: {len(ids_longos)} registros > 50 caracteres")
        print(f"   ❌ {len(ids_longos)} IDs > 50 caracteres")
    else:
        print(f"   ✓ Todos os IDs ≤ 50 caracteres")
    
    # ========================================
    # 4. CPF (UNIQUE, VARCHAR 14, VALIDAÇÃO)
    # ========================================
    print("\n4. Validando CPF...")
    cpfs_preenchidos = df['cpf'].notna()
    total_cpfs = cpfs_preenchidos.sum()
    print(f"   Total de CPFs: {total_cpfs} ({total_cpfs/len(df)*100:.1f}%)")
    
    # CPFs duplicados
    cpf_duplicados = df[cpfs_preenchidos]['cpf'].duplicated().sum()
    if cpf_duplicados > 0:
        erros.append(f"CPF: {cpf_duplicados} CPFs duplicados (UNIQUE violado)")
        print(f"   ❌ {cpf_duplicados} CPFs duplicados")
        dups = df[cpfs_preenchidos][df[cpfs_preenchidos]['cpf'].duplicated(keep=False)]
        print(f"   Exemplos: {dups[['nome', 'cpf']].head()}")
    else:
        print(f"   ✓ Todos os CPFs únicos")
    
    # Validação do algoritmo
    cpfs_invalidos = []
    for idx, row in df[cpfs_preenchidos].iterrows():
        if not validar_cpf(row['cpf']):
            cpfs_invalidos.append((idx, row['cpf'], row['nome']))
    
    if cpfs_invalidos:
        erros.append(f"CPF: {len(cpfs_invalidos)} CPFs inválidos (algoritmo)")
        print(f"   ❌ {len(cpfs_invalidos)} CPFs inválidos")
        for idx, cpf, nome in cpfs_invalidos[:5]:
            print(f"      Linha {idx}: {cpf} - {nome}")
    else:
        print(f"   ✓ Todos os CPFs válidos (algoritmo)")
    
    # Tamanho
    cpfs_longos = df[cpfs_preenchidos & (df['cpf'].str.len() > 14)]
    if len(cpfs_longos) > 0:
        erros.append(f"CPF: {len(cpfs_longos)} CPFs > 14 caracteres")
        print(f"   ❌ {len(cpfs_longos)} CPFs > 14 caracteres")
    else:
        print(f"   ✓ Todos os CPFs ≤ 14 caracteres")
    
    # ========================================
    # 5. EMAIL (VARCHAR 100, VALIDAÇÃO)
    # ========================================
    print("\n5. Validando EMAIL...")
    emails_preenchidos = df['email'].notna()
    total_emails = emails_preenchidos.sum()
    print(f"   Total de emails: {total_emails} ({total_emails/len(df)*100:.1f}%)")
    
    emails_invalidos = []
    for idx, row in df[emails_preenchidos].iterrows():
        if not validar_email(row['email']):
            emails_invalidos.append((idx, row['email'], row['nome']))
    
    if emails_invalidos:
        erros.append(f"EMAIL: {len(emails_invalidos)} emails inválidos (formato)")
        print(f"   ❌ {len(emails_invalidos)} emails inválidos")
        for idx, email, nome in emails_invalidos[:5]:
            print(f"      Linha {idx}: {email} - {nome}")
    else:
        print(f"   ✓ Todos os emails válidos")
    
    emails_longos = df[emails_preenchidos & (df['email'].str.len() > 100)]
    if len(emails_longos) > 0:
        erros.append(f"EMAIL: {len(emails_longos)} emails > 100 caracteres")
        print(f"   ❌ {len(emails_longos)} emails > 100 caracteres")
    else:
        print(f"   ✓ Todos os emails ≤ 100 caracteres")
    
    # ========================================
    # 6. DATA_NASCIMENTO (DATE, ≤ TODAY)
    # ========================================
    print("\n6. Validando DATA_NASCIMENTO...")
    datas_preenchidas = df['data_nascimento'].notna()
    total_datas = datas_preenchidas.sum()
    print(f"   Total de datas: {total_datas} ({total_datas/len(df)*100:.1f}%)")
    
    datas_futuras = []
    for idx, row in df[datas_preenchidas].iterrows():
        if not validar_data(row['data_nascimento']):
            datas_futuras.append((idx, row['data_nascimento'], row['nome']))
    
    if datas_futuras:
        erros.append(f"DATA_NASCIMENTO: {len(datas_futuras)} datas futuras")
        print(f"   ❌ {len(datas_futuras)} datas futuras")
        for idx, data, nome in datas_futuras[:5]:
            print(f"      Linha {idx}: {data} - {nome}")
    else:
        print(f"   ✓ Todas as datas ≤ hoje")
    
    # ========================================
    # 7. SEXO (CHAR 1, M/F/O)
    # ========================================
    print("\n7. Validando SEXO...")
    sexos_preenchidos = df['sexo'].notna()
    total_sexos = sexos_preenchidos.sum()
    print(f"   Total de sexos: {total_sexos} ({total_sexos/len(df)*100:.1f}%)")
    print(f"   Distribuição: {dict(df['sexo'].value_counts())}")
    
    sexos_invalidos = []
    for idx, row in df[sexos_preenchidos].iterrows():
        if not validar_sexo(row['sexo']):
            sexos_invalidos.append((idx, row['sexo'], row['nome']))
    
    if sexos_invalidos:
        erros.append(f"SEXO: {len(sexos_invalidos)} valores inválidos (deve ser M/F/O)")
        print(f"   ❌ {len(sexos_invalidos)} valores inválidos")
        for idx, sexo, nome in sexos_invalidos[:5]:
            print(f"      Linha {idx}: '{sexo}' - {nome}")
    else:
        print(f"   ✓ Todos os sexos válidos")
    
    # ========================================
    # 8. STATUS (DEFAULT 'ATIVO')
    # ========================================
    print("\n8. Validando STATUS...")
    print(f"   Distribuição: {dict(df['status'].value_counts())}")
    status_invalidos = df[~df['status'].isin(['ATIVO', 'INATIVO', 'BLOQUEADO'])]
    if len(status_invalidos) > 0:
        erros.append(f"STATUS: {len(status_invalidos)} valores inválidos")
        print(f"   ❌ {len(status_invalidos)} valores inválidos")
    else:
        print(f"   ✓ Todos os status válidos")
    
    # ========================================
    # 9. ORIGEM (VARCHAR 100)
    # ========================================
    print("\n9. Validando ORIGEM...")
    print(f"   Distribuição: {dict(df['origem'].value_counts())}")
    origens_longas = df[df['origem'].str.len() > 100]
    if len(origens_longas) > 0:
        erros.append(f"ORIGEM: {len(origens_longas)} valores > 100 caracteres")
        print(f"   ❌ {len(origens_longas)} valores > 100 caracteres")
    else:
        print(f"   ✓ Todos os valores ≤ 100 caracteres")
    
    # ========================================
    # 10. CLIENTE_DESDE (DATE)
    # ========================================
    print("\n10. Validando CLIENTE_DESDE...")
    cliente_desde_preenchido = df['cliente_desde'].notna()
    total_cliente_desde = cliente_desde_preenchido.sum()
    print(f"   Total preenchido: {total_cliente_desde} ({total_cliente_desde/len(df)*100:.1f}%)")
    
    # ========================================
    # RESUMO FINAL
    # ========================================
    print("\n" + "="*80)
    print("RESUMO DA VALIDAÇÃO")
    print("="*80)
    
    if erros:
        print(f"\n❌ ENCONTRADOS {len(erros)} TIPOS DE ERROS:\n")
        for i, erro in enumerate(erros, 1):
            print(f"{i}. {erro}")
        
        print("\n⚠️  O ARQUIVO NÃO ESTÁ PRONTO PARA IMPORTAÇÃO!")
        print("   Execute o script de correção automática.")
        return False
    else:
        print("\n✅ TODAS AS VALIDAÇÕES PASSARAM!")
        print("\n📊 ESTATÍSTICAS FINAIS:")
        print(f"   - Total de registros: {len(df)}")
        print(f"   - CPF: {total_cpfs} ({total_cpfs/len(df)*100:.1f}%)")
        print(f"   - Email: {total_emails} ({total_emails/len(df)*100:.1f}%)")
        print(f"   - Data Nasc: {total_datas} ({total_datas/len(df)*100:.1f}%)")
        print(f"   - Sexo: {total_sexos} ({total_sexos/len(df)*100:.1f}%)")
        print(f"   - Cliente Desde: {total_cliente_desde} ({total_cliente_desde/len(df)*100:.1f}%)")
        
        print("\n🎯 ARQUIVO PRONTO PARA IMPORTAÇÃO NO SUPABASE!")
        return True

if __name__ == '__main__':
    validar_arquivo()
