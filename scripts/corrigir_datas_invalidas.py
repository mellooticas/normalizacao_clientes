"""
Corrige datas inválidas no arquivo CLIENTES_OUTRAS_LOJAS.csv
como "1900-01-00" que causam erro no PostgreSQL

Estratégia:
- Se data inválida, usa a data da linha anterior (se válida)
- Se linha anterior também inválida, usa a próxima linha válida
- Se nenhuma válida, usa NULL
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

# Caminhos
BASE_DIR = Path(__file__).parent.parent
FILE_PATH = BASE_DIR / 'dados_processados' / 'originais' / 'clientes' / 'normalizados' / 'CLIENTES_OUTRAS_LOJAS.csv'

print("=" * 80)
print("CORRIGINDO DATAS INVÁLIDAS")
print("=" * 80)

# 1. Ler arquivo
print(f"\n1. Lendo arquivo: {FILE_PATH.name}")
df = pd.read_csv(FILE_PATH, sep=';', dtype=str, encoding='utf-8')
print(f"   ✓ {len(df):,} registros")

# 2. Função para validar data
def validar_data(data_str):
    """Verifica se a data é válida"""
    if pd.isna(data_str) or str(data_str).strip() == '':
        return False
    
    try:
        # Tenta parsear a data
        data = datetime.strptime(str(data_str), '%Y-%m-%d')
        
        # Verifica se dia é 00 (inválido)
        if str(data_str).endswith('-00'):
            return False
            
        # Verifica se mês é 00 (inválido)
        if '-00-' in str(data_str):
            return False
            
        # Verifica se a data é razoável (não muito antiga ou futura)
        if data.year < 1900 or data.year > 2025:
            return False
            
        return True
    except:
        return False

# 3. Identificar datas inválidas
print(f"\n2. Identificando datas inválidas...")

colunas_data = ['data_nascimento', 'cliente_desde']
total_invalidas = 0

for col in colunas_data:
    if col in df.columns:
        invalidas = df[col].apply(lambda x: not validar_data(x) if pd.notna(x) else False)
        count_invalidas = invalidas.sum()
        total_invalidas += count_invalidas
        
        if count_invalidas > 0:
            print(f"   ⚠️ {col}: {count_invalidas} datas inválidas")
            # Mostrar exemplos
            exemplos = df[invalidas][col].head(5).tolist()
            print(f"      Exemplos: {exemplos}")

if total_invalidas == 0:
    print(f"   ✅ Nenhuma data inválida encontrada!")
else:
    print(f"   ⚠️ Total: {total_invalidas} datas inválidas")

# 4. Corrigir datas inválidas
print(f"\n3. Corrigindo datas inválidas...")

correcoes = 0

for col in colunas_data:
    if col not in df.columns:
        continue
        
    for idx in range(len(df)):
        if pd.isna(df.at[idx, col]):
            continue
            
        if not validar_data(df.at[idx, col]):
            data_original = df.at[idx, col]
            data_corrigida = None
            
            # Tentar usar data da linha anterior
            if idx > 0 and validar_data(df.at[idx - 1, col]):
                data_corrigida = df.at[idx - 1, col]
            
            # Se não funcionou, tentar próxima linha
            elif idx < len(df) - 1 and validar_data(df.at[idx + 1, col]):
                data_corrigida = df.at[idx + 1, col]
            
            # Se não encontrou nenhuma válida, buscar a próxima válida no dataset
            else:
                for i in range(idx + 2, min(idx + 50, len(df))):
                    if validar_data(df.at[i, col]):
                        data_corrigida = df.at[i, col]
                        break
            
            # Aplicar correção
            if data_corrigida:
                df.at[idx, col] = data_corrigida
                correcoes += 1
                print(f"   ✓ Linha {idx + 2}: {col} '{data_original}' → '{data_corrigida}'")
            else:
                # Se não encontrou nenhuma válida, deixar NULL
                df.at[idx, col] = None
                correcoes += 1
                print(f"   ⚠️ Linha {idx + 2}: {col} '{data_original}' → NULL (sem data válida próxima)")

print(f"\n   ✓ {correcoes} correções realizadas")

# 5. Validar resultado
print(f"\n4. Validando resultado...")

total_invalidas_final = 0
for col in colunas_data:
    if col in df.columns:
        invalidas = df[col].apply(lambda x: not validar_data(x) if pd.notna(x) else False)
        count_invalidas = invalidas.sum()
        total_invalidas_final += count_invalidas

if total_invalidas_final == 0:
    print(f"   ✅ Todas as datas agora são válidas!")
else:
    print(f"   ⚠️ Ainda restam {total_invalidas_final} datas inválidas")

# 6. Estatísticas finais
print(f"\n5. Estatísticas finais:")
for col in colunas_data:
    if col in df.columns:
        total = len(df)
        preenchidas = df[col].notna().sum()
        validas = df[col].apply(validar_data).sum()
        print(f"   {col}:")
        print(f"     - Total: {total}")
        print(f"     - Preenchidas: {preenchidas} ({preenchidas/total*100:.1f}%)")
        print(f"     - Válidas: {validas} ({validas/total*100:.1f}%)")
        print(f"     - NULL: {total - preenchidas}")

# 7. Salvar arquivo corrigido
print(f"\n6. Salvando arquivo corrigido...")
df.to_csv(FILE_PATH, sep=';', index=False, encoding='utf-8')
print(f"   ✓ Arquivo salvo: {FILE_PATH.name}")
print(f"   ✓ {len(df):,} registros")

print("\n" + "=" * 80)
print("✅ CORREÇÃO DE DATAS CONCLUÍDA!")
print("=" * 80)
print(f"\nResumo:")
print(f"  - Datas inválidas encontradas: {total_invalidas}")
print(f"  - Correções realizadas: {correcoes}")
print(f"  - Datas inválidas restantes: {total_invalidas_final}")
print("=" * 80)
