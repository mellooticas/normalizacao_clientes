import pandas as pd

arquivos = [
    'data/importacao_clientes/modelo_tabela/clientes_suzano_lote1.csv',
    'data/importacao_clientes/modelo_tabela/clientes_suzano_lote3.csv',
    'data/importacao_clientes/modelo_tabela/clientes_suzano_lote4.csv',
    'data/importacao_clientes/modelo_tabela/clientes_suzano_lote7.csv',
    'data/importacao_clientes/modelo_tabela/clientes_suzano2.csv',
]

# Carregar todos os dataframes
dfs = [pd.read_csv(arq, dtype=str) for arq in arquivos]
# Adicionar coluna de origem para rastrear
for df, arq in zip(dfs, arquivos):
    df['__arquivo'] = arq
# Concatenar todos
df_all = pd.concat(dfs, ignore_index=True)
# Remover duplicatas globais de id_legado, mantendo a primeira ocorrência
antes = len(df_all)
df_all = df_all.drop_duplicates(subset=['id_legado'], keep='first')
depois = len(df_all)
print(f'Removidas {antes-depois} duplicatas globais de id_legado.')
# Salvar de volta para cada arquivo apenas as linhas de sua origem
for arq in arquivos:
    df_arq = df_all[df_all['__arquivo'] == arq].drop(columns='__arquivo')
    df_arq.to_csv(arq, index=False, encoding='utf-8')
    print(f'Arquivo atualizado: {arq}')
