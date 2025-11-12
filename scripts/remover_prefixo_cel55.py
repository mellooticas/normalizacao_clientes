import pandas as pd
import re

df = pd.read_csv('data/importacao_clientes/telefones_id_fone_principal.csv', dtype=str)

def remover_prefixo(fone):
    fone = str(fone)
    if fone.startswith('CEL: 55 '):
        fone = fone[len('CEL: 55 '):]
    return fone

df['fone'] = df['fone'].apply(remover_prefixo)
df.to_csv('data/importacao_clientes/telefones_id_fone_principal_sem_cel55.csv', index=False, encoding='utf-8')
print('Arquivo salvo sem o prefixo "CEL: 55 ".')
