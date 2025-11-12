"""
ANÁLISE DE DUPLICAÇÕES ENTRE OSS_SUZANO_MAUA E VIXEN
Cruza informações para identificar clientes que podem estar duplicados:
- CPF (match exato)
- Nome + Data Nascimento (match fuzzy)
- Telefone (match exato)
- Email (match exato)
- Endereço (quando possível)
"""

import pandas as pd
from pathlib import Path
from fuzzywuzzy import fuzz
import re

# Caminhos
BASE_DIR = Path(__file__).parent.parent
OSS_PATH = BASE_DIR / 'dados_processados' / 'originais' / 'clientes' / 'normalizados' / 'OSS_SUZANO_MAUA.csv'
VIXEN_PATH = BASE_DIR / 'dados_processados' / 'originais' / 'clientes' / 'normalizados' / 'VIXEN.csv'
OUTPUT_PATH = BASE_DIR / 'dados_processados' / 'originais' / 'clientes' / 'normalizados' / 'RELATORIO_DUPLICACOES_OSS_VIXEN.csv'

print("=" * 80)
print("ANÁLISE DE DUPLICAÇÕES: OSS_SUZANO_MAUA vs VIXEN")
print("=" * 80)

# 1. Ler arquivos
print(f"\n1. Lendo arquivos...")
print(f"   - OSS_SUZANO_MAUA.csv")
df_oss = pd.read_csv(OSS_PATH, sep=';', dtype=str, encoding='utf-8')
print(f"     ✓ {len(df_oss):,} OSS")
print(f"     ✓ {df_oss['ID_CLIENTE'].nunique():,} clientes únicos")

print(f"   - VIXEN.csv")
df_vixen = pd.read_csv(VIXEN_PATH, sep=';', dtype=str, encoding='utf-8')
print(f"     ✓ {len(df_vixen):,} clientes VIXEN")

# 2. Preparar dados OSS (agrupar por cliente)
print(f"\n2. Agrupando OSS por cliente (pegando primeira OS)...")
df_oss_clientes = df_oss.groupby('ID_CLIENTE').first().reset_index()
print(f"   ✓ {len(df_oss_clientes):,} clientes OSS")

# 3. Normalizar campos para comparação
print(f"\n3. Normalizando campos para comparação...")

def normalizar_texto(texto):
    """Remove acentos, espaços extras e coloca em maiúsculas"""
    if pd.isna(texto):
        return ''
    texto = str(texto).upper().strip()
    # Remove espaços múltiplos
    texto = re.sub(r'\s+', ' ', texto)
    return texto

def normalizar_cpf(cpf):
    """Remove formatação do CPF"""
    if pd.isna(cpf):
        return ''
    return re.sub(r'\D', '', str(cpf))

def normalizar_telefone(tel):
    """Remove formatação do telefone"""
    if pd.isna(tel):
        return ''
    return re.sub(r'\D', '', str(tel))

# Normalizar OSS
df_oss_clientes['nome_norm'] = df_oss_clientes['NOME:'].apply(normalizar_texto)
df_oss_clientes['cpf_norm'] = df_oss_clientes['CPF'].apply(normalizar_cpf)
df_oss_clientes['email_norm'] = df_oss_clientes['EMAIL:'].apply(normalizar_texto)
df_oss_clientes['data_nasc'] = df_oss_clientes['DT NASC']

# Extrair telefones do OSS (tentar diferentes variações de nome da coluna)
if 'TELEFONE  :' in df_oss_clientes.columns:
    df_oss_clientes['tel_norm'] = df_oss_clientes['TELEFONE  :'].apply(normalizar_telefone)
elif 'TELEFONE:' in df_oss_clientes.columns:
    df_oss_clientes['tel_norm'] = df_oss_clientes['TELEFONE:'].apply(normalizar_telefone)
elif 'TELEFONE' in df_oss_clientes.columns:
    df_oss_clientes['tel_norm'] = df_oss_clientes['TELEFONE'].apply(normalizar_telefone)
else:
    df_oss_clientes['tel_norm'] = ''
    print(f"   ⚠️ Coluna TELEFONE não encontrada no OSS")

# Normalizar VIXEN
df_vixen['nome_norm'] = df_vixen['Nome Completo'].apply(normalizar_texto)
df_vixen['cpf_norm'] = df_vixen['Cliente'].apply(normalizar_cpf)  # CPF pode estar em 'Cliente'
df_vixen['email_norm'] = df_vixen['E-mail'].apply(normalizar_texto)
df_vixen['data_nasc'] = df_vixen['Dt de aniversário']

# Telefones VIXEN (montar de DDD + Fone.1, Fone.2, Fone.3)
def montar_telefone_vixen(row):
    ddd = str(row.get('DDD', '')).strip()
    fone1 = str(row.get('Fone.1', '')).strip()
    if ddd and fone1:
        return normalizar_telefone(f"({ddd}) {fone1}")
    return normalizar_telefone(fone1)

df_vixen['tel_norm'] = df_vixen.apply(montar_telefone_vixen, axis=1)

print(f"   ✓ Campos normalizados")

# 4. ANÁLISE 1: Match por CPF
print(f"\n4. ANÁLISE 1: Match por CPF...")
matches_cpf = []

# Determinar nome da coluna telefone no OSS
col_telefone_oss = None
for col in ['TELEFONE  :', 'TELEFONE:', 'TELEFONE']:
    if col in df_oss_clientes.columns:
        col_telefone_oss = col
        break

for idx, row_oss in df_oss_clientes.iterrows():
    if row_oss['cpf_norm'] and len(row_oss['cpf_norm']) == 11:
        matches = df_vixen[df_vixen['cpf_norm'] == row_oss['cpf_norm']]
        if len(matches) > 0:
            for _, row_vixen in matches.iterrows():
                matches_cpf.append({
                    'tipo_match': 'CPF_EXATO',
                    'confianca': '100%',
                    'oss_id': row_oss['ID_CLIENTE'],
                    'oss_nome': row_oss['NOME:'],
                    'oss_cpf': row_oss['CPF'],
                    'oss_data_nasc': row_oss['DT NASC'],
                    'oss_telefone': row_oss.get('TELEFONE  :', row_oss.get('TELEFONE:', '')),
                    'oss_email': row_oss['EMAIL:'],
                    'oss_loja': row_oss['LOJA'],
                    'vixen_id': row_vixen['ID'],
                    'vixen_nome': row_vixen['Nome Completo'],
                    'vixen_cpf': row_vixen['Cliente'],
                    'vixen_data_nasc': row_vixen['Dt de aniversário'],
                    'vixen_telefone': f"({row_vixen.get('DDD', '')}) {row_vixen.get('Fone.1', '')}",
                    'vixen_email': row_vixen['E-mail']
                })

print(f"   ✓ {len(matches_cpf)} matches por CPF")

# 5. ANÁLISE 2: Match por Email - DESABILITADO
print(f"\n5. ANÁLISE 2: Match por Email...")
print(f"   ⚠️  DESABILITADO - colaboradores usaram emails padrão/genéricos")
matches_email = []

# COMENTADO: Email não é confiável para match devido a emails genéricos
# for idx, row_oss in df_oss_clientes.iterrows():
#     if row_oss['email_norm'] and '@' in row_oss['email_norm']:
#         matches = df_vixen[df_vixen['email_norm'] == row_oss['email_norm']]
#         ...

print(f"   ✓ 0 matches por Email (desabilitado)")

# 6. ANÁLISE 3: Match por Telefone
print(f"\n6. ANÁLISE 3: Match por Telefone...")
matches_telefone = []

for idx, row_oss in df_oss_clientes.iterrows():
    if row_oss['tel_norm'] and len(row_oss['tel_norm']) >= 10:
        matches = df_vixen[df_vixen['tel_norm'] == row_oss['tel_norm']]
        if len(matches) > 0:
            # Verificar se já não foi encontrado
            ja_encontrado = any(m['oss_id'] == row_oss['ID_CLIENTE'] for m in matches_cpf + matches_email)
            if not ja_encontrado:
                for _, row_vixen in matches.iterrows():
                    matches_telefone.append({
                        'tipo_match': 'TELEFONE_EXATO',
                        'confianca': '85%',
                        'oss_id': row_oss['ID_CLIENTE'],
                        'oss_nome': row_oss['NOME:'],
                        'oss_cpf': row_oss['CPF'],
                        'oss_data_nasc': row_oss['DT NASC'],
                        'oss_telefone': row_oss.get('TELEFONE  :', row_oss.get('TELEFONE:', '')),
                        'oss_email': row_oss['EMAIL:'],
                        'oss_loja': row_oss['LOJA'],
                        'vixen_id': row_vixen['ID'],
                        'vixen_nome': row_vixen['Nome Completo'],
                        'vixen_cpf': row_vixen['Cliente'],
                        'vixen_data_nasc': row_vixen['Dt de aniversário'],
                        'vixen_telefone': f"({row_vixen.get('DDD', '')}) {row_vixen.get('Fone.1', '')}",
                        'vixen_email': row_vixen['E-mail']
                    })

print(f"   ✓ {len(matches_telefone)} matches por Telefone (novos)")

# 7. ANÁLISE 4: Match por Nome + Data Nascimento (Fuzzy)
print(f"\n7. ANÁLISE 4: Match por Nome + Data Nascimento (Fuzzy)...")
print(f"   (Isso pode levar alguns minutos...)")
matches_nome_data = []

ids_ja_encontrados = set([m['oss_id'] for m in matches_cpf + matches_email + matches_telefone])

contador = 0
total = len(df_oss_clientes[~df_oss_clientes['ID_CLIENTE'].isin(ids_ja_encontrados)])

for idx, row_oss in df_oss_clientes[~df_oss_clientes['ID_CLIENTE'].isin(ids_ja_encontrados)].iterrows():
    contador += 1
    if contador % 100 == 0:
        print(f"     Processando... {contador}/{total}")
    
    if row_oss['nome_norm'] and row_oss['data_nasc']:
        # Buscar por data nascimento igual
        matches_data = df_vixen[df_vixen['data_nasc'] == row_oss['data_nasc']]
        
        for _, row_vixen in matches_data.iterrows():
            # Calcular similaridade do nome
            similaridade = fuzz.ratio(row_oss['nome_norm'], row_vixen['nome_norm'])
            
            # Se similaridade >= 85%, considerar match
            if similaridade >= 85:
                matches_nome_data.append({
                    'tipo_match': 'NOME_DATA_FUZZY',
                    'confianca': f'{similaridade}%',
                    'oss_id': row_oss['ID_CLIENTE'],
                    'oss_nome': row_oss['NOME:'],
                    'oss_cpf': row_oss['CPF'],
                    'oss_data_nasc': row_oss['DT NASC'],
                    'oss_telefone': row_oss.get('TELEFONE  :', row_oss.get('TELEFONE:', '')),
                    'oss_email': row_oss['EMAIL:'],
                    'oss_loja': row_oss['LOJA'],
                    'vixen_id': row_vixen['ID'],
                    'vixen_nome': row_vixen['Nome Completo'],
                    'vixen_cpf': row_vixen['Cliente'],
                    'vixen_data_nasc': row_vixen['Dt de aniversário'],
                    'vixen_telefone': f"({row_vixen.get('DDD', '')}) {row_vixen.get('Fone.1', '')}",
                    'vixen_email': row_vixen['E-mail']
                })

print(f"   ✓ {len(matches_nome_data)} matches por Nome+Data (novos)")

# 8. Consolidar todos os matches
print(f"\n8. Consolidando resultados...")
todos_matches = matches_cpf + matches_email + matches_telefone + matches_nome_data
df_matches = pd.DataFrame(todos_matches)

if len(df_matches) > 0:
    # Ordenar por confiança
    df_matches['confianca_num'] = df_matches['confianca'].str.replace('%', '').astype(float)
    df_matches = df_matches.sort_values('confianca_num', ascending=False)
    df_matches = df_matches.drop('confianca_num', axis=1)

print(f"   ✓ {len(df_matches)} matches totais encontrados")

# 9. Estatísticas
print(f"\n9. Estatísticas:")
print(f"   Total de clientes OSS_SUZANO_MAUA: {len(df_oss_clientes):,}")
print(f"   Total de clientes VIXEN: {len(df_vixen):,}")
print(f"   ")
print(f"   Matches encontrados:")
print(f"     - Por CPF: {len(matches_cpf)}")
print(f"     - Por Email: {len(matches_email)}")
print(f"     - Por Telefone: {len(matches_telefone)}")
print(f"     - Por Nome+Data: {len(matches_nome_data)}")
print(f"     - TOTAL: {len(df_matches)}")
print(f"   ")
print(f"   Taxa de duplicação: {len(df_matches)/len(df_oss_clientes)*100:.2f}%")

# 10. Salvar relatório
print(f"\n10. Salvando relatório...")
if len(df_matches) > 0:
    df_matches.to_csv(OUTPUT_PATH, sep=';', index=False, encoding='utf-8')
    print(f"   ✓ Arquivo salvo: {OUTPUT_PATH.name}")
    print(f"   ✓ {len(df_matches)} registros")
    
    # Mostrar primeiros 10
    print(f"\n   Primeiros 10 matches:")
    for idx, row in df_matches.head(10).iterrows():
        print(f"     {idx+1}. {row['tipo_match']} ({row['confianca']}):")
        print(f"        OSS: {row['oss_nome']} | VIXEN: {row['vixen_nome']}")
else:
    print(f"   ⚠️ Nenhum match encontrado!")

print("\n" + "=" * 80)
print("✅ ANÁLISE DE DUPLICAÇÕES CONCLUÍDA!")
print("=" * 80)
