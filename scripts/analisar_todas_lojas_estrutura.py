"""
Análise completa da estrutura de TODAS as lojas
Para criar estratégia de unificação
"""

import pandas as pd
from pathlib import Path
from collections import defaultdict

# Diretório base
base_dir = Path('dados_processados/originais/cxs/planilhas_originais')

# Lojas
lojas = ['maua', 'perus', 'rio_pequeno', 'sao_mateus', 'suzano', 'suzano2']

print('=' * 80)
print('ANÁLISE COMPLETA - ESTRUTURA DAS PLANILHAS ORIGINAIS')
print('=' * 80)

for loja in lojas:
    loja_dir = base_dir / loja
    
    if not loja_dir.exists():
        continue
    
    print(f'\n{"=" * 80}')
    print(f'LOJA: {loja.upper()}')
    print('=' * 80)
    
    # Listar arquivos
    arquivos = sorted(loja_dir.glob('*.xlsx'))
    print(f'\n📁 Total de arquivos: {len(arquivos)}')
    
    # Mostrar primeiros e últimos 3
    print(f'\n📋 Arquivos:')
    for arq in arquivos[:3]:
        print(f'   - {arq.name}')
    if len(arquivos) > 6:
        print(f'   ... ({len(arquivos) - 6} arquivos intermediários)')
    for arq in arquivos[-3:]:
        print(f'   - {arq.name}')
    
    # Analisar PRIMEIRO arquivo como exemplo
    arquivo_exemplo = arquivos[0]
    print(f'\n🔍 Analisando: {arquivo_exemplo.name}')
    
    try:
        excel_file = pd.ExcelFile(arquivo_exemplo)
        
        print(f'\n📋 Abas ({len(excel_file.sheet_names)}):')
        print(f'   Primeira: {excel_file.sheet_names[0]}')
        print(f'   Última: {excel_file.sheet_names[-1]}')
        
        # Verificar se tem aba 'base'
        if 'base' in excel_file.sheet_names:
            df_base = pd.read_excel(arquivo_exemplo, sheet_name='base')
            print(f'\n   ✅ Aba BASE encontrada: {len(df_base)} registros')
            print(f'      Colunas: {list(df_base.columns)}')
        else:
            print(f'\n   ❌ Aba BASE não encontrada')
        
        # Verificar abas numéricas (dias)
        abas_numericas = [aba for aba in excel_file.sheet_names if aba.isdigit()]
        print(f'\n   📅 Abas de dias: {len(abas_numericas)} ({min(abas_numericas) if abas_numericas else "N/A"} a {max(abas_numericas) if abas_numericas else "N/A"})')
        
        # Analisar uma aba de dia
        if abas_numericas:
            aba_dia = abas_numericas[0]
            df_dia = pd.read_excel(arquivo_exemplo, sheet_name=aba_dia, nrows=20)
            
            print(f'\n   🔍 Exemplo aba "{aba_dia}":')
            print(f'      - Primeiras 20 linhas carregadas')
            print(f'      - Colunas: {len(df_dia.columns)}')
            
            # Procurar linha de cabeçalho com dados de vendas
            for idx, row in df_dia.iterrows():
                row_str = ' '.join(str(val) for val in row if pd.notna(val))
                if 'Nº Venda' in row_str or 'OS' in row_str or 'Cliente' in row_str:
                    print(f'      - Cabeçalho encontrado na linha {idx}')
                    print(f'      - Valores: {[str(v)[:20] for v in row if pd.notna(v)][:5]}')
                    break
    
    except Exception as e:
        print(f'   ❌ Erro ao analisar: {str(e)[:100]}')

print(f'\n{"=" * 80}')
print('RESUMO GERAL')
print('=' * 80)

# Contar total de arquivos por loja
for loja in lojas:
    loja_dir = base_dir / loja
    if loja_dir.exists():
        total = len(list(loja_dir.glob('*.xlsx')))
        print(f'   {loja.upper():15} - {total:2} arquivos')
