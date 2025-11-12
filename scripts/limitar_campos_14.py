import pandas as pd
import sys

ARQUIVO = sys.argv[1] if len(sys.argv) > 1 else 'data/importacao_clientes/modelo_tabela/clientes_rio_pequeno.csv'

# Limite máximo para campos character varying(14)
MAXLEN = 14
CAMPOS = ['cpf', 'rg']

def main():
    df = pd.read_csv(ARQUIVO, dtype=str)
    for campo in CAMPOS:
        if campo in df.columns:
            df[campo] = df[campo].apply(lambda x: x[:MAXLEN] if isinstance(x, str) and len(x) > MAXLEN else x)
    df.to_csv(ARQUIVO, index=False, encoding='utf-8')
    print(f'Campos cortados para 14 caracteres em {ARQUIVO}')

if __name__ == '__main__':
    main()
