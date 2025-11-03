import pandas as pd
import re

df = pd.read_csv('data/importacao_clientes/telefones_id_fone.csv', dtype=str)
registros = []

for _, row in df.iterrows():
    id_val = row['id']
    fone = str(row['fone']).strip()
    if '/' in fone:
        fone = fone.split('/')[0].strip()
    if fone and fone.lower() != 'nan':
        registros.append({'id': id_val, 'fone': fone})

pd.DataFrame(registros).to_csv('data/importacao_clientes/telefones_id_fone_principal.csv', index=False, encoding='utf-8')
print(f'Arquivo gerado com {len(registros)} linhas (apenas telefone principal por id).')
