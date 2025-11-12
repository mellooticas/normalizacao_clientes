import pandas as pd
import re

def corrigir_fone(fone):
    fone = str(fone).strip()
    # Remove tudo que não for número
    numeros = re.sub(r'\D', '', fone)
    # Se tiver 10 ou 11 dígitos, formata para (XX) XXXXXXXX(X)
    if len(numeros) == 11:
        return f'({numeros[:2]}) {numeros[2:]}'
    if len(numeros) == 10:
        return f'({numeros[:2]}) {numeros[2:]}'
    return ''

df = pd.read_csv('data/importacao_clientes/telefones_id_fone_principal_com_ddd11.csv', dtype=str)
df['fone_corrigido'] = df['fone'].apply(corrigir_fone)
df.to_csv('data/importacao_clientes/telefones_id_fone_principal_corrigido.csv', index=False, encoding='utf-8')
print('Arquivo salvo com coluna fone_corrigido, formatado para o padrão.')
