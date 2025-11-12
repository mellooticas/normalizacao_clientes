#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validação final antes de importar no Supabase

Valida todos os constraints da tabela core.clientes:
- CPF válido (algoritmo dígito verificador)
- Email formato válido
- Data nascimento <= hoje
- Sexo em ('M', 'F', 'O')
- Status válido
- Campos obrigatórios preenchidos
"""

import pandas as pd
import re
from pathlib import Path
from datetime import datetime

# ================================================================================
# CONFIGURAÇÕES
# ================================================================================
DIR_BASE = Path(__file__).parent.parent
DIR_DADOS = DIR_BASE / 'dados_processados' / 'originais' / 'clientes' / 'normalizados'

ARQUIVO_ENTRADA = DIR_DADOS / 'CLIENTES_OSS_VIXEN_CONSOLIDADO_20251109_131403.csv'
ARQUIVO_ERROS = DIR_DADOS / f'ERROS_VALIDACAO_FINAL_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'

# ================================================================================
# FUNÇÕES DE VALIDAÇÃO
# ================================================================================

def validar_cpf(cpf):
    """Valida CPF com dígito verificador completo"""
    if pd.isna(cpf) or cpf == '':
        return True  # CPF é opcional
    
    cpf = str(cpf).strip()
    
    # Remove formatação
    cpf_limpo = re.sub(r'[^\d]', '', cpf)
    
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
    if pd.isna(email) or email == '':
        return True  # Email é opcional
    
    email = str(email).strip()
    
    # Regex básico de email
    pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    return bool(re.match(pattern, email))

def validar_data_nascimento(data):
    """Valida se data de nascimento é <= hoje"""
    if pd.isna(data) or data == '':
        return True  # Data é opcional
    
    try:
        data_dt = pd.to_datetime(data)
        hoje = pd.Timestamp.now()
        return data_dt <= hoje
    except:
        return False

def validar_sexo(sexo):
    """Valida se sexo está em M, F ou O"""
    if pd.isna(sexo) or sexo == '':
        return True  # Sexo é opcional
    
    return str(sexo).strip().upper() in ['M', 'F', 'O']

def validar_status(status):
    """Valida se status é válido"""
    if pd.isna(status) or status == '':
        return False  # Status é obrigatório
    
    valores_validos = ['ATIVO', 'INATIVO', 'BLOQUEADO', 'PENDENTE']
    return str(status).strip().upper() in valores_validos

def validar_nome(nome):
    """Valida se nome está preenchido (campo obrigatório)"""
    if pd.isna(nome) or str(nome).strip() == '':
        return False
    return True

# ================================================================================
# FUNÇÃO PRINCIPAL DE VALIDAÇÃO
# ================================================================================

def validar_arquivo(df):
    """Valida todas as regras e retorna DataFrame com erros"""
    
    erros = []
    
    print("\n" + "="*80)
    print("VALIDANDO CONSTRAINTS DO BANCO")
    print("="*80)
    
    total = len(df)
    
    # 1. NOME (obrigatório)
    print("\n1. Validando NOME (obrigatório)...")
    invalidos = df[~df['nome'].apply(validar_nome)]
    if len(invalidos) > 0:
        for idx, row in invalidos.iterrows():
            erros.append({
                'linha': idx + 2,  # +2 porque linha 1 é header e index começa em 0
                'id_legado': row['id_legado'],
                'campo': 'nome',
                'valor': row['nome'],
                'erro': 'Nome é obrigatório'
            })
    print(f"   ✓ Válidos: {total - len(invalidos)}/{total}")
    if len(invalidos) > 0:
        print(f"   ✗ Inválidos: {len(invalidos)}")
    
    # 2. CPF
    print("\n2. Validando CPF (algoritmo dígito verificador)...")
    invalidos = df[df['cpf'].notna() & ~df['cpf'].apply(validar_cpf)]
    if len(invalidos) > 0:
        for idx, row in invalidos.iterrows():
            erros.append({
                'linha': idx + 2,
                'id_legado': row['id_legado'],
                'campo': 'cpf',
                'valor': row['cpf'],
                'erro': 'CPF inválido (dígito verificador)'
            })
    cpfs_preenchidos = df['cpf'].notna().sum()
    print(f"   ✓ Válidos: {cpfs_preenchidos - len(invalidos)}/{cpfs_preenchidos} CPFs preenchidos")
    if len(invalidos) > 0:
        print(f"   ✗ Inválidos: {len(invalidos)}")
    
    # 3. EMAIL
    print("\n3. Validando EMAIL (formato)...")
    invalidos = df[df['email'].notna() & ~df['email'].apply(validar_email)]
    if len(invalidos) > 0:
        for idx, row in invalidos.iterrows():
            erros.append({
                'linha': idx + 2,
                'id_legado': row['id_legado'],
                'campo': 'email',
                'valor': row['email'],
                'erro': 'Email com formato inválido'
            })
    emails_preenchidos = df['email'].notna().sum()
    print(f"   ✓ Válidos: {emails_preenchidos - len(invalidos)}/{emails_preenchidos} emails preenchidos")
    if len(invalidos) > 0:
        print(f"   ✗ Inválidos: {len(invalidos)}")
    
    # 4. DATA DE NASCIMENTO
    print("\n4. Validando DATA_NASCIMENTO (<= hoje)...")
    invalidos = df[df['data_nascimento'].notna() & ~df['data_nascimento'].apply(validar_data_nascimento)]
    if len(invalidos) > 0:
        for idx, row in invalidos.iterrows():
            erros.append({
                'linha': idx + 2,
                'id_legado': row['id_legado'],
                'campo': 'data_nascimento',
                'valor': row['data_nascimento'],
                'erro': 'Data de nascimento futura ou inválida'
            })
    datas_preenchidas = df['data_nascimento'].notna().sum()
    print(f"   ✓ Válidos: {datas_preenchidas - len(invalidos)}/{datas_preenchidas} datas preenchidas")
    if len(invalidos) > 0:
        print(f"   ✗ Inválidos: {len(invalidos)}")
    
    # 5. SEXO
    print("\n5. Validando SEXO (M, F ou O)...")
    invalidos = df[df['sexo'].notna() & ~df['sexo'].apply(validar_sexo)]
    if len(invalidos) > 0:
        for idx, row in invalidos.iterrows():
            erros.append({
                'linha': idx + 2,
                'id_legado': row['id_legado'],
                'campo': 'sexo',
                'valor': row['sexo'],
                'erro': 'Sexo deve ser M, F ou O'
            })
    sexos_preenchidos = df['sexo'].notna().sum()
    print(f"   ✓ Válidos: {sexos_preenchidos - len(invalidos)}/{sexos_preenchidos} sexos preenchidos")
    if len(invalidos) > 0:
        print(f"   ✗ Inválidos: {len(invalidos)}")
    
    # 6. STATUS
    print("\n6. Validando STATUS (obrigatório)...")
    invalidos = df[~df['status'].apply(validar_status)]
    if len(invalidos) > 0:
        for idx, row in invalidos.iterrows():
            erros.append({
                'linha': idx + 2,
                'id_legado': row['id_legado'],
                'campo': 'status',
                'valor': row['status'],
                'erro': 'Status inválido ou vazio'
            })
    print(f"   ✓ Válidos: {total - len(invalidos)}/{total}")
    if len(invalidos) > 0:
        print(f"   ✗ Inválidos: {len(invalidos)}")
    
    # 7. ID_LEGADO (único)
    print("\n7. Validando ID_LEGADO (único)...")
    duplicados = df[df['id_legado'].duplicated(keep=False)]
    if len(duplicados) > 0:
        for id_legado, grupo in duplicados.groupby('id_legado'):
            for idx, row in grupo.iterrows():
                erros.append({
                    'linha': idx + 2,
                    'id_legado': row['id_legado'],
                    'campo': 'id_legado',
                    'valor': row['id_legado'],
                    'erro': f'ID_LEGADO duplicado (aparece {len(grupo)} vezes)'
                })
    print(f"   ✓ Únicos: {total - len(duplicados)}/{total}")
    if len(duplicados) > 0:
        print(f"   ✗ Duplicados: {len(duplicados)}")
    
    # 8. CPF (único quando preenchido)
    print("\n8. Validando CPF (único quando preenchido)...")
    cpfs_preenchidos = df[df['cpf'].notna()]
    duplicados = cpfs_preenchidos[cpfs_preenchidos['cpf'].duplicated(keep=False)]
    if len(duplicados) > 0:
        for cpf, grupo in duplicados.groupby('cpf'):
            for idx, row in grupo.iterrows():
                erros.append({
                    'linha': idx + 2,
                    'id_legado': row['id_legado'],
                    'campo': 'cpf',
                    'valor': row['cpf'],
                    'erro': f'CPF duplicado (aparece {len(grupo)} vezes)'
                })
    print(f"   ✓ Únicos: {len(cpfs_preenchidos) - len(duplicados)}/{len(cpfs_preenchidos)} CPFs")
    if len(duplicados) > 0:
        print(f"   ✗ Duplicados: {len(duplicados)}")
    
    return pd.DataFrame(erros) if erros else None

# ================================================================================
# MAIN
# ================================================================================

def main():
    print("="*80)
    print("VALIDAÇÃO FINAL ANTES DE IMPORTAR NO SUPABASE")
    print("="*80)
    print(f"\nData/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nArquivo de entrada: {ARQUIVO_ENTRADA}")
    
    # Lê arquivo
    print("\n" + "="*80)
    print("CARREGANDO DADOS")
    print("="*80)
    
    df = pd.read_csv(ARQUIVO_ENTRADA, sep=';', dtype={'cpf': str, 'id_legado': str})
    print(f"\n✓ {len(df)} registros carregados")
    
    # Valida
    df_erros = validar_arquivo(df)
    
    # Resultado
    print("\n" + "="*80)
    print("RESULTADO DA VALIDAÇÃO")
    print("="*80)
    
    if df_erros is None or len(df_erros) == 0:
        print("\n✅ TODOS OS REGISTROS ESTÃO VÁLIDOS!")
        print(f"\n🎉 Arquivo pronto para importação no Supabase:")
        print(f"   {ARQUIVO_ENTRADA}")
        print(f"\n📊 Resumo:")
        print(f"   - Total de registros: {len(df)}")
        print(f"   - Nome: {df['nome'].notna().sum()} (100%)")
        print(f"   - CPF: {df['cpf'].notna().sum()} ({df['cpf'].notna().sum()/len(df)*100:.1f}%)")
        print(f"   - Email: {df['email'].notna().sum()} ({df['email'].notna().sum()/len(df)*100:.1f}%)")
        print(f"   - Data Nasc: {df['data_nascimento'].notna().sum()} ({df['data_nascimento'].notna().sum()/len(df)*100:.1f}%)")
        print(f"   - Sexo: {df['sexo'].notna().sum()} ({df['sexo'].notna().sum()/len(df)*100:.1f}%)")
        print(f"   - Cliente Desde: {df['cliente_desde'].notna().sum()} ({df['cliente_desde'].notna().sum()/len(df)*100:.1f}%)")
    else:
        print(f"\n❌ ENCONTRADOS {len(df_erros)} ERROS DE VALIDAÇÃO")
        print(f"\n📄 Arquivo de erros salvo: {ARQUIVO_ERROS}")
        
        # Salva erros
        df_erros.to_csv(ARQUIVO_ERROS, sep=';', index=False, encoding='utf-8')
        
        # Mostra resumo por tipo de erro
        print("\n📊 Resumo por campo:")
        print(df_erros['campo'].value_counts().to_string())
        
        print("\n🔍 Primeiros 10 erros:")
        print(df_erros.head(10).to_string(index=False))
        
        print("\n⚠️  CORRIJA OS ERROS ANTES DE IMPORTAR!")
    
    print("\n" + "="*80)

if __name__ == '__main__':
    main()
