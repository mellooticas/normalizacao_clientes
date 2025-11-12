#!/usr/bin/env python3
"""
Análise e processamento completo do arquivo de vendas com outros pagamentos
14k+ linhas - todos os clientes já estão no banco
"""

import pandas as pd
from pathlib import Path
import re
from datetime import datetime

def analisar_arquivo_vendas_completo():
    """Analisa o arquivo completo de vendas com outros pagamentos"""
    
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    
    print("🔍 === ANÁLISE ARQUIVO VENDAS COMPLETO === 🔍")
    
    # 1. Carrega arquivo completo
    arquivo_completo = base_dir / "data" / "originais" / "controles_gerais" / "trans_financ" / "separados_por_pagamento" / "ordem_servico_pdv_outros_pagamentos_com_uuid_normalizado.csv"
    
    vendas_completas = pd.read_csv(arquivo_completo)
    print(f"📊 Total registros: {len(vendas_completas)}")
    
    # 2. Análise inicial
    print(f"\n=== ANÁLISE INICIAL ===")
    print(f"📅 Período: {vendas_completas['Dh.emissão'].min()} a {vendas_completas['Dh.emissão'].max()}")
    
    # Operações únicas (vendas)
    operacoes_unicas = vendas_completas['ID operação'].nunique()
    print(f"🎯 Operações (vendas) únicas: {operacoes_unicas}")
    
    # Clientes únicos
    clientes_unicos = vendas_completas['ID'].nunique()
    print(f"👥 Clientes únicos: {clientes_unicos}")
    
    # Estabelecimentos
    estabelecimentos = vendas_completas['ID emp.'].value_counts()
    print(f"🏪 Por estabelecimento:")
    for estab, count in estabelecimentos.items():
        print(f"   ID {estab}: {count} registros")
    
    # Nro.operacao_original (OSs)
    print(f"\n📋 Análise Nro.operacao_original:")
    ops_originais = vendas_completas['Nro.operacao_original'].nunique()
    print(f"   OSs únicas: {ops_originais}")
    
    # Amostra dos números originais
    amostra_ops = vendas_completas['Nro.operacao_original'].dropna().unique()[:10]
    print(f"   Amostra: {amostra_ops}")
    
    # 3. Agrupamento por venda (ID operação)
    print(f"\n=== AGRUPAMENTO POR VENDA ===")
    
    vendas_agrupadas = vendas_completas.groupby('ID operação').agg({
        'Nro.operação': 'first',
        'ID emp.': 'first',
        'ID': 'first',  # Cliente ID
        'Cliente': 'first',
        'Dh.emissão': 'first',
        'Dh.transação': 'first',
        'Vl.movimento': 'sum',  # Soma todos os pagamentos
        'ID.5': 'first',  # Vendedor
        'Vendedor': 'first',
        'arquivo_origem': 'first',
        'mes_origem': 'first',
        'Nro.operacao_original': 'first'  # OS original
    }).reset_index()
    
    print(f"✅ Vendas agrupadas: {len(vendas_agrupadas)} vendas únicas")
    
    # 4. Análise de valores
    print(f"\n💰 ANÁLISE DE VALORES:")
    print(f"   Valor total: R$ {vendas_agrupadas['Vl.movimento'].sum():,.2f}")
    print(f"   Valor médio por venda: R$ {vendas_agrupadas['Vl.movimento'].mean():.2f}")
    print(f"   Maior venda: R$ {vendas_agrupadas['Vl.movimento'].max():.2f}")
    print(f"   Menor venda: R$ {vendas_agrupadas['Vl.movimento'].min():.2f}")
    
    # 5. Padronização de lojas
    print(f"\n🏪 PADRONIZAÇÃO LOJAS:")
    
    lojas_map = {
        42: {
            'loja_id': '52f92716-d2ba-441a-ac3c-94bdfabd9722',
            'nome': 'SUZANO'
        },
        48: {
            'loja_id': 'aa7a5646-f7d6-4239-831c-6602fbabb10a',  # UUID correto de Mauá
            'nome': 'MAUA'
        }
    }
    
    vendas_agrupadas['loja_id'] = vendas_agrupadas['ID emp.'].map(lambda x: lojas_map.get(x, {}).get('loja_id'))
    vendas_agrupadas['loja_nome'] = vendas_agrupadas['ID emp.'].map(lambda x: lojas_map.get(x, {}).get('nome'))
    
    por_loja = vendas_agrupadas['loja_nome'].value_counts()
    print(f"   Por loja:")
    for loja, count in por_loja.items():
        valor_loja = vendas_agrupadas[vendas_agrupadas['loja_nome'] == loja]['Vl.movimento'].sum()
        print(f"   {loja}: {count} vendas (R$ {valor_loja:,.2f})")
    
    # 6. Ligação com clientes UUID
    print(f"\n🔗 LIGAÇÃO COM CLIENTES UUID:")
    
    # Carrega clientes UUID consolidado
    uuid_consolidado = pd.read_csv(base_dir / "data" / "clientes_uuid" / "todos_clientes_uuid_consolidado.csv")
    uuid_consolidado['id_legado_str'] = uuid_consolidado['id_legado'].astype(str).str.replace('.0', '')
    cliente_para_uuid = dict(zip(uuid_consolidado['id_legado_str'], uuid_consolidado['cliente_id']))
    
    # Aplica UUIDs
    vendas_agrupadas['cliente_id_str'] = vendas_agrupadas['ID'].astype(str)
    vendas_agrupadas['cliente_uuid'] = vendas_agrupadas['cliente_id_str'].map(cliente_para_uuid)
    
    # Estatísticas de ligação
    com_uuid = vendas_agrupadas['cliente_uuid'].notna().sum()
    sem_uuid = len(vendas_agrupadas) - com_uuid
    
    print(f"   ✅ COM UUID: {com_uuid} ({com_uuid/len(vendas_agrupadas)*100:.1f}%)")
    print(f"   ❌ SEM UUID: {sem_uuid} ({sem_uuid/len(vendas_agrupadas)*100:.1f}%)")
    
    # 7. Padronização de números de OS
    print(f"\n🔢 PADRONIZAÇÃO NÚMEROS OS:")
    
    def padronizar_numero_os(numero_original):
        """Padroniza número da OS removendo prefixos de loja"""
        if pd.isna(numero_original):
            return None
        
        numero_str = str(numero_original)
        
        # Remove prefixos 42000 ou 48000
        if numero_str.startswith('420'):
            return numero_str[3:]  # Remove 420
        elif numero_str.startswith('480'):
            return numero_str[3:]  # Remove 480
        else:
            return numero_str
    
    vendas_agrupadas['numero_os_padronizado'] = vendas_agrupadas['Nro.operacao_original'].apply(padronizar_numero_os)
    
    # Amostra de padronização
    amostra_padronizacao = vendas_agrupadas[['Nro.operacao_original', 'numero_os_padronizado']].head(10)
    print(f"   Amostra padronização:")
    for _, row in amostra_padronizacao.iterrows():
        print(f"   {row['Nro.operacao_original']} → {row['numero_os_padronizado']}")
    
    # 8. Preparação para banco
    print(f"\n🗄️  PREPARAÇÃO PARA BANCO:")
    
    # Aplica vendedor que funcionou
    vendas_agrupadas['vendedor_id'] = '2fec96c8-d492-49ab-b38a-a5d5452af4d2'
    
    # Campos para banco
    vendas_agrupadas['data_venda'] = pd.to_datetime(vendas_agrupadas['Dh.emissão']).dt.strftime('%Y-%m-%d')
    vendas_agrupadas['numero_venda'] = vendas_agrupadas['numero_os_padronizado']
    vendas_agrupadas['valor_total'] = vendas_agrupadas['Vl.movimento'].abs()
    vendas_agrupadas['valor_entrada'] = 0
    vendas_agrupadas['nome_cliente_temp'] = vendas_agrupadas['Cliente']
    vendas_agrupadas['observacoes'] = 'Importado de outros pagamentos VIXEN - Completo'
    vendas_agrupadas['status'] = 'ATIVO'
    vendas_agrupadas['cancelado'] = False
    vendas_agrupadas['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    vendas_agrupadas['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 9. Separação prontas vs pendentes
    vendas_prontas = vendas_agrupadas[vendas_agrupadas['cliente_uuid'].notna()].copy()
    vendas_pendentes = vendas_agrupadas[vendas_agrupadas['cliente_uuid'].isna()].copy()
    
    print(f"   ✅ Prontas: {len(vendas_prontas)} vendas")
    print(f"   ⏳ Pendentes: {len(vendas_pendentes)} vendas")
    
    # 10. Estatísticas finais
    print(f"\n📊 ESTATÍSTICAS FINAIS:")
    print(f"   📈 DESCOBERTA: Temos {len(vendas_prontas)} vendas adicionais!")
    print(f"   💰 Valor adicional: R$ {vendas_prontas['valor_total'].sum():,.2f}")
    print(f"   🎯 Cobertura UUID: {len(vendas_prontas)/len(vendas_agrupadas)*100:.1f}%")
    
    # Comparação com arquivos anteriores
    print(f"\n📊 COMPARAÇÃO COM ANTERIORES:")
    print(f"   OSS anteriores: ~5.076 vendas")
    print(f"   VIXEN carnê: ~1.239 vendas")
    print(f"   ESTE ARQUIVO: {len(vendas_prontas)} vendas prontas")
    print(f"   🚀 TOTAL POTENCIAL: {5076 + 1239 + len(vendas_prontas)} vendas!")
    
    return vendas_agrupadas, vendas_prontas, vendas_pendentes

if __name__ == "__main__":
    agrupadas, prontas, pendentes = analisar_arquivo_vendas_completo()
    print(f"\n🎉 ANÁLISE CONCLUÍDA!")
    print(f"📊 {len(agrupadas)} vendas totais")
    print(f"✅ {len(prontas)} vendas prontas")
    print(f"⏳ {len(pendentes)} vendas pendentes")