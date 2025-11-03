import pandas as pd
import re

# Carregar arquivo consolidado
df = pd.read_csv('data/importacao_clientes/telefones_id_fone.csv', dtype=str)
registros = []


for _, row in df.iterrows():
    id_val = row['id']
    fones = re.split(r'[;,/| ]+', str(row['fone']))
    for fone in fones:
        fone = fone.strip()
        if fone and fone.lower() != 'nan':
            registros.append({'id': id_val, 'fone': fone})

pd.DataFrame(registros).to_csv('data/importacao_clientes/telefones_id_fone_normalizado.csv', index=False, encoding='utf-8')
print(f'Arquivo normalizado gerado com {len(registros)} linhas.')
