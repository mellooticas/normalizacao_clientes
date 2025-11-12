#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import json
from datetime import datetime
import os

def carregar_mapeamento_uuid():
    """Carrega o mapeamento de códigos ID.1 para UUIDs"""
    try:
        df_mapping = pd.read_csv('data/originais/controles_gerais/trans_financ/separados_por_pagamento/TODOS_CODIGOS_ID1_PARA_MAPEAMENTO_UUID.csv')
        # Criar dicionário de mapeamento
        mapping = {}
        for _, row in df_mapping.iterrows():
            codigo = row['codigo_id1']
            uuid = row['uuid_forma_pagamento']  # Coluna correta
            if pd.notna(uuid) and uuid.strip():
                mapping[codigo] = uuid
        return mapping
    except Exception as e:
        print(f"⚠️ Erro ao carregar mapeamento UUID: {e}")
        return {}

def normalizar_nro_operacao(nro_op):
    """Remove prefixos 420- e 480- do número de operação"""
    if pd.isna(nro_op):
        return nro_op
    
    nro_str = str(nro_op)
    
    # Remover prefixos 420- e 480-
    if nro_str.startswith('420-'):
        return nro_str.replace('420-', '')
    elif nro_str.startswith('480-'):
        return nro_str.replace('480-', '')
    
    return nro_str

def processar_venda():
    """Processa arquivo VENDA.csv"""
    print("=== PROCESSAMENTO ARQUIVO VENDA.csv ===\n")
    
    # Carregar arquivo
    print("📁 Carregando arquivo VENDA.csv...")
    df = pd.read_csv('data/originais/controles_gerais/trans_financ/trans_financ_consolidado/por_origem/VENDA.csv')
    print(f"✅ {len(df):,} registros carregados\n")
    
    # Análise inicial
    print("🔍 ANÁLISE INICIAL:")
    print(f"Total de registros: {len(df):,}")
    print(f"Tipos de pagamento únicos: {df['Pagamento'].nunique()}")
    
    # Análise da coluna Pagamento
    print("\n📊 DISTRIBUIÇÃO TIPOS DE PAGAMENTO:")
    pagamentos = df['Pagamento'].value_counts()
    for pagamento, count in pagamentos.head(10).items():
        print(f"  • {pagamento}: {count:,}")
    
    # 1. SEPARAR CARNE LANCASTER
    print("\n🔄 SEPARANDO CARNE LANCASTER...")
    carne_mask = df['Pagamento'] == 'CARNE LANCASTER'
    df_carne = df[carne_mask].copy()
    df_outros = df[~carne_mask].copy()
    
    print(f"  • CARNE LANCASTER: {len(df_carne):,} registros")
    print(f"  • OUTROS PAGAMENTOS: {len(df_outros):,} registros")
    
    # 2. NORMALIZAR NRO.OPERAÇÃO
    print("\n🔧 NORMALIZANDO NRO.OPERAÇÃO...")
    
    # Para CARNE LANCASTER
    if len(df_carne) > 0:
        df_carne['Nro.operação_original'] = df_carne['Nro.operação'].copy()
        df_carne['Nro.operação'] = df_carne['Nro.operação'].apply(normalizar_nro_operacao)
        
        print(f"  • CARNE LANCASTER: {len(df_carne)} operações normalizadas")
        print("    Exemplos de normalização:")
        for i, (orig, norm) in enumerate(zip(df_carne['Nro.operação_original'].head(5), 
                                           df_carne['Nro.operação'].head(5))):
            print(f"      {i+1}. {orig} → {norm}")
    
    # Para OUTROS PAGAMENTOS
    if len(df_outros) > 0:
        df_outros['Nro.operação_original'] = df_outros['Nro.operação'].copy()
        df_outros['Nro.operação'] = df_outros['Nro.operação'].apply(normalizar_nro_operacao)
        
        print(f"  • OUTROS PAGAMENTOS: {len(df_outros)} operações normalizadas")
        print("    Exemplos de normalização:")
        for i, (orig, norm) in enumerate(zip(df_outros['Nro.operação_original'].head(5), 
                                           df_outros['Nro.operação'].head(5))):
            print(f"      {i+1}. {orig} → {norm}")
    
    # 3. APLICAR UUIDS
    print("\n🏷️ APLICANDO UUIDS...")
    mapping_uuid = carregar_mapeamento_uuid()
    print(f"  • {len(mapping_uuid)} mapeamentos UUID carregados")
    
    def aplicar_uuid(df_input, nome_arquivo):
        if len(df_input) == 0:
            return df_input
            
        df_output = df_input.copy()
        df_output['uuid'] = None
        
        # Aplicar UUIDs baseado no campo ID.1
        uuids_aplicados = 0
        for idx, row in df_output.iterrows():
            codigo_id1 = row['ID.1']
            if codigo_id1 in mapping_uuid:
                df_output.at[idx, 'uuid'] = mapping_uuid[codigo_id1]
                uuids_aplicados += 1
        
        cobertura = (uuids_aplicados / len(df_output)) * 100 if len(df_output) > 0 else 0
        print(f"    • {nome_arquivo}: {uuids_aplicados}/{len(df_output)} UUIDs aplicados ({cobertura:.1f}%)")
        
        return df_output
    
    # Aplicar UUIDs
    if len(df_carne) > 0:
        df_carne = aplicar_uuid(df_carne, "CARNE LANCASTER")
    
    if len(df_outros) > 0:
        df_outros = aplicar_uuid(df_outros, "OUTROS PAGAMENTOS")
    
    # 4. SALVAR ARQUIVOS
    print("\n💾 SALVANDO ARQUIVOS...")
    
    # Criar diretório se não existir
    output_dir = 'data/originais/controles_gerais/trans_financ/venda_processado'
    os.makedirs(output_dir, exist_ok=True)
    
    # Salvar CARNE LANCASTER (enviado para ordem_servico_pdv_carne_lancaster)
    if len(df_carne) > 0:
        carne_file = f'{output_dir}/ordem_servico_pdv_carne_lancaster_venda.csv'
        df_carne.to_csv(carne_file, index=False)
        print(f"  ✅ CARNE LANCASTER: {carne_file}")
    
    # Salvar OUTROS PAGAMENTOS
    if len(df_outros) > 0:
        outros_file = f'{output_dir}/venda_outros_pagamentos_com_uuid.csv'
        df_outros.to_csv(outros_file, index=False)
        print(f"  ✅ OUTROS PAGAMENTOS: {outros_file}")
    
    # 5. ANÁLISE FINAL
    print("\n📊 ANÁLISE FINAL:")
    
    if len(df_carne) > 0:
        print(f"\n🎯 CARNE LANCASTER:")
        print(f"  • Total de registros: {len(df_carne):,}")
        print(f"  • OSs únicas: {df_carne['Nro.operação'].nunique():,}")
        print(f"  • Clientes únicos: {df_carne['ID.2'].nunique():,}")
        print(f"  • Valor total: R$ {df_carne['Vl.movimento'].sum():,.2f}")
    
    if len(df_outros) > 0:
        print(f"\n💰 OUTROS PAGAMENTOS:")
        print(f"  • Total de registros: {len(df_outros):,}")
        print(f"  • OSs únicas: {df_outros['Nro.operação'].nunique():,}")
        print(f"  • Tipos de pagamento: {df_outros['Pagamento'].nunique()}")
        print(f"  • Valor total: R$ {df_outros['Vl.movimento'].sum():,.2f}")
        
        print(f"\n  📋 Distribuição por tipo:")
        for pagamento, count in df_outros['Pagamento'].value_counts().head(5).items():
            valor = df_outros[df_outros['Pagamento'] == pagamento]['Vl.movimento'].sum()
            print(f"    • {pagamento}: {count:,} ({valor:,.2f})")
    
    # 6. RELATÓRIO DE PROCESSAMENTO
    relatorio = {
        'data_processamento': datetime.now().isoformat(),
        'arquivo_origem': 'VENDA.csv',
        'total_registros_original': len(df),
        'carne_lancaster': {
            'registros': len(df_carne) if len(df_carne) > 0 else 0,
            'os_unicas': df_carne['Nro.operação'].nunique() if len(df_carne) > 0 else 0,
            'valor_total': float(df_carne['Vl.movimento'].sum()) if len(df_carne) > 0 else 0,
            'uuids_aplicados': len(df_carne[df_carne['uuid'].notna()]) if len(df_carne) > 0 else 0
        },
        'outros_pagamentos': {
            'registros': len(df_outros) if len(df_outros) > 0 else 0,
            'os_unicas': df_outros['Nro.operação'].nunique() if len(df_outros) > 0 else 0,
            'valor_total': float(df_outros['Vl.movimento'].sum()) if len(df_outros) > 0 else 0,
            'uuids_aplicados': len(df_outros[df_outros['uuid'].notna()]) if len(df_outros) > 0 else 0,
            'tipos_pagamento': df_outros['Pagamento'].value_counts().to_dict() if len(df_outros) > 0 else {}
        },
        'normalizacao': {
            'prefixos_removidos': ['420-', '480-'],
            'total_normalizados': len(df)
        }
    }
    
    relatorio_file = f'{output_dir}/relatorio_processamento_venda.json'
    with open(relatorio_file, 'w', encoding='utf-8') as f:
        json.dump(relatorio, f, indent=2, ensure_ascii=False)
    
    print(f"\n📋 Relatório salvo: {relatorio_file}")
    
    # Resumo final
    print(f"\n{'='*50}")
    print("✅ PROCESSAMENTO VENDA.CSV CONCLUÍDO!")
    print(f"{'='*50}")
    print(f"📊 Total processado: {len(df):,} registros")
    print(f"🎯 CARNE LANCASTER: {len(df_carne):,} registros → ordem_servico_pdv_carne_lancaster")
    print(f"💰 OUTROS PAGAMENTOS: {len(df_outros):,} registros com UUIDs")
    print(f"🔧 Números de operação normalizados (420-/480- removidos)")
    print(f"📁 Arquivos salvos em: {output_dir}")

if __name__ == "__main__":
    processar_venda()