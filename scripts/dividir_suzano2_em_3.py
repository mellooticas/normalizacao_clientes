import pandas as pd
import math

arq = 'data/importacao_clientes/modelo_tabela/clientes_suzano2.csv'
df = pd.read_csv(arq, dtype=str)
n = math.ceil(len(df)/3)
for i in range(3):
    df.iloc[i*n:(i+1)*n].to_csv(f'data/importacao_clientes/modelo_tabela/clientes_suzano2_parte{i+1}.csv', index=False, encoding='utf-8')
print('Arquivo dividido em 3 partes.')
