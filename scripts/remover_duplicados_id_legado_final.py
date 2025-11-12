import pandas as pd
import sys

ARQUIVO = sys.argv[1] if len(sys.argv) > 1 else 'data/importacao_clientes/modelo_tabela/clientes_perus.csv'

def main():
    df = pd.read_csv(ARQUIVO, dtype=str)
    antes = len(df)
    df = df.drop_duplicates(subset=['id_legado'], keep='first')
    depois = len(df)
    df.to_csv(ARQUIVO, index=False, encoding='utf-8')
    print(f'Removidas {antes-depois} duplicatas de id_legado em {ARQUIVO}')

if __name__ == '__main__':
    main()
