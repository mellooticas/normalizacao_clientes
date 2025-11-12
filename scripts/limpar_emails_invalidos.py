"""
Limpa emails inválidos do arquivo CLIENTES_OUTRAS_LOJAS.csv
Remove emails que não são emails válidos e converte para NULL

Emails inválidos comuns:
- N POSSUI
- SEM EMAIL
- NAO POSSUI
- Textos sem @
- Emails malformados
"""

import pandas as pd
from pathlib import Path
import re

# Caminhos
BASE_DIR = Path(__file__).parent.parent
FILE_PATH = BASE_DIR / 'dados_processados' / 'originais' / 'clientes' / 'normalizados' / 'CLIENTES_OUTRAS_LOJAS.csv'

print("=" * 80)
print("LIMPANDO EMAILS INVÁLIDOS")
print("=" * 80)

# 1. Ler arquivo
print(f"\n1. Lendo arquivo: {FILE_PATH.name}")
df = pd.read_csv(FILE_PATH, sep=';', dtype=str, encoding='utf-8')
print(f"   ✓ {len(df):,} registros")

# 2. Função para validar email
def email_valido(email_str):
    """Verifica se email é válido"""
    if pd.isna(email_str) or str(email_str).strip() == '':
        return False
    
    email = str(email_str).strip().upper()
    
    # Lista de valores que não são emails
    valores_invalidos = [
        'N POSSUI', 'NAO POSSUI', 'NÃO POSSUI', 'SEM EMAIL', 
        'NENHUM', 'NAO TEM', 'NÃO TEM', 'N TEM',
        'S/EMAIL', 'SEM', 'NAO', 'NÃO', 'N',
        'NENHUMA', 'POSSUI', 'TEM'
    ]
    
    if email in valores_invalidos:
        return False
    
    # Verifica se tem @
    if '@' not in email:
        return False
    
    # Regex básico para email
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email, re.IGNORECASE):
        return False
    
    return True

# 3. Identificar emails inválidos
print(f"\n2. Identificando emails inválidos...")

if 'email' in df.columns:
    emails_invalidos = df['email'].apply(lambda x: not email_valido(x) if pd.notna(x) else False)
    count_invalidos = emails_invalidos.sum()
    
    print(f"   ⚠️ Emails inválidos encontrados: {count_invalidos}")
    
    if count_invalidos > 0:
        # Mostrar exemplos únicos
        exemplos_unicos = df[emails_invalidos]['email'].value_counts().head(20)
        print(f"\n   Exemplos de emails inválidos (top 20):")
        for email, count in exemplos_unicos.items():
            print(f"     - '{email}': {count} ocorrências")
else:
    print("   ⚠️ Coluna 'email' não encontrada!")
    exit(1)

# 4. Limpar emails inválidos
print(f"\n3. Limpando emails inválidos (convertendo para NULL)...")

if count_invalidos > 0:
    # Mostrar alguns registros que serão alterados
    print(f"\n   Primeiros 10 registros que serão limpos:")
    exemplos = df[emails_invalidos][['nome', 'email']].head(10)
    for idx, row in exemplos.iterrows():
        print(f"     - {row['nome']}: '{row['email']}' → NULL")
    
    df.loc[emails_invalidos, 'email'] = None
    print(f"\n   ✓ {count_invalidos} emails convertidos para NULL")
else:
    print(f"   ✓ Nenhum email inválido para limpar")

# 5. Estatísticas finais
print(f"\n4. Estatísticas finais:")
total = len(df)
com_email = df['email'].notna().sum()
validos = df['email'].apply(email_valido).sum()

print(f"   Total de registros: {total}")
print(f"   Com email: {com_email} ({com_email/total*100:.1f}%)")
print(f"   Emails válidos: {validos} ({validos/total*100:.1f}%)")
print(f"   Sem email (NULL): {total - com_email} ({(total - com_email)/total*100:.1f}%)")

# 6. Verificar se ainda há emails inválidos
emails_ainda_invalidos = df['email'].apply(lambda x: not email_valido(x) if pd.notna(x) else False).sum()

if emails_ainda_invalidos > 0:
    print(f"\n   ⚠️ ATENÇÃO: Ainda há {emails_ainda_invalidos} emails inválidos!")
    print(f"\n   Emails ainda inválidos:")
    exemplos = df[df['email'].apply(lambda x: not email_valido(x) if pd.notna(x) else False)]['email'].head(10)
    for email in exemplos:
        print(f"     - {email}")
else:
    print(f"\n   ✅ Todos os emails agora são válidos ou NULL!")

# 7. Salvar arquivo corrigido
print(f"\n5. Salvando arquivo corrigido...")
df.to_csv(FILE_PATH, sep=';', index=False, encoding='utf-8')
print(f"   ✓ Arquivo salvo: {FILE_PATH.name}")
print(f"   ✓ {len(df):,} registros")

print("\n" + "=" * 80)
print("✅ LIMPEZA DE EMAILS CONCLUÍDA!")
print("=" * 80)
print(f"\nResumo:")
print(f"  - Emails inválidos removidos: {count_invalidos}")
print(f"  - Emails válidos mantidos: {validos}")
print(f"  - Registros sem email: {total - com_email}")
print("=" * 80)
