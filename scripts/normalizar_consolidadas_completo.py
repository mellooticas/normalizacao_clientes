"""
Script Consolidado: Aplica TODAS as 8 normalizações em consolidadas.csv
- CPF → 000.000.000-00
- CEP (2 colunas) → 00000-000
- Telefones (4 colunas) → (XX) XXXXXXXXX
- Consolidar TELEFONE → CELULAR
- Como Conheceu → remover números, Title Case, preencher vazios
- LOJA → vazio="Suzano", "1"="Suzano 2"
- OS N° → remover .0
"""

import pandas as pd
import re
from pathlib import Path

# Caminhos
BASE_DIR = Path(__file__).parent.parent
CSV_PATH = BASE_DIR / 'dados_processados' / 'originais' / 'oss' / 'consolidadas' / 'consolidadas.csv'

print("=" * 80)
print("NORMALIZADOR CONSOLIDADO - TODAS AS 8 ETAPAS")
print("=" * 80)

# Leitura
print(f"\n1. Lendo arquivo: {CSV_PATH.name}")
df = pd.read_csv(CSV_PATH, sep=';', dtype=str, encoding='utf-8')
print(f"   ✓ {len(df):,} registros, {len(df.columns)} colunas")

# Limpar nomes das colunas
df.columns = df.columns.str.strip()

# ============================================================================
# ETAPA 1: NORMALIZAR CPF
# ============================================================================
print("\n" + "=" * 80)
print("ETAPA 1: NORMALIZANDO CPF")
print("=" * 80)

def normalizar_cpf(cpf):
    """Normaliza CPF para formato 000.000.000-00"""
    if pd.isna(cpf) or cpf == '':
        return cpf
    
    # Remove tudo que não é dígito
    cpf_limpo = re.sub(r'\D', '', str(cpf))
    
    # Remove .0 do final se existir
    if cpf_limpo.endswith('0') and len(cpf_limpo) > 11:
        cpf_limpo = cpf_limpo[:-2] if cpf_limpo[-2] == '0' else cpf_limpo[:-1]
    
    # Padding com zeros à esquerda
    cpf_limpo = cpf_limpo.zfill(11)
    
    # Se tiver mais de 11 dígitos, pega os 11 primeiros
    if len(cpf_limpo) > 11:
        cpf_limpo = cpf_limpo[:11]
    
    # Formata
    if len(cpf_limpo) == 11:
        return f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"
    
    return cpf

cpf_antes = df['CPF'].notna().sum()
df['CPF'] = df['CPF'].apply(normalizar_cpf)
cpf_depois = df['CPF'].str.match(r'^\d{3}\.\d{3}\.\d{3}-\d{2}$', na=False).sum()
print(f"   ✓ CPF normalizados: {cpf_depois:,} (antes: {cpf_antes:,})")

# ============================================================================
# ETAPA 2: NORMALIZAR CEP (2 COLUNAS)
# ============================================================================
print("\n" + "=" * 80)
print("ETAPA 2: NORMALIZANDO CEP (2 COLUNAS)")
print("=" * 80)

def normalizar_cep(cep):
    """Normaliza CEP para formato 00000-000"""
    if pd.isna(cep) or cep == '':
        return cep
    
    # Remove tudo que não é dígito
    cep_limpo = re.sub(r'\D', '', str(cep))
    
    # Padding com zeros à esquerda
    cep_limpo = cep_limpo.zfill(8)
    
    # Se tiver mais de 8 dígitos, pega os 8 primeiros
    if len(cep_limpo) > 8:
        cep_limpo = cep_limpo[:8]
    
    # Formata
    if len(cep_limpo) == 8:
        return f"{cep_limpo[:5]}-{cep_limpo[5:]}"
    
    return cep

# Normalizar ambas as colunas CEP
for col in ['CEP', 'CEP.1']:
    if col in df.columns:
        cep_antes = df[col].notna().sum()
        df[col] = df[col].apply(normalizar_cep)
        cep_depois = df[col].str.match(r'^\d{5}-\d{3}$', na=False).sum()
        print(f"   ✓ {col}: {cep_depois:,} normalizados (antes: {cep_antes:,})")

# ============================================================================
# ETAPA 3: NORMALIZAR TELEFONES (4 COLUNAS)
# ============================================================================
print("\n" + "=" * 80)
print("ETAPA 3: NORMALIZANDO TELEFONES (4 COLUNAS)")
print("=" * 80)

# Lista de textos comuns para remover
TEXTOS_REMOVER = [
    'LIGAR', 'RECADO', 'REC', 'MARCOS', 'NAMORADA', 'PAI', 'MAE', 
    'ROMULO', 'SOBRINHA', 'FILHA', 'FILHO', 'MARIDO', 'ESPOSA',
    'CASA', 'TRABALHO', 'CELULAR', 'FIXO', 'TIM', 'VIVO', 'CLARO', 'OI'
]

def limpar_telefone(telefone):
    """Remove textos comuns e mantém apenas números"""
    if pd.isna(telefone) or telefone == '':
        return telefone
    
    tel_str = str(telefone).upper()
    
    # Remove textos comuns
    for texto in TEXTOS_REMOVER:
        tel_str = tel_str.replace(texto, '')
    
    # Remove tudo que não é dígito
    tel_limpo = re.sub(r'\D', '', tel_str)
    
    return tel_limpo if tel_limpo else None

def normalizar_telefone(telefone):
    """Normaliza telefone para formato (XX) XXXXXXXXX"""
    if pd.isna(telefone) or telefone == '':
        return None
    
    # Limpa primeiro
    tel_limpo = limpar_telefone(telefone)
    
    if not tel_limpo or len(tel_limpo) < 8:
        return None
    
    # Remove zeros à esquerda
    tel_limpo = tel_limpo.lstrip('0')
    
    # Se tem 8 ou 9 dígitos, assume DDD 11
    if len(tel_limpo) in [8, 9]:
        tel_limpo = '11' + tel_limpo
    
    # Se tem 10 ou 11 dígitos, formata
    if len(tel_limpo) == 10:
        return f"({tel_limpo[:2]}) {tel_limpo[2:]}"
    elif len(tel_limpo) == 11:
        return f"({tel_limpo[:2]}) {tel_limpo[2:]}"
    elif len(tel_limpo) == 12:
        # Caso especial: 5511... → (11) 5...
        return f"({tel_limpo[:2]}) {tel_limpo[2:]}"
    elif len(tel_limpo) == 13:
        # Caso especial: 05511... → (11) 5...
        return f"({tel_limpo[1:3]}) {tel_limpo[3:]}"
    
    return None

# Normalizar 4 colunas de telefone
colunas_tel = ['TELEFONE :', 'CELULAR:', 'CELULAR:.1', 'CELULAR']
for col in colunas_tel:
    if col in df.columns:
        tel_antes = df[col].notna().sum()
        df[col] = df[col].apply(normalizar_telefone)
        tel_depois = df[col].notna().sum()
        tel_validos = df[col].str.match(r'^\(\d{2}\) \d{8,9}$', na=False).sum()
        print(f"   ✓ {col}: {tel_validos:,} válidos (antes: {tel_antes:,}, depois: {tel_depois:,})")

# ============================================================================
# ETAPA 4: CONSOLIDAR TELEFONE → CELULAR
# ============================================================================
print("\n" + "=" * 80)
print("ETAPA 4: CONSOLIDANDO TELEFONE → CELULAR")
print("=" * 80)

consolidacoes = []

if 'TELEFONE :' in df.columns:
    # Consolidar para CELULAR:
    if 'CELULAR:' in df.columns:
        mask = (df['CELULAR:'].isna()) & (df['TELEFONE :'].notna())
        qtd = mask.sum()
        df.loc[mask, 'CELULAR:'] = df.loc[mask, 'TELEFONE :']
        consolidacoes.append(f"CELULAR:: +{qtd}")
        print(f"   ✓ CELULAR:: +{qtd:,} preenchidos")
    
    # Consolidar para CELULAR:.1
    if 'CELULAR:.1' in df.columns:
        mask = (df['CELULAR:.1'].isna()) & (df['TELEFONE :'].notna())
        qtd = mask.sum()
        df.loc[mask, 'CELULAR:.1'] = df.loc[mask, 'TELEFONE :']
        consolidacoes.append(f"CELULAR:.1: +{qtd}")
        print(f"   ✓ CELULAR:.1: +{qtd:,} preenchidos")
    
    # Consolidar para CELULAR
    if 'CELULAR' in df.columns:
        mask = (df['CELULAR'].isna()) & (df['TELEFONE :'].notna())
        qtd = mask.sum()
        df.loc[mask, 'CELULAR'] = df.loc[mask, 'TELEFONE :']
        consolidacoes.append(f"CELULAR: +{qtd}")
        print(f"   ✓ CELULAR: +{qtd:,} preenchidos")

total_consolidado = sum(int(c.split('+')[1]) for c in consolidacoes)
print(f"   ✓ Total consolidado: {total_consolidado:,}")

# ============================================================================
# ETAPA 5: NORMALIZAR COMO CONHECEU
# ============================================================================
print("\n" + "=" * 80)
print("ETAPA 5: NORMALIZANDO COMO CONHECEU")
print("=" * 80)

def normalizar_como_conheceu(texto):
    """Remove números iniciais e aplica Title Case"""
    if pd.isna(texto) or texto == '':
        return texto
    
    texto_str = str(texto).strip()
    
    # Remove números no início (ex: "04 CLIENTES" → "CLIENTES")
    texto_limpo = re.sub(r'^\d+\s*-?\s*', '', texto_str)
    
    # Aplica Title Case
    texto_limpo = texto_limpo.title()
    
    return texto_limpo

if 'COMO CONHECEU' in df.columns:
    conheceu_antes = df['COMO CONHECEU'].notna().sum()
    df['COMO CONHECEU'] = df['COMO CONHECEU'].apply(normalizar_como_conheceu)
    conheceu_depois = df['COMO CONHECEU'].notna().sum()
    print(f"   ✓ Normalizados: {conheceu_depois:,} (antes: {conheceu_antes:,})")
    
    # Preencher vazios com "Já É Cliente"
    mask_vazio = df['COMO CONHECEU'].isna() | (df['COMO CONHECEU'] == '')
    qtd_preenchidos = mask_vazio.sum()
    df.loc[mask_vazio, 'COMO CONHECEU'] = 'Já É Cliente'
    print(f"   ✓ Preenchidos com 'Já É Cliente': {qtd_preenchidos:,}")

# ============================================================================
# ETAPA 6: AJUSTAR LOJA
# ============================================================================
print("\n" + "=" * 80)
print("ETAPA 6: AJUSTANDO LOJA")
print("=" * 80)

if 'LOJA' in df.columns:
    # Vazio → "Suzano"
    mask_vazio = df['LOJA'].isna() | (df['LOJA'] == '')
    qtd_vazio = mask_vazio.sum()
    df.loc[mask_vazio, 'LOJA'] = 'Suzano'
    
    # "1" → "Suzano 2"
    mask_um = df['LOJA'] == '1'
    qtd_um = mask_um.sum()
    df.loc[mask_um, 'LOJA'] = 'Suzano 2'
    
    print(f"   ✓ Vazio → 'Suzano': {qtd_vazio:,}")
    print(f"   ✓ '1' → 'Suzano 2': {qtd_um:,}")
    print(f"   ✓ Total ajustado: {qtd_vazio + qtd_um:,}")

# ============================================================================
# ETAPA 7: LIMPAR OS N°
# ============================================================================
print("\n" + "=" * 80)
print("ETAPA 7: LIMPANDO OS N°")
print("=" * 80)

def limpar_os_numero(os_num):
    """Remove .0 e mantém apenas números antes de . ou ,"""
    if pd.isna(os_num) or os_num == '':
        return os_num
    
    os_str = str(os_num).strip()
    
    # Pega apenas o que está antes do . ou ,
    if '.' in os_str:
        os_str = os_str.split('.')[0]
    elif ',' in os_str:
        os_str = os_str.split(',')[0]
    
    return os_str

if 'OS N°' in df.columns:
    os_antes = df['OS N°'].notna().sum()
    df['OS N°'] = df['OS N°'].apply(limpar_os_numero)
    os_depois = df['OS N°'].notna().sum()
    print(f"   ✓ OS N° limpas: {os_depois:,} (antes: {os_antes:,})")

# ============================================================================
# SALVAR ARQUIVO
# ============================================================================
print("\n" + "=" * 80)
print("SALVANDO ARQUIVO")
print("=" * 80)

df.to_csv(CSV_PATH, sep=';', index=False, encoding='utf-8')
print(f"   ✓ Arquivo salvo: {CSV_PATH.name}")
print(f"   ✓ {len(df):,} registros, {len(df.columns)} colunas")

# ============================================================================
# RESUMO FINAL
# ============================================================================
print("\n" + "=" * 80)
print("RESUMO FINAL - TODAS AS NORMALIZAÇÕES")
print("=" * 80)

print("\n✅ ETAPA 1 - CPF:")
print(f"   {cpf_depois:,} CPFs no formato 000.000.000-00")

print("\n✅ ETAPA 2 - CEP:")
if 'CEP' in df.columns:
    print(f"   CEP: {df['CEP'].str.match(r'^\d{5}-\d{3}$', na=False).sum():,} no formato 00000-000")
if 'CEP.1' in df.columns:
    print(f"   CEP.1: {df['CEP.1'].str.match(r'^\d{5}-\d{3}$', na=False).sum():,} no formato 00000-000")

print("\n✅ ETAPA 3 - TELEFONES:")
for col in colunas_tel:
    if col in df.columns:
        print(f"   {col}: {df[col].str.match(r'^\(\d{2}\) \d{8,9}$', na=False).sum():,} no formato (XX) XXXXXXXXX")

print("\n✅ ETAPA 4 - CONSOLIDAÇÃO:")
print(f"   Total de telefones consolidados: {total_consolidado:,}")

print("\n✅ ETAPA 5 - COMO CONHECEU:")
if 'COMO CONHECEU' in df.columns:
    print(f"   {df['COMO CONHECEU'].notna().sum():,} registros normalizados e preenchidos")

print("\n✅ ETAPA 6 - LOJA:")
if 'LOJA' in df.columns:
    print(f"   {df['LOJA'].notna().sum():,} registros com loja definida")

print("\n✅ ETAPA 7 - OS N°:")
if 'OS N°' in df.columns:
    print(f"   {df['OS N°'].notna().sum():,} OS limpas")

print("\n" + "=" * 80)
print("✅ NORMALIZAÇÃO COMPLETA CONCLUÍDA!")
print("=" * 80)
