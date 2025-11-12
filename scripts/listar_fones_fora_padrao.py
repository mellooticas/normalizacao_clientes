import pandas as pd
import re

df = pd.read_csv('data/importacao_clientes/telefones_id_fone_principal_com_ddd11.csv', dtype=str)

# Regex para o padrão (XX) XXXXXXXXX ou (XX) XXXXXXXXXX
padrao = re.compile(r'^\(\d{2}\) \d{8,9}$')
fora_padrao = df[~df['fone'].apply(lambda x: bool(padrao.match(str(x))))]

fora_padrao.to_csv('data/importacao_clientes/telefones_fora_padrao.csv', index=False, encoding='utf-8')
print(f'Foram encontrados {len(fora_padrao)} telefones fora do padrão.')
