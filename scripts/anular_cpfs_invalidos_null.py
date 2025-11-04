import pandas as pd
import re
import sys

ARQUIVO = sys.argv[1] if len(sys.argv) > 1 else 'data/importacao_clientes/modelo_tabela/clientes_perus.csv'

def is_valid_cpf(cpf):
    if pd.isna(cpf):
        return False
    cpf = re.sub(r'[^0-9]', '', str(cpf).strip())
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    for i in [9, 10]:
        soma = sum(int(cpf[num]) * ((i+1) - num) for num in range(0, i))
        digito = ((soma * 10) % 11) % 10
        if digito != int(cpf[i]):
            return False
    return True

def main():
    df = pd.read_csv(ARQUIVO, dtype=str)
    df['cpf'] = df['cpf'].apply(lambda x: re.sub(r'[^0-9]', '', str(x).strip()) if is_valid_cpf(x) else pd.NA)
    df.to_csv(ARQUIVO, index=False, encoding='utf-8')
    print(f'CPFs inválidos anulados (NULL real) e limpos em {ARQUIVO}')

if __name__ == '__main__':
    main()
