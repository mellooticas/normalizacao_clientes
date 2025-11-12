import pandas as pd
import os

PASTA = 'data/importacao_clientes/modelo_tabela'
ARQUIVOS = [f for f in os.listdir(PASTA) if f.endswith('.csv')]
CAMPO = 'cpf'

for arq in ARQUIVOS:
    path = os.path.join(PASTA, arq)
    df = pd.read_csv(path)
    if CAMPO in df.columns:
        # Identifica duplicados (exceto null)
        mask_duplicado = df[CAMPO].notnull() & df[CAMPO].duplicated(keep='first')
        n_duplicados = mask_duplicado.sum()
        if n_duplicados > 0:
            print(f'{arq}: {n_duplicados} CPFs duplicados removidos (mantendo cliente, CPF fica null)')
            df.loc[mask_duplicado, CAMPO] = None
            df.to_csv(path, index=False)
        else:
            print(f'{arq}: nenhum CPF duplicado encontrado.')
print('Remoção de CPFs duplicados concluída!')
