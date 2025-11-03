


import pandas as pd
import glob
import os

# Caminhos
uuid_map = pd.read_csv('data/importacao_clientes/modelo_tabela/clientes_uuid_banco_completo.csv', dtype=str)[['id','id_legado']].rename(columns={'id':'cliente_id'})

dir_in = 'data/originais/clientes/'
dir_out = 'data/telefones_para_importar/'
os.makedirs(dir_out, exist_ok=True)

arquivos = glob.glob(dir_in + 'clientes_*.csv')
registros = []

for arq in arquivos:
    df = pd.read_csv(arq, dtype=str)
    registros = []
    col_tel = None
    for c in ['FONE', 'CELULAR', 'TELEFONE', 'telefone', 'celular']:
        if c in df.columns:
            col_tel = c
            break
    if col_tel:
        for i, row in df.iterrows():
            tels = str(row[col_tel]).split(';')
            for tel in tels:
                tel = tel.strip()
                if tel and row.get('cliente_id'):
                    id_legado = row[df.columns[0]]
                    uuid = uuid_map.loc[uuid_map['id_legado']==id_legado, 'cliente_id'].values
                    if len(uuid):
                        registros.append({
                            'cliente_id': uuid[0],
                            'tipo': 'CELULAR',
                            'numero': tel,
                            'whatsapp': '',
                            'principal': '',
                            'observacao': ''
                        })
    if registros:
        nome_saida = os.path.basename(arq).replace('clientes_', 'telefones_')
        pd.DataFrame(registros).to_csv(dir_out + nome_saida, index=False, encoding='utf-8')
        print(f'Arquivo gerado: {dir_out + nome_saida}')
    else:
        print(f'Nenhum telefone encontrado em {arq}')
