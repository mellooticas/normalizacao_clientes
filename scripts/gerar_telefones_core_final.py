import pandas as pd

# Carregar arquivo de telefones normalizados
telefones_df = pd.read_csv('data/importacao_clientes/telefones_id_fone_principal_com_ddd11.csv', dtype=str)

# Carregar mapeamento UUID (id_legado -> cliente_id)
uuid_map = pd.read_csv('data/importacao_clientes/modelo_tabela/clientes_uuid_banco_completo.csv', dtype=str)[['id','id_legado']].rename(columns={'id':'cliente_id'})

# Cruzar telefones com UUID usando id (telefones) = id_legado (clientes)
telefones_final = pd.merge(telefones_df, uuid_map, left_on='id', right_on='id_legado', how='inner')

# Montar DataFrame no formato da tabela core.telefones
telefones_banco = pd.DataFrame({
    'cliente_id': telefones_final['cliente_id'],
    'tipo': 'CELULAR',
    'numero': telefones_final['fone'],
    'whatsapp': False,
    'principal': False,
    'observacao': ''
})

# Remover registros sem cliente_id válido
telefones_banco = telefones_banco[telefones_banco['cliente_id'].notna()]

# Salvar arquivo final pronto para importação
telefones_banco.to_csv('data/telefones_para_importar/telefones_core_final.csv', index=False, encoding='utf-8')

print(f'Arquivo final gerado: telefones_core_final.csv')
print(f'Total de telefones: {len(telefones_banco)}')
print(f'Telefones com cliente_id válido: {telefones_banco["cliente_id"].notna().sum()}')