#!/usr/bin/env python3
"""
Aplicação dos UUIDs das formas de pagamento no arquivo ordem_servico_pdv_outros_pagamentos.csv
Baseado no mapeamento código ID.1 -> UUID
"""

import pandas as pd
import json
from datetime import datetime

def aplicar_uuids_outros_pagamentos():
    print("=== APLICAÇÃO DE UUIDs - OUTROS PAGAMENTOS ===\n")
    
    # Carregar arquivo de mapeamento
    arquivo_mapeamento = 'data/originais/controles_gerais/trans_financ/separados_por_pagamento/TODOS_CODIGOS_ID1_PARA_MAPEAMENTO_UUID.csv'
    
    print("📁 Carregando mapeamento de UUIDs...")
    df_mapeamento = pd.read_csv(arquivo_mapeamento, encoding='utf-8-sig')
    
    # Filtrar apenas códigos com UUID preenchido
    df_mapeamento_valido = df_mapeamento[
        (df_mapeamento['uuid_forma_pagamento'].notna()) & 
        (df_mapeamento['uuid_forma_pagamento'] != '')
    ].copy()
    
    print(f"✅ {len(df_mapeamento_valido)} códigos com UUID válido encontrados")
    
    # Criar dicionário de mapeamento
    mapeamento_dict = {}
    for _, row in df_mapeamento_valido.iterrows():
        codigo = row['codigo_id1']
        uuid_pagamento = row['uuid_forma_pagamento']
        tipo_pagamento = row['principal_tipo_pagamento']
        mapeamento_dict[codigo] = {
            'uuid': uuid_pagamento,
            'tipo': tipo_pagamento
        }
    
    print(f"📋 Mapeamento criado para {len(mapeamento_dict)} códigos")
    print()
    
    # Carregar arquivo de outros pagamentos
    arquivo_outros = 'data/originais/controles_gerais/trans_financ/separados_por_pagamento/ordem_servico_pdv_outros_pagamentos.csv'
    
    print("📁 Carregando arquivo de outros pagamentos...")
    df_outros = pd.read_csv(arquivo_outros, encoding='utf-8-sig')
    print(f"✅ {len(df_outros):,} registros carregados")
    print()
    
    # Aplicar UUIDs
    print("🔗 Aplicando UUIDs...")
    
    # Criar nova coluna para UUID da forma de pagamento
    df_outros['uuid_forma_pagamento'] = None
    df_outros['tipo_pagamento_normalizado'] = None
    
    # Estatísticas
    registros_com_uuid = 0
    registros_sem_uuid = 0
    codigos_aplicados = set()
    
    for index, row in df_outros.iterrows():
        codigo_id1 = row['ID.1']
        
        if pd.notna(codigo_id1) and codigo_id1 in mapeamento_dict:
            df_outros.loc[index, 'uuid_forma_pagamento'] = mapeamento_dict[codigo_id1]['uuid']
            df_outros.loc[index, 'tipo_pagamento_normalizado'] = mapeamento_dict[codigo_id1]['tipo']
            registros_com_uuid += 1
            codigos_aplicados.add(codigo_id1)
        else:
            registros_sem_uuid += 1
    
    print(f"✅ UUIDs aplicados em {registros_com_uuid:,} registros")
    print(f"⚠️  {registros_sem_uuid:,} registros sem UUID (códigos não mapeados)")
    print(f"📊 {len(codigos_aplicados)} códigos diferentes aplicados")
    print()
    
    # Resumo por UUID
    print("📊 RESUMO POR UUID APLICADO:")
    resumo_uuid = df_outros[df_outros['uuid_forma_pagamento'].notna()].groupby(['uuid_forma_pagamento', 'tipo_pagamento_normalizado']).size().reset_index(name='quantidade')
    resumo_uuid = resumo_uuid.sort_values('quantidade', ascending=False)
    
    for _, row in resumo_uuid.iterrows():
        print(f"  {row['uuid_forma_pagamento']} | {row['tipo_pagamento_normalizado']:35} | {row['quantidade']:,}")
    print()
    
    # Verificar códigos sem UUID
    print("⚠️  CÓDIGOS SEM UUID:")
    codigos_sem_uuid = df_outros[df_outros['uuid_forma_pagamento'].isna()]['ID.1'].value_counts()
    for codigo, qtd in codigos_sem_uuid.items():
        if pd.notna(codigo):
            print(f"  '{codigo}' -> {qtd:,} registros")
    print()
    
    # Salvar arquivo atualizado
    print("💾 SALVANDO ARQUIVO ATUALIZADO...")
    
    arquivo_atualizado = 'data/originais/controles_gerais/trans_financ/separados_por_pagamento/ordem_servico_pdv_outros_pagamentos_com_uuid.csv'
    df_outros.to_csv(arquivo_atualizado, index=False, encoding='utf-8-sig')
    
    print(f"✅ Arquivo salvo: {arquivo_atualizado}")
    print()
    
    # Relatório de aplicação
    relatorio = {
        'data_processamento': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'arquivo_origem': arquivo_outros,
        'arquivo_mapeamento': arquivo_mapeamento,
        'arquivo_destino': arquivo_atualizado,
        'total_registros': int(len(df_outros)),
        'registros_com_uuid': int(registros_com_uuid),
        'registros_sem_uuid': int(registros_sem_uuid),
        'percentual_com_uuid': round((registros_com_uuid / len(df_outros)) * 100, 2),
        'codigos_aplicados': len(codigos_aplicados),
        'uuids_unicos': int(len(resumo_uuid)),
        'resumo_por_uuid': [
            {
                'uuid': row['uuid_forma_pagamento'],
                'tipo': row['tipo_pagamento_normalizado'],
                'quantidade': int(row['quantidade'])
            }
            for _, row in resumo_uuid.iterrows()
        ]
    }
    
    arquivo_relatorio = 'data/originais/controles_gerais/trans_financ/separados_por_pagamento/relatorio_aplicacao_uuid_outros_pagamentos.json'
    with open(arquivo_relatorio, 'w', encoding='utf-8') as f:
        json.dump(relatorio, f, indent=2, ensure_ascii=False)
    
    print(f"📋 Relatório salvo: {arquivo_relatorio}")
    
    # Resumo executivo
    resumo = f"""
=== APLICAÇÃO DE UUIDs - OUTROS PAGAMENTOS ===
Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}

📊 RESULTADOS:
• Total de registros: {len(df_outros):,}
• Registros com UUID: {registros_com_uuid:,} ({(registros_com_uuid / len(df_outros)) * 100:.1f}%)
• Registros sem UUID: {registros_sem_uuid:,} ({(registros_sem_uuid / len(df_outros)) * 100:.1f}%)

📋 CÓDIGOS APLICADOS: {len(codigos_aplicados)}
📋 UUIDs ÚNICOS: {len(resumo_uuid)}

🏆 TOP 5 UUIDS MAIS USADOS:
"""
    
    for i, (_, row) in enumerate(resumo_uuid.head(5).iterrows()):
        resumo += f"{i+1}. {row['tipo_pagamento_normalizado']:25} -> {row['quantidade']:,} registros\n"
    
    resumo += f"""
📁 ARQUIVOS GERADOS:
• {arquivo_atualizado}
• {arquivo_relatorio}

✅ Aplicação de UUIDs concluída com sucesso!
"""
    
    arquivo_resumo = 'data/originais/controles_gerais/trans_financ/separados_por_pagamento/RESUMO_APLICACAO_UUID_OUTROS.txt'
    with open(arquivo_resumo, 'w', encoding='utf-8') as f:
        f.write(resumo)
    
    print(resumo)
    print(f"📄 Resumo salvo: {arquivo_resumo}")
    
    return df_outros

if __name__ == "__main__":
    df_atualizado = aplicar_uuids_outros_pagamentos()