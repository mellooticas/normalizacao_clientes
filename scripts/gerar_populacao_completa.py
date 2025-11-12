#!/usr/bin/env python3
"""
Gerador do script SQL completo para população das tabelas de vendedores
Usa os dados processados dos arquivos CSV
"""

import pandas as pd
from datetime import datetime

def gerar_script_populacao():
    print("🔄 Gerando script completo de população...")
    
    # Ler dados dos vendedores únicos
    df_vendedores = pd.read_csv('VENDEDORES_UNICOS_UUID.csv')
    print(f"✅ Carregados {len(df_vendedores)} vendedores únicos")
    
    # Ler dados dos relacionamentos
    df_relacionamentos = pd.read_csv('VENDEDORES_LOJAS_RELACIONAMENTO.csv')
    print(f"✅ Carregados {len(df_relacionamentos)} relacionamentos")
    
    # Começar o script
    script = []
    script.append("-- =============================================")
    script.append("-- POPULAÇÃO COMPLETA DAS TABELAS REESTRUTURADAS")
    script.append("-- =============================================")
    script.append(f"-- Gerado automaticamente em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    script.append(f"-- {len(df_vendedores)} vendedores únicos + {len(df_relacionamentos)} relacionamentos")
    script.append("")
    
    # 1. Limpeza das tabelas
    script.append("-- =============================================")
    script.append("-- 1. LIMPAR TABELAS PARA NOVA POPULAÇÃO")
    script.append("-- =============================================")
    script.append("")
    script.append("-- Limpar relacionamentos primeiro (por causa da FK)")
    script.append("TRUNCATE TABLE core.vendedores_lojas CASCADE;")
    script.append("")
    script.append("-- Limpar vendedores")
    script.append("TRUNCATE TABLE core.vendedores CASCADE;")
    script.append("")
    
    # 2. Inserir vendedores únicos
    script.append("-- =============================================")
    script.append(f"-- 2. INSERIR VENDEDORES ÚNICOS ({len(df_vendedores)} registros)")
    script.append("-- =============================================")
    script.append("")
    script.append("INSERT INTO core.vendedores (id, nome, nome_padronizado, nome_exibicao, ativo, created_at, updated_at) VALUES")
    
    vendedores_values = []
    for _, row in df_vendedores.iterrows():
        vendedores_values.append(
            f"('{row['uuid']}', '{row['nome_padronizado']}', '{row['nome_padronizado']}', '{row['nome_exibicao']}', true, NOW(), NOW())"
        )
    
    script.append(',\n'.join(vendedores_values) + ';')
    script.append("")
    
    # 3. Inserir relacionamentos por loja
    script.append("-- =============================================")
    script.append(f"-- 3. INSERIR RELACIONAMENTOS VENDEDOR-LOJA ({len(df_relacionamentos)} registros)")
    script.append("-- =============================================")
    script.append("")
    
    # Agrupar por loja
    lojas = df_relacionamentos.groupby(['loja_nome', 'loja_codigo', 'loja_uuid'])
    
    for (loja_nome, loja_codigo, loja_uuid), group in lojas:
        script.append(f"-- {loja_nome} ({loja_codigo}) - {len(group)} vendedores")
        script.append(f"INSERT INTO core.vendedores_lojas (vendedor_id, loja_id, codigo_vendedor_sistema, ativo, data_inicio) VALUES")
        
        relacionamentos_values = []
        for _, row in group.iterrows():
            relacionamentos_values.append(
                f"('{row['vendedor_uuid']}', '{row['loja_uuid']}', '{row['codigo_vendedor_sistema']}', true, '2023-01-01')"
            )
        
        script.append(',\n'.join(relacionamentos_values) + ';')
        script.append("")
    
    # 4. Verificações finais
    script.append("-- =============================================")
    script.append("-- 4. VERIFICAÇÕES FINAIS")
    script.append("-- =============================================")
    script.append("")
    script.append("-- Contar registros inseridos")
    script.append("SELECT ")
    script.append("    'vendedores' as tabela, ")
    script.append("    COUNT(*) as total,")
    script.append("    COUNT(CASE WHEN ativo = true THEN 1 END) as ativos")
    script.append("FROM core.vendedores")
    script.append("UNION ALL")
    script.append("SELECT ")
    script.append("    'vendedores_lojas' as tabela, ")
    script.append("    COUNT(*) as total,")
    script.append("    COUNT(CASE WHEN ativo = true THEN 1 END) as ativos")
    script.append("FROM core.vendedores_lojas;")
    script.append("")
    
    script.append("-- Verificar distribuição por loja")
    script.append("SELECT ")
    script.append("    l.nome as loja_nome,")
    script.append("    l.codigo as loja_codigo,")
    script.append("    COUNT(vl.vendedor_id) as total_vendedores")
    script.append("FROM core.lojas l")
    script.append("LEFT JOIN core.vendedores_lojas vl ON l.id = vl.loja_id")
    script.append("GROUP BY l.id, l.nome, l.codigo")
    script.append("ORDER BY l.codigo;")
    script.append("")
    
    script.append("-- Verificar se algum vendedor ficou sem loja")
    script.append("SELECT ")
    script.append("    v.nome_padronizado,")
    script.append("    CASE WHEN vl.vendedor_id IS NULL THEN 'SEM LOJA' ELSE 'COM LOJA' END as status")
    script.append("FROM core.vendedores v")
    script.append("LEFT JOIN core.vendedores_lojas vl ON v.id = vl.vendedor_id")
    script.append("WHERE vl.vendedor_id IS NULL")
    script.append("ORDER BY v.nome_padronizado;")
    script.append("")
    
    # 5. Status final
    script.append("-- =============================================")
    script.append("-- 5. STATUS FINAL")
    script.append("-- =============================================")
    script.append("")
    script.append("SELECT 'População completa finalizada!' as status;")
    script.append("")
    script.append("-- RESUMO:")
    script.append(f"-- ✅ {len(df_vendedores)} vendedores únicos inseridos")
    script.append(f"-- ✅ {len(df_relacionamentos)} relacionamentos vendedor-loja inseridos")
    script.append("-- ✅ Todas as 6 lojas contempladas")
    script.append("-- ✅ Estrutura N:N implementada com sucesso")
    
    # Salvar o script
    script_content = '\n'.join(script)
    
    with open('database/10_populacao_vendedores_completo.sql', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print(f"✅ Script gerado: database/10_populacao_vendedores_completo.sql")
    print(f"📊 {len(df_vendedores)} vendedores + {len(df_relacionamentos)} relacionamentos")
    print("🎯 Pronto para executar no Supabase!")
    
    return script_content

if __name__ == "__main__":
    gerar_script_populacao()