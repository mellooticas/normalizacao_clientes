#!/usr/bin/env python3
"""
Aplicação dos UUIDs das formas de pagamento no arquivo ordem_servico_pdv_carne_lancaster.csv
Baseado no mapeamento código ID.1 -> UUID (mesmo que vazio para CARNE LANCASTER)
"""

import pandas as pd
import json
from datetime import datetime

def aplicar_uuids_carne_lancaster():
    print("=== APLICAÇÃO DE UUIDs - CARNE LANCASTER ===\n")
    
    # Carregar arquivo de mapeamento
    arquivo_mapeamento = 'data/originais/controles_gerais/trans_financ/separados_por_pagamento/TODOS_CODIGOS_ID1_PARA_MAPEAMENTO_UUID.csv'
    
    print("📁 Carregando mapeamento de UUIDs...")
    df_mapeamento = pd.read_csv(arquivo_mapeamento, encoding='utf-8-sig')
    
    # Filtrar códigos CARNE LANCASTER (mesmo sem UUID)
    df_mapeamento_carne = df_mapeamento[df_mapeamento['categoria'] == 'CARNE_LANCASTER'].copy()
    
    print(f"✅ {len(df_mapeamento_carne)} códigos CARNE LANCASTER encontrados")
    
    # Carregar arquivo de CARNE LANCASTER
    arquivo_carne = 'data/originais/controles_gerais/trans_financ/separados_por_pagamento/ordem_servico_pdv_carne_lancaster.csv'
    
    print("📁 Carregando arquivo CARNE LANCASTER...")
    df_carne = pd.read_csv(arquivo_carne, encoding='utf-8-sig')
    print(f"✅ {len(df_carne):,} registros carregados")
    print()
    
    # Aplicar informações de mapeamento
    print("🔗 Aplicando informações de mapeamento...")
    
    # Criar novas colunas
    df_carne['uuid_forma_pagamento'] = None  # UUID vazio para CARNE LANCASTER
    df_carne['tipo_pagamento_normalizado'] = 'CARNE LANCASTER'
    df_carne['observacao_pagamento'] = 'Não é pagamento - entrega de carnês'
    
    # Estatísticas
    total_registros = len(df_carne)
    
    print(f"✅ Informações aplicadas em {total_registros:,} registros")
    print("ℹ️  CARNE LANCASTER não possui UUID (não é forma de pagamento)")
    print()
    
    # Resumo por código ID.1
    print("📊 RESUMO POR CÓDIGO ID.1:")
    resumo_codigo = df_carne['ID.1'].value_counts()
    for codigo, qtd in resumo_codigo.items():
        print(f"  '{codigo}' -> {qtd:,} registros")
    print()
    
    # Salvar arquivo atualizado
    print("💾 SALVANDO ARQUIVO ATUALIZADO...")
    
    arquivo_atualizado = 'data/originais/controles_gerais/trans_financ/separados_por_pagamento/ordem_servico_pdv_carne_lancaster_com_uuid.csv'
    df_carne.to_csv(arquivo_atualizado, index=False, encoding='utf-8-sig')
    
    print(f"✅ Arquivo salvo: {arquivo_atualizado}")
    print()
    
    # Relatório de aplicação
    relatorio = {
        'data_processamento': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'arquivo_origem': arquivo_carne,
        'arquivo_mapeamento': arquivo_mapeamento,
        'arquivo_destino': arquivo_atualizado,
        'total_registros': int(len(df_carne)),
        'tipo_pagamento': 'CARNE LANCASTER',
        'uuid_forma_pagamento': None,
        'observacao': 'Não é forma de pagamento - entrega de carnês',
        'codigos_encontrados': dict(resumo_codigo)
    }
    
    arquivo_relatorio = 'data/originais/controles_gerais/trans_financ/separados_por_pagamento/relatorio_aplicacao_uuid_carne_lancaster.json'
    with open(arquivo_relatorio, 'w', encoding='utf-8') as f:
        json.dump(relatorio, f, indent=2, ensure_ascii=False)
    
    print(f"📋 Relatório salvo: {arquivo_relatorio}")
    
    # Resumo executivo
    resumo = f"""
=== APLICAÇÃO DE UUIDs - CARNE LANCASTER ===
Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}

📊 RESULTADOS:
• Total de registros: {len(df_carne):,}
• Tipo de pagamento: CARNE LANCASTER
• UUID: Não aplicável (não é forma de pagamento)
• Observação: Entrega de carnês

📋 CÓDIGOS ENCONTRADOS:
"""
    
    for codigo, qtd in resumo_codigo.items():
        resumo += f"• '{codigo}' -> {qtd:,} registros\n"
    
    resumo += f"""
📁 ARQUIVOS GERADOS:
• {arquivo_atualizado}
• {arquivo_relatorio}

ℹ️  NOTA: CARNE LANCASTER representa entrega de carnês,
   não uma forma de pagamento tradicional.

✅ Processamento concluído!
"""
    
    arquivo_resumo = 'data/originais/controles_gerais/trans_financ/separados_por_pagamento/RESUMO_APLICACAO_UUID_CARNE.txt'
    with open(arquivo_resumo, 'w', encoding='utf-8') as f:
        f.write(resumo)
    
    print(resumo)
    print(f"📄 Resumo salvo: {arquivo_resumo}")
    
    return df_carne

if __name__ == "__main__":
    df_atualizado = aplicar_uuids_carne_lancaster()