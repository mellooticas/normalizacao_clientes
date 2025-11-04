#!/usr/bin/env python3
"""
Análise da coluna ID.1 do arquivo ordem_servico_pdv_outros_pagamentos.csv
Extração de códigos únicos das formas de pagamento para mapeamento de UUIDs
"""

import pandas as pd
from collections import Counter

def analisar_codigos_id1_outros_pagamentos():
    arquivo = 'data/originais/controles_gerais/trans_financ/separados_por_pagamento/ordem_servico_pdv_outros_pagamentos.csv'
    
    print("=== ANÁLISE COLUNA ID.1 - OUTROS PAGAMENTOS ===\n")
    
    # Carregar dados
    print("📁 Carregando arquivo...")
    df = pd.read_csv(arquivo, encoding='utf-8-sig')
    print(f"✅ {len(df):,} registros carregados")
    print()
    
    # Analisar coluna ID.1
    print("🔍 ANÁLISE DA COLUNA ID.1:")
    
    # Valores únicos na coluna ID.1
    codigos_id1 = df['ID.1'].dropna().unique()
    print(f"Total de códigos únicos: {len(codigos_id1)}")
    print()
    
    # Contagem por código
    contagem_codigos = df['ID.1'].value_counts()
    print("📊 DISTRIBUIÇÃO DOS CÓDIGOS:")
    for codigo, qtd in contagem_codigos.items():
        if pd.notna(codigo):
            percentual = (qtd / len(df)) * 100
            print(f"  '{codigo}' -> {qtd:,} registros ({percentual:.1f}%)")
    print()
    
    # Cruzamento ID.1 x Pagamento
    print("🔗 CRUZAMENTO ID.1 x TIPO DE PAGAMENTO:")
    cruzamento = df.groupby(['ID.1', 'Pagamento']).size().reset_index(name='quantidade')
    cruzamento = cruzamento.sort_values(['ID.1', 'quantidade'], ascending=[True, False])
    
    for codigo in codigos_id1:
        if pd.notna(codigo):
            print(f"\n  📋 Código '{codigo}':")
            subset = cruzamento[cruzamento['ID.1'] == codigo]
            for _, row in subset.iterrows():
                print(f"    {row['Pagamento']:30} -> {row['quantidade']:,}")
    
    # Criar arquivo para mapeamento de UUIDs
    print("\n📝 CRIANDO ARQUIVO PARA MAPEAMENTO DE UUIDs...")
    
    # Preparar dados para o arquivo de mapeamento
    mapeamento_data = []
    
    for codigo in sorted(codigos_id1):
        if pd.notna(codigo):
            # Pegar os tipos de pagamento mais comuns para este código
            subset = df[df['ID.1'] == codigo]
            tipos_pagamento = subset['Pagamento'].value_counts()
            principal_tipo = tipos_pagamento.index[0] if len(tipos_pagamento) > 0 else "N/A"
            total_registros = len(subset)
            
            mapeamento_data.append({
                'codigo_id1': codigo,
                'principal_tipo_pagamento': principal_tipo,
                'total_registros': total_registros,
                'uuid_forma_pagamento': '',  # Para preenchimento manual
                'observacoes': ''  # Para observações
            })
    
    # Criar DataFrame para o mapeamento
    df_mapeamento = pd.DataFrame(mapeamento_data)
    
    # Salvar arquivo para mapeamento
    arquivo_mapeamento = 'data/originais/controles_gerais/trans_financ/separados_por_pagamento/mapeamento_codigos_id1_para_uuid.csv'
    df_mapeamento.to_csv(arquivo_mapeamento, index=False, encoding='utf-8-sig')
    
    print(f"✅ Arquivo criado: {arquivo_mapeamento}")
    print()
    
    # Criar também versão para análise visual
    print("📋 RESUMO PARA MAPEAMENTO:")
    print("Código | Tipo Principal | Registros")
    print("-" * 50)
    for _, row in df_mapeamento.iterrows():
        print(f"{row['codigo_id1']:6} | {row['principal_tipo_pagamento']:25} | {row['total_registros']:,}")
    
    # Salvar resumo detalhado
    resumo = f"""
=== CÓDIGOS ID.1 - OUTROS PAGAMENTOS ===

📊 RESUMO:
• Total de registros: {len(df):,}
• Códigos únicos encontrados: {len(codigos_id1)}

📋 CÓDIGOS PARA MAPEAMENTO UUID:
"""
    
    for _, row in df_mapeamento.iterrows():
        resumo += f"\n• {row['codigo_id1']} -> {row['principal_tipo_pagamento']} ({row['total_registros']:,} registros)"
    
    resumo += f"""

📁 ARQUIVOS GERADOS:
• {arquivo_mapeamento}

📝 PRÓXIMO PASSO:
Preencha a coluna 'uuid_forma_pagamento' no arquivo CSV com os UUIDs correspondentes.
"""
    
    arquivo_resumo = 'data/originais/controles_gerais/trans_financ/separados_por_pagamento/CODIGOS_ID1_PARA_MAPEAMENTO.txt'
    with open(arquivo_resumo, 'w', encoding='utf-8') as f:
        f.write(resumo)
    
    print(f"\n📄 Resumo salvo: {arquivo_resumo}")
    print()
    print("🎯 PRÓXIMOS PASSOS:")
    print("1. Abra o arquivo: mapeamento_codigos_id1_para_uuid.csv")
    print("2. Preencha a coluna 'uuid_forma_pagamento' com os UUIDs")
    print("3. Informe quando estiver pronto para aplicar os UUIDs")
    
    return df_mapeamento

if __name__ == "__main__":
    df_mapeamento = analisar_codigos_id1_outros_pagamentos()