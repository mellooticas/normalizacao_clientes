import pandas as pd
import glob
import os

# Caminhos

base_dir = 'data/originais/clientes/'
saida_dir = 'data/enderecos_para_importar/'
# Novo caminho do arquivo de UUID atualizado
map_uuid = 'data/importacao_clientes/modelo_tabela/clientes_uuid_banco_completo.csv'

# Carregar mapeamento uuid
uuid_df = pd.read_csv(map_uuid, dtype=str)[['id', 'id_legado']].rename(columns={'id': 'cliente_id'})

# Arquivos de clientes das lojas
arquivos = [f for f in glob.glob(base_dir + 'clientes_*.csv') if 'uuid' not in f]

# Mapeamento de colunas de endereço
col_map = {
    'cep': ['CEP', 'cep'],
    'logradouro': ['END:', 'END', 'logradouro'],
    'numero': ['Nº', 'numero', 'NUMERO'],
    'complemento': ['COMP', 'complemento'],
    'bairro': ['BAIRRO:', 'bairro'],
    'cidade': ['cidade', 'CIDADE', 'loja_nome'],
    'estado': ['estado', 'ESTADO'],
}

for arq in arquivos:
    df = pd.read_csv(arq, dtype=str)
    # Tenta mapear as colunas de endereço
    endereco = {}
    for padrao, nomes in col_map.items():
        for nome in nomes:
            if nome in df.columns:
                endereco[padrao] = df[nome]
                break
        else:
            endereco[padrao] = ''
    # Monta DataFrame de endereço
    end_df = pd.DataFrame({
        'id_legado': df[df.columns[0]],
        'cep': endereco['cep'],
        'logradouro': endereco['logradouro'],
        'numero': endereco['numero'],
        'complemento': endereco['complemento'],
        'bairro': endereco['bairro'],
        'cidade': endereco['cidade'],
        'estado': endereco['estado'],
        'pais': 'Brasil',
        'tipo': 'RESIDENCIAL',
        'principal': False
    })
    # Cruzar com uuid
    merged = pd.merge(end_df, uuid_df, on='id_legado', how='left')
    # Reorganizar colunas
    merged = merged[['cliente_id','tipo','cep','logradouro','numero','complemento','bairro','cidade','estado','pais','principal']]
    # Salvar
    nome_saida = os.path.basename(arq).replace('clientes_', 'enderecos_')
    merged.to_csv(os.path.join(saida_dir, nome_saida), index=False, encoding='utf-8')
    print(f'Arquivo gerado: {nome_saida} ({merged["cliente_id"].isna().sum()} sem uuid)')
