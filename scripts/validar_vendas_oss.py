import pandas as pd

df = pd.read_csv('1_normalizacao/dados_processados/vendas_para_importar/vendas_oss_final.csv', 
                 sep=';', encoding='utf-8')

print('VALIDACAO FINAL')
print('='*70)

entrada_maior = df[df['valor_entrada'] > df['valor_total']]
print(f'Vendas com entrada > total: {len(entrada_maior)}')

if len(entrada_maior) == 0:
    print('OK! Todas as vendas respeitam a constraint!')
else:
    print('ERRO! Ainda ha vendas com entrada > total')
    print(entrada_maior[['numero_venda', 'valor_total', 'valor_entrada']].head())
