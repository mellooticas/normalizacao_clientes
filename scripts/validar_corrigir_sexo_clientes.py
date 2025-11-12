import pandas as pd
import os

PASTA = 'data/importacao_clientes/modelo_tabela'
VALORES_VALIDOS = {'M', 'F', 'O'}

arquivos = [f for f in os.listdir(PASTA) if f.endswith('.csv')]

for arq in arquivos:
    path = os.path.join(PASTA, arq)
    df = pd.read_csv(path)
    if 'sexo' in df.columns:
        orig = df['sexo'].copy()
        # Normalizar e filtrar
        df['sexo'] = df['sexo'].astype(str).str.strip().str.upper()
        df['sexo'] = df['sexo'].apply(lambda x: x if x in VALORES_VALIDOS else None)
        invalidos = orig[~orig.fillna('').str.strip().str.upper().isin(VALORES_VALIDOS)]
        if not invalidos.empty:
            print(f'Arquivo: {arq} - {len(invalidos)} valores de sexo inválidos corrigidos para null')
    df.to_csv(path, index=False)
print('Validação e correção de sexo finalizada!')
