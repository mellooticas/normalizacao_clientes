import pandas as pd
import re

ARQUIVO = 'data/importacao_clientes/modelo_tabela/clientes_perus.csv'

def is_valid_cpf(cpf):
    if pd.isna(cpf):
        return False
    cpf = re.sub(r'[^0-9]', '', str(cpf))
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    # Validação dos dígitos verificadores
    for i in [9, 10]:
        soma = sum(int(cpf[num]) * ((i+1) - num) for num in range(0, i))
        digito = ((soma * 10) % 11) % 10
        if digito != int(cpf[i]):
            return False
    return True

def main():
    df = pd.read_csv(ARQUIVO, dtype=str)
    df['cpf'] = df['cpf'].apply(lambda x: x if is_valid_cpf(x) else '')
    df.to_csv(ARQUIVO, index=False, encoding='utf-8')
    print('CPFs inválidos (inclusive pelo algoritmo) anulados com sucesso.')

if __name__ == '__main__':
    main()
