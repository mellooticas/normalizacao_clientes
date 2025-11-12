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
        for i in inter:
            encontrados.append({'id_legado': i, 'arquivo_duplicado': f})

# Gerar CSV detalhado
df_encontrados = pd.DataFrame(encontrados)
df_encontrados.to_csv('data/importacao_clientes/modelo_tabela/id_legado_duplicados_suzano2.csv', index=False, encoding='utf-8')
print('Relatório gerado: data/importacao_clientes/modelo_tabela/id_legado_duplicados_suzano2.csv')
