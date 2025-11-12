import pandas as pd

df = pd.read_csv('data/importacao_clientes/telefones_id_fone_principal_sem_cel55.csv', dtype=str)

def incluir_ddd(fone):
    fone = str(fone)
    if not fone.startswith('(11) '):
        return '(11) ' + fone
    return fone

df['fone'] = df['fone'].apply(incluir_ddd)
df.to_csv('data/importacao_clientes/telefones_id_fone_principal_com_ddd11.csv', index=False, encoding='utf-8')
print('Arquivo salvo com DDD (11) incluído onde necessário.')
