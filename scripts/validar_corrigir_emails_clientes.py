import pandas as pd
import os
import re

PASTA = 'data/importacao_clientes/modelo_tabela'
REGEX_EMAIL = re.compile(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')

arquivos = [f for f in os.listdir(PASTA) if f.endswith('.csv')]

for arq in arquivos:
    path = os.path.join(PASTA, arq)
    df = pd.read_csv(path)
    if 'email' in df.columns:
        emails_orig = df['email'].copy()
        # Corrigir espaços, letras maiúsculas, etc.
        df['email'] = df['email'].astype(str).str.strip().str.lower()
        # Tornar vazio se não for válido
        df['email'] = df['email'].apply(lambda x: x if REGEX_EMAIL.match(x) else None)
        # Relatório
        invalidos = emails_orig[~emails_orig.fillna('').str.strip().str.lower().apply(lambda x: bool(REGEX_EMAIL.match(x)) if x else True)]
        if not invalidos.empty:
            print(f'Arquivo: {arq} - {len(invalidos)} e-mails inválidos corrigidos para null')
    df.to_csv(path, index=False)
print('Validação e correção de e-mails finalizada!')
