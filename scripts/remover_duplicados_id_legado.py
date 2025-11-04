import pandas as pd
import os

PASTA = 'data/importacao_clientes/modelo_tabela'
ARQUIVO = 'clientes_perus.csv'
CAMPO = 'id_legado'

path = os.path.join(PASTA, ARQUIVO)
df = pd.read_csv(path)

duplicados = df[CAMPO].duplicated(keep=False)
if duplicados.any():
    print(f'Encontrados {duplicados.sum()} registros duplicados em {CAMPO}. Mantendo apenas o primeiro de cada um.')
    df = df.drop_duplicates(subset=[CAMPO], keep='first')
    df.to_csv(path, index=False)
    print('Arquivo corrigido!')
else:
    print('Nenhum duplicado encontrado.')
