#!/usr/bin/env python3
"""
Correção Final de Entregas OS - Sistema Carne Fácil
==================================================

Corrige CSV final usando dados existentes:
1. Cruza os_numero com vendas para obter venda_id corretos
2. Mapeia vendedor_uuid para vendedor_id
3. Ajusta estrutura para tabela final
4. Remove registros sem venda_id (constraint obrigatória)
5. Gera CSV pronto para importação direta

Estratégia: CSV → Correção → Importação Direta
"""

import pandas as pd
import uuid
from datetime import datetime

def corrigir_csv_final():
    """Corrige CSV final com dados reais disponíveis"""
    
    print("🔧 === CORREÇÃO FINAL DO CSV === 🔧")
    
    # 1. Carrega dados de entregas
    try:
        entregas_df = pd.read_csv('data/vendas_para_importar/entregas_os_reais_corrigido.csv')
        print(f"📂 Entregas carregadas: {len(entregas_df):,} registros")
    except:
        print("❌ Arquivo de entregas não encontrado!")
        return
    
    # 2. Carrega dados de vendas para cruzamento
    try:
        vendas_df = pd.read_csv('data/vendas_para_importar/vendas_totais_com_uuid.csv')
        print(f"📂 Vendas carregadas: {len(vendas_df):,} registros")
    except:
        print("❌ Arquivo de vendas não encontrado!")
        return
    
    print(f"\n🔄 Iniciando correções...")
    
    # 3. Prepara dados para cruzamento
    entregas_df['os_numero'] = entregas_df['os_numero'].astype(str)
    vendas_df['numero_venda'] = vendas_df['numero_venda'].astype(str)
    
    # 4. Faz cruzamento por OS número
    print("🔗 Cruzando entregas com vendas por os_numero...")
    
    antes_cruzamento = entregas_df['venda_id'].notna().sum()
    
    # Remove venda_id atual para refazer cruzamento completo
    entregas_df = entregas_df.drop('venda_id', axis=1, errors='ignore')
    
    # Faz merge com vendas
    entregas_corrigidas = entregas_df.merge(
        vendas_df[['numero_venda', 'id', 'vendedor_id']],
        left_on='os_numero',
        right_on='numero_venda',
        how='left'
    )
    
    # Renomeia colunas
    entregas_corrigidas['venda_id'] = entregas_corrigidas['id_y']
    entregas_corrigidas['vendedor_id_venda'] = entregas_corrigidas['vendedor_id']
    entregas_corrigidas = entregas_corrigidas.drop(['id_y', 'numero_venda', 'vendedor_id'], axis=1)
    entregas_corrigidas = entregas_corrigidas.rename(columns={'id_x': 'id'})
    
    # Estatísticas do cruzamento
    depois_cruzamento = entregas_corrigidas['venda_id'].notna().sum()
    sem_venda = entregas_corrigidas['venda_id'].isna().sum()
    
    print(f"✅ Cruzamento concluído:")
    print(f"   Antes: {antes_cruzamento:,} com venda_id")
    print(f"   Depois: {depois_cruzamento:,} com venda_id")
    print(f"   Melhoria: +{depois_cruzamento - antes_cruzamento:,} registros")
    print(f"   Sem venda: {sem_venda:,} registros")
    
    # 5. Define vendedor_id final
    print("👥 Definindo vendedor_id...")
    
    # Prioriza vendedor da venda, depois vendedor da entrega
    entregas_corrigidas['vendedor_id_final'] = entregas_corrigidas['vendedor_id_venda'].fillna(
        entregas_corrigidas['vendedor_uuid']
    )
    
    vendedores_definidos = entregas_corrigidas['vendedor_id_final'].notna().sum()
    print(f"   ✅ Vendedor definido: {vendedores_definidos:,} registros")
    
    # 6. Converte campo carne para boolean
    print("🚚 Convertendo campo carne...")
    entregas_corrigidas['tem_carne'] = entregas_corrigidas['carne'].apply(
        lambda x: True if x == 'Sim' else False
    )
    
    carne_stats = entregas_corrigidas['tem_carne'].value_counts()
    print(f"   TRUE (carnê): {carne_stats.get(True, 0):,}")
    print(f"   FALSE (produtos): {carne_stats.get(False, 0):,}")
    
    # 7. Filtra apenas registros com venda_id (constraint obrigatória)
    print(f"\n⚡ Filtrando registros válidos...")
    
    antes_filtro = len(entregas_corrigidas)
    entregas_validas = entregas_corrigidas[entregas_corrigidas['venda_id'].notna()].copy()
    depois_filtro = len(entregas_validas)
    
    print(f"   Antes do filtro: {antes_filtro:,}")
    print(f"   Depois do filtro: {depois_filtro:,}")
    print(f"   Removidos: {antes_filtro - depois_filtro:,} (sem venda_id)")
    
    # 8. Verifica constraint única venda_id + data_entrega
    print(f"\n🔍 Verificando constraint única...")
    
    duplicatas = entregas_validas.groupby(['venda_id', 'data_entrega']).size()
    duplicatas_encontradas = duplicatas[duplicatas > 1]
    
    if len(duplicatas_encontradas) > 0:
        print(f"❌ Encontradas {len(duplicatas_encontradas)} violações de constraint única:")
        for (venda_id, data), count in duplicatas_encontradas.head(5).items():
            print(f"   venda_id {venda_id[:8]}... em {data}: {count} registros")
        
        # Remove duplicatas mantendo primeira
        antes_dedup = len(entregas_validas)
        entregas_validas = entregas_validas.drop_duplicates(
            subset=['venda_id', 'data_entrega'], 
            keep='first'
        )
        depois_dedup = len(entregas_validas)
        print(f"   ✅ Removidas {antes_dedup - depois_dedup} duplicatas")
    else:
        print(f"   ✅ Nenhuma violação de constraint encontrada")
    
    # 9. Estrutura final para tabela
    print(f"\n📋 Preparando estrutura final...")
    
    # Colunas finais conforme tabela
    entregas_final = pd.DataFrame({
        'id': [str(uuid.uuid4()) for _ in range(len(entregas_validas))],  # Novos IDs únicos
        'venda_id': entregas_validas['venda_id'],
        'vendedor_id': entregas_validas['vendedor_id_final'],
        'data_entrega': entregas_validas['data_entrega'],
        'tem_carne': entregas_validas['tem_carne'],
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    
    # 10. Validações finais
    print(f"\n🔍 === VALIDAÇÕES FINAIS === 🔍")
    print(f"✅ Total de registros: {len(entregas_final):,}")
    print(f"✅ IDs únicos: {entregas_final['id'].nunique() == len(entregas_final)}")
    print(f"✅ Venda_IDs válidos: {entregas_final['venda_id'].notna().all()}")
    print(f"✅ Datas válidas: {entregas_final['data_entrega'].notna().all()}")
    print(f"✅ Constraint única: {len(entregas_final.groupby(['venda_id', 'data_entrega']).size().reset_index()) == len(entregas_final)}")
    
    # Estatísticas finais
    print(f"\n📊 === ESTATÍSTICAS FINAIS === 📊")
    
    # Por tipo de entrega
    carne_final = entregas_final['tem_carne'].value_counts()
    for valor, count in carne_final.items():
        tipo = "Carnê" if valor else "Produtos"
        pct = (count / len(entregas_final)) * 100
        print(f"   {tipo}: {count:,} ({pct:.1f}%)")
    
    # Vendedores
    com_vendedor = entregas_final['vendedor_id'].notna().sum()
    pct_vendedor = (com_vendedor / len(entregas_final)) * 100
    print(f"   Com vendedor: {com_vendedor:,} ({pct_vendedor:.1f}%)")
    
    # Período
    print(f"   Período: {entregas_final['data_entrega'].min()} → {entregas_final['data_entrega'].max()}")
    
    # 11. Salva arquivo final
    output_path = 'data/vendas_para_importar/entregas_os_final_para_importacao.csv'
    entregas_final.to_csv(output_path, index=False)
    
    print(f"\n💾 Arquivo final salvo: {output_path}")
    print(f"📁 Tamanho: {len(entregas_final):,} registros")
    print(f"📊 Colunas: {', '.join(entregas_final.columns)}")
    
    print(f"\n🎯 === RESUMO DA CORREÇÃO === 🎯")
    print("✅ Cruzamento completo com vendas realizado")
    print("✅ Vendedor_id corrigido e mapeado")
    print("✅ Campo tem_carne convertido para boolean")
    print("✅ Constraint única respeitada")
    print("✅ Apenas registros válidos mantidos")
    print("✅ Estrutura compatível com tabela final")
    
    print(f"\n🚀 === PRONTO PARA IMPORTAÇÃO === 🚀")
    print("✅ CSV corrigido e validado")
    print("✅ Constraints respeitadas")
    print("✅ Foreign keys válidas")
    print("✅ Pode importar direto na tabela!")
    
    return entregas_final

if __name__ == "__main__":
    corrigir_csv_final()