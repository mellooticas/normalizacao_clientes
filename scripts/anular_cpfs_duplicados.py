import pandas as pd
import sys

ARQUIVO = sys.argv[1] if len(sys.argv) > 1 else 'data/importacao_clientes/modelo_tabela/clientes_perus.csv'

def main():
    df = pd.read_csv(ARQUIVO, dtype=str)
    # Considera apenas CPFs não nulos
    mask_valid = df['cpf'].notna() & (df['cpf'] != '')
    cpfs = df.loc[mask_valid, 'cpf']
    duplicados = cpfs[cpfs.duplicated(keep='first')].unique()
    # Anula todos os CPFs duplicados, exceto o primeiro
    df['cpf'] = df['cpf'].where(~df['cpf'].isin(duplicados) | df['cpf'].duplicated(keep='first'), pd.NA)
    df.to_csv(ARQUIVO, index=False, encoding='utf-8')
    print(f'CPFs duplicados anulados em {ARQUIVO}')

if __name__ == '__main__':
    main()
