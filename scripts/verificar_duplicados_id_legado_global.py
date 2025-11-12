import pandas as pd

arquivos = [
    'data/importacao_clientes/modelo_tabela/clientes_suzano_lote1.csv',
    'data/importacao_clientes/modelo_tabela/clientes_suzano_lote3.csv',
    'data/importacao_clientes/modelo_tabela/clientes_suzano_lote4.csv',
    'data/importacao_clientes/modelo_tabela/clientes_suzano_lote7.csv',
    'data/importacao_clientes/modelo_tabela/clientes_suzano2.csv',
]

todos_ids = pd.Series(dtype=str)
mapa_arquivo = []
for arq in arquivos:
    df = pd.read_csv(arq, dtype=str)
    todos_ids = todos_ids.append(df['id_legado'], ignore_index=True)
    mapa_arquivo.extend([(arq, idl) for idl in df['id_legado']])

duplicados = todos_ids[todos_ids.duplicated(keep=False)].unique().tolist()
print('id_legado duplicados entre arquivos:', duplicados)
if duplicados:
    print('Ocorrências:')
    for arq, idl in mapa_arquivo:
        if idl in duplicados:
            print(f'{arq}: {idl}')
