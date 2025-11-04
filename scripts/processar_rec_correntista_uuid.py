#!/usr/bin/env python3
"""
Processamento final do REC. CORRENTISTA com aplicação de UUIDs
"""

import pandas as pd
import json
from datetime import datetime

def processar_rec_correntista_final():
    print("=== PROCESSAMENTO FINAL: REC. CORRENTISTA ===\n")
    
    # Carregar arquivo REC. CORRENTISTA
    arquivo_rec = 'data/originais/controles_gerais/trans_financ/trans_financ_consolidado/por_origem/REC. CORRENTISTA.csv'
    
    print("📁 Carregando REC. CORRENTISTA...")
    df_rec = pd.read_csv(arquivo_rec, encoding='utf-8-sig')
    print(f"✅ {len(df_rec):,} registros carregados")
    print()
    
    # Análise das formas de pagamento
    print("💳 FORMAS DE PAGAMENTO:")
    pagamentos_rec = df_rec['Pagamento'].value_counts()
    for pagamento, qtd in pagamentos_rec.items():
        print(f"  {pagamento:25} -> {qtd:,}")
    print()
    
    # Códigos ID.1
    print("🔑 CÓDIGOS ID.1:")
    codigos_rec = df_rec['ID.1'].value_counts()
    for codigo, qtd in codigos_rec.items():
        if pd.notna(codigo):
            print(f"  '{codigo}' -> {qtd:,}")
    print()
    
    # Carregar mapeamento de UUIDs
    arquivo_mapeamento = 'data/originais/controles_gerais/trans_financ/separados_por_pagamento/TODOS_CODIGOS_ID1_PARA_MAPEAMENTO_UUID.csv'
    df_mapeamento = pd.read_csv(arquivo_mapeamento, encoding='utf-8-sig')
    
    # Criar dicionário de mapeamento
    mapeamento_dict = {}
    for _, row in df_mapeamento.iterrows():
        if pd.notna(row['uuid_forma_pagamento']) and row['uuid_forma_pagamento'] != '':
            mapeamento_dict[row['codigo_id1']] = {
                'uuid': row['uuid_forma_pagamento'],
                'tipo': row['principal_tipo_pagamento']
            }
    
    print(f"📋 Mapeamento carregado: {len(mapeamento_dict)} códigos com UUID")
    print()
    
    # Aplicar UUIDs
    print("🔗 APLICANDO UUIDs...")
    
    df_rec['uuid_forma_pagamento'] = None
    df_rec['tipo_pagamento_normalizado'] = None
    
    registros_com_uuid = 0
    registros_sem_uuid = 0
    
    for index, row in df_rec.iterrows():
        codigo_id1 = row['ID.1']
        
        if pd.notna(codigo_id1) and codigo_id1 in mapeamento_dict:
            df_rec.loc[index, 'uuid_forma_pagamento'] = mapeamento_dict[codigo_id1]['uuid']
            df_rec.loc[index, 'tipo_pagamento_normalizado'] = mapeamento_dict[codigo_id1]['tipo']
            registros_com_uuid += 1
        else:
            registros_sem_uuid += 1
    
    print(f"✅ UUIDs aplicados em {registros_com_uuid:,} registros")
    print(f"⚠️  {registros_sem_uuid:,} registros sem UUID")
    print(f"📊 Taxa de aplicação: {(registros_com_uuid/len(df_rec))*100:.1f}%")
    print()
    
    # Análise das referências de carnê
    print("🍖 ANÁLISE DAS REFERÊNCIAS DE CARNÊ:")
    referencias_carne = df_rec[df_rec['Referência'].str.contains('CARNE|LANCASTER|PARCELA', case=False, na=False)]
    print(f"Total de referências de carnê: {len(referencias_carne):,}")
    print()
    
    # Salvar arquivo
    arquivo_rec_uuid = 'data/originais/controles_gerais/trans_financ/separados_por_pagamento/rec_correntista_com_uuid.csv'
    df_rec.to_csv(arquivo_rec_uuid, index=False, encoding='utf-8-sig')
    
    print(f"💾 Arquivo salvo: {arquivo_rec_uuid}")
    print()
    
    print("✅ PROCESSAMENTO CONCLUÍDO!")
    print(f"REC. CORRENTISTA agora possui UUIDs das formas de pagamento")
    print(f"Este arquivo contém os PAGAMENTOS das parcelas de carnê")
    
    return df_rec

if __name__ == "__main__":
    df_final = processar_rec_correntista_final()