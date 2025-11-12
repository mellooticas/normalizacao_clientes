import pandas as pd
import re

def normalizar_telefone(fone):
    fone = str(fone)
    fone = re.sub(r'(?i)cel: ?', '', fone)  # Remove CEL: (case insensitive)
    fone = re.sub(r'\D', '', fone)  # Remove tudo que não for dígito
    if fone.startswith('55') and len(fone) > 11:
        fone = fone[2:]
    if len(fone) == 11 or len(fone) == 10:
        return fone
    return ''

df = pd.read_csv('data/importacao_clientes/telefones_id_fone_principal.csv', dtype=str)
df['fone_normalizado'] = df['fone'].apply(normalizar_telefone)
df.to_csv('data/importacao_clientes/telefones_id_fone_principal_normalizado.csv', index=False, encoding='utf-8')
print('Arquivo salvo com coluna fone_normalizado (limpeza CEL: e 55 aplicada).')
