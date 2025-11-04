import pandas as pd
import re

ARQUIVO = 'data/importacao_clientes/modelo_tabela/clientes_perus.csv'

def is_valid_cpf(cpf):
    if pd.isna(cpf):
        return False
    return bool(re.fullmatch(r'^[0-9]{11}$', str(cpf)))

def main():
    df = pd.read_csv(ARQUIVO, dtype=str)
    df['cpf'] = df['cpf'].apply(lambda x: x if is_valid_cpf(x) else '')
    df.to_csv(ARQUIVO, index=False, encoding='utf-8')
    print('CPFs inválidos anulados com sucesso.')

if __name__ == '__main__':
    main()
