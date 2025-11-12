"""
Remove CPFs inválidos do arquivo CLIENTES_OUTRAS_LOJAS.csv
CPFs com todos os dígitos iguais (000.000.000-00, 111.111.111-11, etc) são inválidos

Estratégia:
- Se CPF tem todos dígitos iguais → NULL
- Se CPF é 000.000.000-00 → NULL
- Mantém CPFs válidos
"""

import pandas as pd
from pathlib import Path
import re

# Caminhos
BASE_DIR = Path(__file__).parent.parent
FILE_PATH = BASE_DIR / 'dados_processados' / 'originais' / 'clientes' / 'normalizados' / 'CLIENTES_OUTRAS_LOJAS.csv'

print("=" * 80)
print("LIMPANDO CPFs INVÁLIDOS")
print("=" * 80)

# 1. Ler arquivo
print(f"\n1. Lendo arquivo: {FILE_PATH.name}")
df = pd.read_csv(FILE_PATH, sep=';', dtype=str, encoding='utf-8')
print(f"   ✓ {len(df):,} registros")

# 2. Função para validar CPF
def cpf_valido(cpf_str):
    """Verifica se CPF é válido (não aceita todos dígitos iguais ou padrões inválidos)"""
    if pd.isna(cpf_str) or str(cpf_str).strip() == '':
        return False
    
    # Remove formatação
    cpf = re.sub(r'\D', '', str(cpf_str))
    
    # Verifica se tem 11 dígitos
    if len(cpf) != 11:
        return False
    
    # Verifica se todos os dígitos são iguais (inválido)
    if cpf == cpf[0] * 11:
        return False
    
    # Verifica se começa com muitos zeros (padrão comum de CPF fake)
    # Ex: 00000014411 = inválido, 000011954 = inválido
    if cpf.startswith('0000'):
        return False
    
    # Lista de CPFs conhecidos como inválidos
    cpfs_invalidos_conhecidos = [
        '00000000000', '11111111111', '22222222222', '33333333333',
        '44444444444', '55555555555', '66666666666', '77777777777',
        '88888888888', '99999999999', '12345678901', '12345678900'
    ]
    
    if cpf in cpfs_invalidos_conhecidos:
        return False
    
    return True

# 3. Identificar CPFs inválidos
print(f"\n2. Identificando CPFs inválidos...")

if 'cpf' in df.columns:
    cpfs_invalidos = df['cpf'].apply(lambda x: not cpf_valido(x) if pd.notna(x) else False)
    count_invalidos = cpfs_invalidos.sum()
    
    print(f"   ⚠️ CPFs inválidos encontrados: {count_invalidos}")
    
    if count_invalidos > 0:
        # Mostrar exemplos
        exemplos = df[cpfs_invalidos][['nome', 'cpf']].head(10)
        print(f"\n   Exemplos de CPFs inválidos:")
        for idx, row in exemplos.iterrows():
            print(f"     - {row['nome']}: {row['cpf']}")
else:
    print("   ⚠️ Coluna 'cpf' não encontrada!")
    exit(1)

# 4. Limpar CPFs inválidos
print(f"\n3. Limpando CPFs inválidos (convertendo para NULL)...")

if count_invalidos > 0:
    df.loc[cpfs_invalidos, 'cpf'] = None
    print(f"   ✓ {count_invalidos} CPFs convertidos para NULL")
else:
    print(f"   ✓ Nenhum CPF inválido para limpar")

# 5. Estatísticas finais
print(f"\n4. Estatísticas finais:")
total = len(df)
com_cpf = df['cpf'].notna().sum()
validos = df['cpf'].apply(cpf_valido).sum()

print(f"   Total de registros: {total}")
print(f"   Com CPF: {com_cpf} ({com_cpf/total*100:.1f}%)")
print(f"   CPFs válidos: {validos} ({validos/total*100:.1f}%)")
print(f"   Sem CPF (NULL): {total - com_cpf} ({(total - com_cpf)/total*100:.1f}%)")

# 6. Verificar se ainda há CPFs inválidos
cpfs_ainda_invalidos = df['cpf'].apply(lambda x: not cpf_valido(x) if pd.notna(x) else False).sum()

if cpfs_ainda_invalidos > 0:
    print(f"\n   ⚠️ ATENÇÃO: Ainda há {cpfs_ainda_invalidos} CPFs inválidos!")
else:
    print(f"\n   ✅ Todos os CPFs agora são válidos ou NULL!")

# 7. Salvar arquivo corrigido
print(f"\n5. Salvando arquivo corrigido...")
df.to_csv(FILE_PATH, sep=';', index=False, encoding='utf-8')
print(f"   ✓ Arquivo salvo: {FILE_PATH.name}")
print(f"   ✓ {len(df):,} registros")

print("\n" + "=" * 80)
print("✅ LIMPEZA DE CPFs CONCLUÍDA!")
print("=" * 80)
print(f"\nResumo:")
print(f"  - CPFs inválidos removidos: {count_invalidos}")
print(f"  - CPFs válidos mantidos: {validos}")
print(f"  - Registros sem CPF: {total - com_cpf}")
print("=" * 80)
