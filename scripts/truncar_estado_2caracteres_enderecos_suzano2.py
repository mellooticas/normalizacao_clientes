import pandas as pd

arq = 'data/enderecos_para_importar/enderecos_suzano2.csv'
df = pd.read_csv(arq, dtype=str)
if 'estado' in df.columns:
    df['estado'] = df['estado'].astype(str).str.slice(0, 2)
df.to_csv(arq, index=False, encoding='utf-8')
print('Campo estado truncado para 2 caracteres.')
