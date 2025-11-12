"""
Normalização de vendas com múltiplas formas de pagamento
Preenche OS e Cliente nas linhas que só têm forma_pgto e entrada
"""

import pandas as pd
from pathlib import Path

# Diretório base
base_dir = Path('dados_processados/originais/cxs/planilhas_originais')

# Lojas
lojas = ['maua', 'perus', 'rio_pequeno', 'sao_mateus', 'suzano', 'suzano2']

print('=' * 80)
print('NORMALIZAÇÃO DE MÚLTIPLAS FORMAS DE PAGAMENTO')
print('=' * 80)

total_geral_preenchido = 0

for loja in lojas:
    arquivo = base_dir / loja / f'vendas_{loja}_consolidado.csv'
    
    if not arquivo.exists():
        continue
    
    print(f'\n{"=" * 80}')
    print(f'LOJA: {loja.upper()}')
    print('=' * 80)
    
    # Ler arquivo
    df = pd.read_csv(arquivo, sep=';', dtype=str)
    
    print(f'\n📊 Total de registros: {len(df)}')
    
    # Identificar linhas vazias (sem nn_venda OU sem cliente)
    mask_vazio = (
        (df['nn_venda'].isna() | (df['nn_venda'].str.strip() == '')) |
        (df['cliente'].isna() | (df['cliente'].str.strip() == ''))
    )
    
    linhas_vazias = mask_vazio.sum()
    print(f'\n🔍 Linhas com OS ou Cliente vazio: {linhas_vazias}')
    
    if linhas_vazias == 0:
        print('✅ Nenhuma linha vazia encontrada!')
        continue
    
    # Mostrar exemplos
    print(f'\n📋 Exemplos de linhas vazias (primeiras 5):')
    exemplos = df[mask_vazio].head(5)
    for idx, row in exemplos.iterrows():
        print(f'   Linha {idx}:')
        print(f'      OS: "{row["nn_venda"]}" | Cliente: "{row["cliente"]}"')
        print(f'      Forma Pgto: {row["forma_de_pgto"]} | Entrada: {row["entrada"]}')
    
    # Criar cópia para comparação
    df_original = df.copy()
    
    # PREENCHER com forward fill
    print(f'\n🔄 Preenchendo com dados da venda anterior...')
    
    # Forward fill nas colunas nn_venda e cliente
    df['nn_venda'] = df['nn_venda'].replace('', pd.NA).ffill()
    df['cliente'] = df['cliente'].replace('', pd.NA).ffill()
    
    # Importante: Deixar valor_venda em BRANCO nas linhas preenchidas
    # (porque são pagamentos adicionais, não o valor total da venda)
    for idx, row in df.iterrows():
        # Se a linha foi preenchida (tinha vazio antes)
        if mask_vazio.loc[idx]:
            # Deixar valor_venda em branco
            df.loc[idx, 'valor_venda'] = ''
    
    # Verificar quantas foram preenchidas
    ainda_vazias = (
        (df['nn_venda'].isna() | (df['nn_venda'].str.strip() == '')) |
        (df['cliente'].isna() | (df['cliente'].str.strip() == ''))
    ).sum()
    
    preenchidas = linhas_vazias - ainda_vazias
    
    print(f'✅ Linhas preenchidas: {preenchidas}')
    print(f'⚠️  Ainda vazias: {ainda_vazias}')
    
    total_geral_preenchido += preenchidas
    
    # Mostrar exemplos de preenchimento
    if preenchidas > 0:
        print(f'\n📋 Exemplos de preenchimento (primeiras 3):')
        
        count = 0
        for idx in df[mask_vazio].head(5).index:
            if idx < len(df):
                antes_os = df_original.loc[idx, 'nn_venda'] if pd.notna(df_original.loc[idx, 'nn_venda']) else '(vazio)'
                depois_os = df.loc[idx, 'nn_venda']
                antes_cliente = df_original.loc[idx, 'cliente'] if pd.notna(df_original.loc[idx, 'cliente']) else '(vazio)'
                depois_cliente = df.loc[idx, 'cliente'][:30]
                
                print(f'\n   Linha {idx}:')
                print(f'      OS: {antes_os} → {depois_os}')
                print(f'      Cliente: {antes_cliente} → {depois_cliente}')
                print(f'      Forma Pgto: {df.loc[idx, "forma_de_pgto"]}')
                print(f'      Entrada: {df.loc[idx, "entrada"]}')
                print(f'      Valor Venda: (deixado em branco - pagamento adicional)')
                
                count += 1
                if count >= 3:
                    break
    
    # Salvar arquivo atualizado
    print(f'\n💾 Salvando arquivo atualizado...')
    df.to_csv(arquivo, sep=';', index=False, encoding='utf-8-sig')
    
    print(f'✅ Arquivo salvo: {arquivo.name}')
    
    # Estatísticas finais
    print(f'\n📊 RESUMO:')
    print(f'   - Registros totais: {len(df)}')
    print(f'   - Linhas preenchidas: {preenchidas}')
    print(f'   - Linhas ainda vazias: {ainda_vazias}')
    print(f'   - Vendas únicas: {df["nn_venda"].nunique()}')

print(f'\n{"=" * 80}')
print('✅ PROCESSAMENTO CONCLUÍDO!')
print('=' * 80)
print(f'\n📊 TOTAL GERAL:')
print(f'   - Linhas preenchidas em todas as lojas: {total_geral_preenchido}')
