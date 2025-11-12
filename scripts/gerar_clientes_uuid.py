import pandas as pd
import glob
import os

uuid_map = pd.read_csv('data/importacao_clientes/modelo_tabela/clientes_uuid_banco_completo.csv', dtype=str)[['id','id_legado']].rename(columns={'id':'cliente_id'})
arquivos = glob.glob('data/originais/clientes/clientes_*.csv')
out_dir = 'data/clientes_uuid/'
os.makedirs(out_dir, exist_ok=True)

for arq in arquivos:
    df = pd.read_csv(arq, dtype=str)
    id_legado_col = df.columns[0]
    df = df.merge(uuid_map, left_on=id_legado_col, right_on='id_legado', how='left')
    df.to_csv(out_dir + os.path.basename(arq), index=False, encoding='utf-8')
    print(f'Arquivo gerado: {out_dir + os.path.basename(arq)}')
