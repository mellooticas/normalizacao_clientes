import pandas as pd
from datetime import datetime
import sys

ARQUIVO = sys.argv[1] if len(sys.argv) > 1 else 'data/importacao_clientes/modelo_tabela/clientes_perus.csv'

# Limites razoáveis para data de nascimento
MIN_DATE = datetime(1900, 1, 1)
MAX_DATE = datetime.now()


def is_valid_date(date_str):
    if pd.isna(date_str) or not isinstance(date_str, str) or not date_str.strip():
        return False
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        if dt < MIN_DATE or dt > MAX_DATE:
            return False
        return True
    except Exception:
        return False

def main():
    df = pd.read_csv(ARQUIVO, dtype=str)
    df['data_nascimento'] = df['data_nascimento'].apply(lambda x: x if is_valid_date(x) else '')
    df.to_csv(ARQUIVO, index=False, encoding='utf-8')
    print(f'Datas de nascimento normalizadas em {ARQUIVO}')

if __name__ == '__main__':
    main()
