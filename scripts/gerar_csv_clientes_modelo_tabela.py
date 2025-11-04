import pandas as pd
import os

# Configurações
PASTA_ORIGEM = 'data/importacao_clientes'
PASTA_DESTINO = 'data/importacao_clientes/modelo_tabela'
LOJAS = [
    'clientes_maua.csv',
    'clientes_perus.csv',
    'clientes_rio_pequeno.csv',
    'clientes_sao_mateus.csv',
    'clientes_suzano.csv',
    'clientes_suzano2.csv',
]
CAMPOS_TABELA = [
    'id_legado',
    'nome',
    'cpf',
    'rg',
    'data_nascimento',
    'sexo',
    'email',
]
# Limite de registros por arquivo para facilitar importação
LIMITE = 1000

# Mapeamento de colunas por loja
MAPEAMENTO = {
    'clientes_maua.csv': {
        'id_legado': 'ID',
        'nome': 'Nome Completo',
        'cpf': None,
        'rg': None,
        'data_nascimento': None,
        'sexo': 'Sexo',
        'email': 'E-mail',
    },
    'clientes_suzano.csv': {
        'id_legado': 'ID',
        'nome': 'Nome Completo',
        'cpf': None,
        'rg': None,
        'data_nascimento': None,
        'sexo': 'Sexo',
        'email': 'E-mail',
    },
    'clientes_perus.csv': {
        'id_legado': 'cliente_id',
        'nome': 'NOME:',
        'cpf': 'CPF',
        'rg': 'RG',
        'data_nascimento': 'data_nascimento',
        'sexo': None,
        'email': 'EMAIL:',
    },
    'clientes_rio_pequeno.csv': {
        'id_legado': 'cliente_id',
        'nome': 'NOME:',
        'cpf': 'CPF',
        'rg': 'RG',
        'data_nascimento': 'data_nascimento',
        'sexo': None,
        'email': 'EMAIL:',
    },
    'clientes_sao_mateus.csv': {
        'id_legado': 'cliente_id',
        'nome': 'NOME:',
        'cpf': 'CPF',
        'rg': 'RG',
        'data_nascimento': 'data_nascimento',
        'sexo': None,
        'email': 'EMAIL:',
    },
    'clientes_suzano2.csv': {
        'id_legado': 'cliente_id',
        'nome': 'NOME:',
        'cpf': 'CPF',
        'rg': 'RG',
        'data_nascimento': 'data_nascimento',
        'sexo': None,
        'email': 'EMAIL:',
    },
}

os.makedirs(PASTA_DESTINO, exist_ok=True)

def processar_arquivo(nome_arquivo):
    print(f'Processando {nome_arquivo}...')
    arq_origem = os.path.join(PASTA_ORIGEM, nome_arquivo)
    arq_base = os.path.splitext(nome_arquivo)[0]
    df = pd.read_csv(arq_origem)
    mapeamento = MAPEAMENTO[nome_arquivo]
    df_saida = pd.DataFrame()
    for campo in CAMPOS_TABELA:
        col = mapeamento.get(campo)
        if col and col in df.columns:
            df_saida[campo] = df[col]
        else:
            df_saida[campo] = None
    # Limpar espaços e normalizar nomes
    df_saida['nome'] = df_saida['nome'].astype(str).str.strip()
    # Dividir em lotes se necessário
    total = len(df_saida)
    if total > LIMITE:
        for i, ini in enumerate(range(0, total, LIMITE)):
            fim = min(ini+LIMITE, total)
            arq_dest = os.path.join(PASTA_DESTINO, f'{arq_base}_lote{i+1}.csv')
            df_saida.iloc[ini:fim].to_csv(arq_dest, index=False)
            print(f'  → {arq_dest} ({fim-ini} registros)')
    else:
        arq_dest = os.path.join(PASTA_DESTINO, f'{arq_base}.csv')
        df_saida.to_csv(arq_dest, index=False)
        print(f'  → {arq_dest} ({total} registros)')

for loja in LOJAS:
    processar_arquivo(loja)
print('Finalizado!')
