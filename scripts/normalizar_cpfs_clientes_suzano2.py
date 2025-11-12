import pandas as pd
import re

arq_import = 'data/originais/clientes/clientes_suzano2_normalizado.csv'
arq_banco = 'data/originais/clientes/clientes_uuid_banco_completo.csv'

def cpf_valido(cpf):
    cpf = re.sub(r'\D', '', str(cpf))
    return len(cpf) == 11 and cpf.isdigit()

df_import = pd.read_csv(arq_import, dtype=str)
df_banco = pd.read_csv(arq_banco, dtype=str)
cpfs_banco = set(df_banco['cpf'].dropna())

antes = len(df_import)
# Normaliza CPFs inválidos para '0'
df_import['cpf'] = df_import['cpf'].apply(lambda x: x if cpf_valido(x) else '0')
# Remove registros cujo CPF já existe no banco, exceto se for '0'
df_import = df_import[~df_import['cpf'].isin(cpfs_banco) | (df_import['cpf'] == '0')]
depois = len(df_import)
df_import.to_csv(arq_import, index=False, encoding='utf-8')
print(f'Removidos {antes-depois} registros com cpf duplicado no banco ou normalizados para 0.')
