import pandas as pd
import glob

arquivos = glob.glob('data/originais/clientes/clientes_*.csv')
registros = []

for arq in arquivos:
    df = pd.read_csv(arq, dtype=str)
    id_col = df.columns[0]
    fone_col = None
    for c in ['FONE', 'fone', 'Fone', 'TELEFONE', 'telefone', 'CELULAR', 'celular']:
        if c in df.columns:
            fone_col = c
            break
    if fone_col:
        for i, row in df.iterrows():
            fone = str(row[fone_col]).strip()
            if fone:
                registros.append({'id': row[id_col], 'fone': fone})

pd.DataFrame(registros).to_csv('data/importacao_clientes/telefones_id_fone.csv', index=False, encoding='utf-8')
print(f'Arquivo gerado com {len(registros)} telefones.')
