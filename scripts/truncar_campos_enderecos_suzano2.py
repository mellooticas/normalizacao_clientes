import pandas as pd

arq = 'data/enderecos_para_importar/enderecos_suzano2.csv'
df = pd.read_csv(arq, dtype=str)
for col in ['cep', 'numero', 'estado']:
    if col in df.columns:
        df[col] = df[col].astype(str).str.slice(0, 10)
df.to_csv(arq, index=False, encoding='utf-8')
print('Campos cep, numero e estado truncados para 10 caracteres.')
