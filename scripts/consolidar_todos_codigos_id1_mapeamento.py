#!/usr/bin/env python3
"""
Consolidação de TODOS os códigos ID.1 para mapeamento de UUIDs
CARNE LANCASTER + OUTROS PAGAMENTOS
"""

import pandas as pd

def consolidar_todos_codigos_id1():
    print("=== CONSOLIDAÇÃO COMPLETA CÓDIGOS ID.1 ===\n")
    
    # Dados do CARNE LANCASTER
    carne_codes = [
        {'codigo_id1': 'CL', 'principal_tipo_pagamento': 'CARNE LANCASTER', 'total_registros': 6353, 'categoria': 'CARNE_LANCASTER'},
        {'codigo_id1': 'CL          ', 'principal_tipo_pagamento': 'CARNE LANCASTER (com espaços)', 'total_registros': 482, 'categoria': 'CARNE_LANCASTER'}
    ]
    
    # Dados dos OUTROS PAGAMENTOS (extraídos da análise anterior)
    outros_codes = [
        {'codigo_id1': '1', 'principal_tipo_pagamento': 'RECEB. PENDENTE', 'total_registros': 720, 'categoria': 'OUTROS'},
        {'codigo_id1': '1           ', 'principal_tipo_pagamento': 'RECEB. PENDENTE (com espaços)', 'total_registros': 83, 'categoria': 'OUTROS'},
        {'codigo_id1': 'AM', 'principal_tipo_pagamento': 'AMEX CREDITO', 'total_registros': 12, 'categoria': 'OUTROS'},
        {'codigo_id1': 'BO', 'principal_tipo_pagamento': 'BOLETO BANCARIO', 'total_registros': 153, 'categoria': 'OUTROS'},
        {'codigo_id1': 'CA', 'principal_tipo_pagamento': 'CORTESIA', 'total_registros': 1, 'categoria': 'OUTROS'},
        {'codigo_id1': 'CM', 'principal_tipo_pagamento': 'CREDITO MASTER', 'total_registros': 2190, 'categoria': 'OUTROS'},
        {'codigo_id1': 'CM          ', 'principal_tipo_pagamento': 'CREDITO MASTER (com espaços)', 'total_registros': 169, 'categoria': 'OUTROS'},
        {'codigo_id1': 'CN', 'principal_tipo_pagamento': 'CONVENIO', 'total_registros': 18, 'categoria': 'OUTROS'},
        {'codigo_id1': 'CS', 'principal_tipo_pagamento': 'MAIS CREDSYSTEM', 'total_registros': 2, 'categoria': 'OUTROS'},
        {'codigo_id1': 'CV', 'principal_tipo_pagamento': 'CREDITO VISA', 'total_registros': 1476, 'categoria': 'OUTROS'},
        {'codigo_id1': 'CV          ', 'principal_tipo_pagamento': 'CREDITO VISA (com espaços)', 'total_registros': 182, 'categoria': 'OUTROS'},
        {'codigo_id1': 'CZ', 'principal_tipo_pagamento': 'CREDZ', 'total_registros': 84, 'categoria': 'OUTROS'},
        {'codigo_id1': 'CZ          ', 'principal_tipo_pagamento': 'CREDZ (com espaços)', 'total_registros': 19, 'categoria': 'OUTROS'},
        {'codigo_id1': 'DI', 'principal_tipo_pagamento': 'DINHEIRO', 'total_registros': 3525, 'categoria': 'OUTROS'},
        {'codigo_id1': 'DI          ', 'principal_tipo_pagamento': 'DINHEIRO (com espaços)', 'total_registros': 243, 'categoria': 'OUTROS'},
        {'codigo_id1': 'DM', 'principal_tipo_pagamento': 'DEBITO MASTER', 'total_registros': 1238, 'categoria': 'OUTROS'},
        {'codigo_id1': 'DM          ', 'principal_tipo_pagamento': 'DEBITO MASTER (com espaços)', 'total_registros': 102, 'categoria': 'OUTROS'},
        {'codigo_id1': 'DP', 'principal_tipo_pagamento': 'DEP. EM CONTA', 'total_registros': 1386, 'categoria': 'OUTROS'},
        {'codigo_id1': 'DP          ', 'principal_tipo_pagamento': 'DEP. EM CONTA (com espaços)', 'total_registros': 160, 'categoria': 'OUTROS'},
        {'codigo_id1': 'DS', 'principal_tipo_pagamento': 'DESC FUNCIONARI', 'total_registros': 43, 'categoria': 'OUTROS'},
        {'codigo_id1': 'DV', 'principal_tipo_pagamento': 'DEBITO VISA', 'total_registros': 946, 'categoria': 'OUTROS'},
        {'codigo_id1': 'DV          ', 'principal_tipo_pagamento': 'DEBITO VISA (com espaços)', 'total_registros': 83, 'categoria': 'OUTROS'},
        {'codigo_id1': 'ED', 'principal_tipo_pagamento': 'ELO DEBITO', 'total_registros': 691, 'categoria': 'OUTROS'},
        {'codigo_id1': 'ED          ', 'principal_tipo_pagamento': 'ELO DEBITO (com espaços)', 'total_registros': 35, 'categoria': 'OUTROS'},
        {'codigo_id1': 'EL', 'principal_tipo_pagamento': 'ELO CREDITO', 'total_registros': 260, 'categoria': 'OUTROS'},
        {'codigo_id1': 'EL          ', 'principal_tipo_pagamento': 'ELO CREDITO (com espaços)', 'total_registros': 12, 'categoria': 'OUTROS'},
        {'codigo_id1': 'HP', 'principal_tipo_pagamento': 'HIPERCARD CRED', 'total_registros': 9, 'categoria': 'OUTROS'},
        {'codigo_id1': 'SO', 'principal_tipo_pagamento': 'SOROCRED CRED', 'total_registros': 8, 'categoria': 'OUTROS'},
        {'codigo_id1': 'VC', 'principal_tipo_pagamento': 'VOUCHER', 'total_registros': 171, 'categoria': 'OUTROS'},
        {'codigo_id1': 'VC          ', 'principal_tipo_pagamento': 'VOUCHER (com espaços)', 'total_registros': 7, 'categoria': 'OUTROS'}
    ]
    
    # Consolidar todos os códigos
    todos_codigos = carne_codes + outros_codes
    
    # Criar DataFrame
    df_consolidado = pd.DataFrame(todos_codigos)
    df_consolidado['uuid_forma_pagamento'] = ''  # Para preenchimento
    df_consolidado['observacoes'] = ''  # Para observações
    
    # Ordenar por categoria e registros
    df_consolidado = df_consolidado.sort_values(['categoria', 'total_registros'], ascending=[True, False])
    
    # Salvar arquivo consolidado
    arquivo_consolidado = 'data/originais/controles_gerais/trans_financ/separados_por_pagamento/TODOS_CODIGOS_ID1_PARA_MAPEAMENTO_UUID.csv'
    df_consolidado.to_csv(arquivo_consolidado, index=False, encoding='utf-8-sig')
    
    print(f"✅ Arquivo consolidado criado: {arquivo_consolidado}")
    print()
    
    # Resumo por categoria
    print("📊 RESUMO POR CATEGORIA:")
    resumo_categoria = df_consolidado.groupby('categoria').agg({
        'total_registros': 'sum',
        'codigo_id1': 'count'
    }).rename(columns={'codigo_id1': 'qtd_codigos'})
    
    for categoria, dados in resumo_categoria.iterrows():
        print(f"  {categoria}: {dados['qtd_codigos']} códigos, {dados['total_registros']:,} registros")
    
    print(f"\n📋 TOTAL GERAL: {len(df_consolidado)} códigos únicos")
    print()
    
    # Exibir lista para visualização
    print("📝 LISTA COMPLETA PARA MAPEAMENTO:")
    print("=" * 80)
    print("CATEGORIA | CÓDIGO | TIPO DE PAGAMENTO | REGISTROS")
    print("-" * 80)
    
    for _, row in df_consolidado.iterrows():
        categoria_icon = "🍖" if row['categoria'] == 'CARNE_LANCASTER' else "🔷"
        print(f"{categoria_icon} {row['categoria']:15} | {row['codigo_id1']:12} | {row['principal_tipo_pagamento']:35} | {row['total_registros']:,}")
    
    # Criar resumo executivo
    resumo = f"""
=== TODOS OS CÓDIGOS ID.1 PARA MAPEAMENTO UUID ===

📊 RESUMO GERAL:
• Total de códigos únicos: {len(df_consolidado)}
• CARNE LANCASTER: {len([c for c in todos_codigos if c['categoria'] == 'CARNE_LANCASTER'])} códigos
• OUTROS PAGAMENTOS: {len([c for c in todos_codigos if c['categoria'] == 'OUTROS'])} códigos

📁 ARQUIVO PARA MAPEAMENTO:
{arquivo_consolidado}

📝 INSTRUÇÕES:
1. Abra o arquivo CSV
2. Preencha a coluna 'uuid_forma_pagamento' com os UUIDs correspondentes
3. Use a coluna 'observacoes' para qualquer anotação
4. Salve o arquivo
5. Informe quando estiver pronto para aplicar os UUIDs

🎯 PRÓXIMO PASSO:
Envie os UUIDs correspondentes para cada código ID.1
"""
    
    arquivo_resumo = 'data/originais/controles_gerais/trans_financ/separados_por_pagamento/INSTRUCOES_MAPEAMENTO_UUID.txt'
    with open(arquivo_resumo, 'w', encoding='utf-8') as f:
        f.write(resumo)
    
    print(f"\n📄 Instruções salvas: {arquivo_resumo}")
    
    return df_consolidado

if __name__ == "__main__":
    df = consolidar_todos_codigos_id1()