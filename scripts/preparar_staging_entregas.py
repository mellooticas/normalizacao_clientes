#!/usr/bin/env python3
"""
Preparação de Entregas OS para Staging - Sistema Carne Fácil
==========================================================

Prepara dados para importação em staging, onde faremos ajustes via SQL:

1. Cria estrutura de staging compatível
2. Prepara dados para upload
3. Gera SQLs de correção e migração
4. Permite análise completa antes de mover para produção

Estratégia: Staging → Correção SQL → Produção
"""

import pandas as pd
from datetime import datetime

def analisar_mapeamentos():
    """Analisa mapeamentos necessários para correção"""
    
    print("🔍 === ANÁLISE DE MAPEAMENTOS === 🔍")
    
    # Carrega dados
    try:
        df = pd.read_csv('data/vendas_para_importar/entregas_os_reais_corrigido.csv')
        print(f"📂 Dados carregados: {len(df):,} registros")
    except:
        print("❌ Arquivo não encontrado!")
        return
    
    # 1. Análise venda_id
    print(f"\n📊 ANÁLISE VENDA_ID:")
    com_venda = df['venda_id'].notna().sum()
    sem_venda = df['venda_id'].isna().sum()
    print(f"   ✅ Com venda_id: {com_venda:,} ({com_venda/len(df)*100:.1f}%)")
    print(f"   ❌ Sem venda_id: {sem_venda:,} ({sem_venda/len(df)*100:.1f}%)")
    
    # 2. Análise vendedor_uuid
    print(f"\n👥 ANÁLISE VENDEDOR:")
    com_vendedor = df['vendedor_uuid'].notna().sum()
    sem_vendedor = df['vendedor_uuid'].isna().sum()
    print(f"   ✅ Com vendedor_uuid: {com_vendedor:,} ({com_vendedor/len(df)*100:.1f}%)")
    print(f"   ❌ Sem vendedor_uuid: {sem_vendedor:,} ({sem_vendedor/len(df)*100:.1f}%)")
    
    # 3. Análise campo carne
    print(f"\n🚚 ANÁLISE CAMPO CARNE:")
    carne_stats = df['carne'].value_counts()
    for valor, count in carne_stats.items():
        pct = (count / len(df)) * 100
        boolean_val = 'TRUE' if valor == 'Sim' else 'FALSE'
        print(f"   '{valor}' → {boolean_val}: {count:,} ({pct:.1f}%)")
    
    # 4. Análise por loja
    print(f"\n🏪 ANÁLISE POR LOJA:")
    loja_stats = df.groupby('loja_origem').agg({
        'venda_id': lambda x: x.notna().sum(),
        'vendedor_uuid': lambda x: x.notna().sum(),
        'os_numero': 'count'
    }).rename(columns={
        'venda_id': 'com_venda_id',
        'vendedor_uuid': 'com_vendedor', 
        'os_numero': 'total'
    })
    
    for loja, stats in loja_stats.iterrows():
        total = stats['total']
        com_venda = stats['com_venda_id']
        com_vendedor = stats['com_vendedor']
        print(f"   {loja}:")
        print(f"      Total: {total:,}")
        print(f"      Com venda_id: {com_venda:,} ({com_venda/total*100:.1f}%)")
        print(f"      Com vendedor: {com_vendedor:,} ({com_vendedor/total*100:.1f}%)")
    
    return df

def preparar_staging():
    """Prepara dados para staging"""
    
    print(f"\n🏗️ === PREPARAÇÃO PARA STAGING === 🏗️")
    
    # Carrega dados
    df = pd.read_csv('data/vendas_para_importar/entregas_os_reais_corrigido.csv')
    
    # Prepara estrutura para staging (mantém todos os campos para análise)
    staging_df = df.copy()
    
    # Converte campo carne para boolean
    staging_df['tem_carne'] = staging_df['carne'].apply(lambda x: x == 'Sim' if pd.notna(x) else False)
    
    # Renomeia vendedor_uuid para vendedor_id 
    staging_df['vendedor_id'] = staging_df['vendedor_uuid']
    
    # Organiza colunas para staging
    colunas_staging = [
        'id',
        'venda_id',           # Pode ser NULL em staging
        'vendedor_id',        # Renomeado de vendedor_uuid
        'data_entrega',
        'tem_carne',          # Convertido de carne string para boolean
        'created_at',
        'updated_at',
        # Campos auxiliares para correção
        'os_numero',
        'loja_id',
        'loja_origem',
        'carne',              # Campo original para referência
        'observacoes'
    ]
    
    staging_final = staging_df[colunas_staging].copy()
    
    # Salva para staging
    output_staging = 'data/vendas_para_importar/entregas_os_staging.csv'
    staging_final.to_csv(output_staging, index=False)
    
    print(f"📁 Arquivo staging criado: {output_staging}")
    print(f"📊 Registros: {len(staging_final):,}")
    print(f"📋 Colunas: {len(colunas_staging)}")
    
    return staging_final

def gerar_sqls_correcao():
    """Gera SQLs para correção em staging"""
    
    print(f"\n🛠️ === GERAÇÃO DE SQLs DE CORREÇÃO === 🛠️")
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    sql_file = f'correção_entregas_staging_{timestamp}.sql'
    
    sqls = []
    
    # 1. Criar tabela de staging
    sqls.append("""
-- 1. CRIAR TABELA DE STAGING
CREATE TABLE IF NOT EXISTS staging.entregas_os_temp (
    id UUID NOT NULL,
    venda_id UUID NULL,              -- NULL permitido em staging
    vendedor_id UUID NULL,
    data_entrega DATE NOT NULL,
    tem_carne BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    -- Campos auxiliares para correção
    os_numero TEXT,
    loja_id UUID,
    loja_origem TEXT,
    carne_original TEXT,
    observacoes TEXT,
    PRIMARY KEY (id)
);
""")
    
    # 2. Análises após importação
    sqls.append("""
-- 2. ANÁLISES APÓS IMPORTAÇÃO DOS DADOS

-- Contagem geral
SELECT 
    COUNT(*) as total_registros,
    COUNT(venda_id) as com_venda_id,
    COUNT(*) - COUNT(venda_id) as sem_venda_id,
    ROUND(COUNT(venda_id)::decimal / COUNT(*) * 100, 1) as percentual_com_venda
FROM staging.entregas_os_temp;

-- Por loja
SELECT 
    loja_origem,
    COUNT(*) as total,
    COUNT(venda_id) as com_venda_id,
    COUNT(vendedor_id) as com_vendedor,
    ROUND(COUNT(venda_id)::decimal / COUNT(*) * 100, 1) as pct_venda
FROM staging.entregas_os_temp
GROUP BY loja_origem
ORDER BY total DESC;

-- Análise campo tem_carne
SELECT 
    tem_carne,
    carne_original,
    COUNT(*) as quantidade
FROM staging.entregas_os_temp
GROUP BY tem_carne, carne_original
ORDER BY quantidade DESC;
""")
    
    # 3. Correções por OS numero
    sqls.append("""
-- 3. CORREÇÃO DE VENDA_ID POR OS_NUMERO

-- Buscar vendas por numero_venda = os_numero
UPDATE staging.entregas_os_temp 
SET venda_id = v.id
FROM vendas.vendas v
WHERE staging.entregas_os_temp.venda_id IS NULL
  AND staging.entregas_os_temp.os_numero = v.numero_venda::text;

-- Verificar correções
SELECT 
    'Após correção OS' as status,
    COUNT(*) as total,
    COUNT(venda_id) as com_venda_id,
    ROUND(COUNT(venda_id)::decimal / COUNT(*) * 100, 1) as percentual
FROM staging.entregas_os_temp;
""")
    
    # 4. Migração para produção
    sqls.append("""
-- 4. MIGRAÇÃO PARA PRODUÇÃO

-- Inserir apenas registros com venda_id válido
INSERT INTO vendas.entregas_os (
    id,
    venda_id,
    vendedor_id,
    data_entrega,
    tem_carne,
    created_at,
    updated_at
)
SELECT 
    id,
    venda_id,
    vendedor_id,
    data_entrega,
    tem_carne,
    created_at,
    updated_at
FROM staging.entregas_os_temp
WHERE venda_id IS NOT NULL
  AND NOT EXISTS (
      SELECT 1 FROM vendas.entregas_os p 
      WHERE p.venda_id = staging.entregas_os_temp.venda_id 
        AND p.data_entrega = staging.entregas_os_temp.data_entrega
  );

-- Verificar inserções
SELECT COUNT(*) as registros_inseridos FROM vendas.entregas_os;
""")
    
    # 5. Relatório final
    sqls.append("""
-- 5. RELATÓRIO FINAL

-- Registros não migrados (para análise)
SELECT 
    'Registros não migrados' as tipo,
    COUNT(*) as quantidade,
    string_agg(DISTINCT loja_origem, ', ') as lojas
FROM staging.entregas_os_temp
WHERE venda_id IS NULL;

-- Resumo final por loja
SELECT 
    loja_origem,
    COUNT(*) as total_staging,
    COUNT(CASE WHEN venda_id IS NOT NULL THEN 1 END) as migrados,
    COUNT(CASE WHEN venda_id IS NULL THEN 1 END) as nao_migrados
FROM staging.entregas_os_temp
GROUP BY loja_origem
ORDER BY total_staging DESC;

-- Limpeza (comentado para segurança)
-- DROP TABLE staging.entregas_os_temp;
""")
    
    # Salva arquivo SQL
    with open(sql_file, 'w', encoding='utf-8') as f:
        f.write("-- CORREÇÃO DE ENTREGAS OS - STAGING\n")
        f.write(f"-- Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("-- \n")
        f.write("-- EXECUÇÃO:\n")
        f.write("-- 1. Importar entregas_os_staging.csv na tabela staging.entregas_os_temp\n")
        f.write("-- 2. Executar os SQLs abaixo em sequência\n")
        f.write("-- 3. Verificar relatórios antes de cada passo\n\n")
        
        for i, sql in enumerate(sqls, 1):
            f.write(f"-- ===== PASSO {i} =====\n")
            f.write(sql)
            f.write("\n\n")
    
    print(f"📁 SQLs gerados: {sql_file}")
    print("🔧 Passos para execução:")
    print("   1. Importar entregas_os_staging.csv")
    print("   2. Executar SQLs do arquivo")
    print("   3. Verificar cada passo")
    print("   4. Migrar dados corretos")

def main():
    """Processo completo de preparação para staging"""
    
    print("🏗️ === PREPARAÇÃO ENTREGAS OS - STAGING === 🏗️")
    
    # 1. Análise dos dados atuais
    df = analisar_mapeamentos()
    if df is None:
        return
    
    # 2. Preparação para staging
    staging_df = preparar_staging()
    
    # 3. Geração de SQLs
    gerar_sqls_correcao()
    
    print(f"\n🎯 === ESTRATÉGIA COMPLETA === 🎯")
    print("✅ Dados preparados para staging")
    print("✅ SQLs de correção gerados")
    print("✅ Processo de migração definido")
    print("✅ Preservação de dados garantida")
    
    print(f"\n📋 RESUMO:")
    print(f"   📂 Staging CSV: entregas_os_staging.csv")
    print(f"   🛠️ SQLs: correção_entregas_staging_*.sql")
    print(f"   📊 Registros: {len(staging_df):,}")
    print(f"   🎯 Estratégia: Staging → SQL → Produção")

if __name__ == "__main__":
    main()