import pandas as pd
import glob

arq_suzano2 = 'data/importacao_clientes/modelo_tabela/clientes_suzano2.csv'
df2 = pd.read_csv(arq_suzano2, dtype=str)
ids2 = set(df2['id_legado'].dropna().astype(str))

arquivos = [f for f in glob.glob('data/importacao_clientes/modelo_tabela/clientes_*.csv') if f != arq_suzano2]
encontrados = []
for f in arquivos:
    df = pd.read_csv(f, dtype=str)
    ids = set(df['id_legado'].dropna().astype(str))
    inter = ids2 & ids
    if inter:
        encontrados.extend([(f, i) for i in inter])

print('id_legado de suzano2.csv encontrados em outros arquivos:')
for f, i in encontrados:
    print(f'{i} em {f}')
