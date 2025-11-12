import pandas as pd
import re

def normalizar_fone(fone):
    fone = str(fone).strip()
    # Remove tudo que não for número
    numeros = re.sub(r'\D', '', fone)
    # Se já tem DDD 11, mantém, senão adiciona
    if len(numeros) == 9:  # Ex: 912345678
        numeros = '11' + numeros
    if len(numeros) == 8:  # Ex: 23456789
        numeros = '11' + '9' + numeros
    # Formatar para (11) 9XXXXXXX ou (11) XXXXXXXX
    if len(numeros) == 11:
        return f'(11) {numeros[2:]}'
    if len(numeros) == 10:
        return f'(11) {numeros[2:]}'
    return ''

df = pd.read_csv('data/importacao_clientes/telefones_id_fone_principal_com_ddd11.csv', dtype=str)
df['fone_normalizado'] = df['fone'].apply(normalizar_fone)
df.to_csv('data/importacao_clientes/telefones_id_fone_principal_normalizado_final.csv', index=False, encoding='utf-8')
print('Arquivo normalizado salvo com sucesso!')
