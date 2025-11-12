import pandas as pd
import re

arq = 'data/originais/clientes/clientes_suzano2_normalizado.csv'

def cpf_valido(cpf):
    cpf = re.sub(r'\D', '', str(cpf))
    return len(cpf) == 11 and cpf.isdigit()

df = pd.read_csv(arq, dtype=str)
df['cpf'] = df['cpf'].apply(lambda x: x if cpf_valido(x) else '')
df.to_csv(arq, index=False, encoding='utf-8')
print('CPFs inválidos normalizados para vazio.')
