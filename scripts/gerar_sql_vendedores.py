#!/usr/bin/env python3
"""
Script para gerar SQLs de população das tabelas reestruturadas
Usa os dados dos arquivos Excel/CSV já processados
"""

import pandas as pd
import json
from pathlib import Path

def gerar_sql_vendedores_unicos():
    """Gera SQL para inserir vendedores únicos"""
    
    # Ler dados dos vendedores únicos
    df_vendedores = pd.read_csv('VENDEDORES_UNICOS_UUID.csv')
    
    sql_statements = []
    sql_statements.append("-- =============================================")
    sql_statements.append("-- INSERIR VENDEDORES ÚNICOS")
    sql_statements.append("-- =============================================")
    sql_statements.append("")
    sql_statements.append("INSERT INTO core.vendedores (id, nome, nome_padronizado, nome_exibicao, ativo, created_at, updated_at) VALUES")
    
    insert_values = []
    
    for _, row in df_vendedores.iterrows():
        uuid = row['uuid']
        nome_pad = row['nome_padronizado']
        nome_exib = nome_pad.title()  # Capitalizar para exibição
        
        insert_values.append(
            f"('{uuid}', '{nome_pad}', '{nome_pad}', '{nome_exib}', true, NOW(), NOW())"
        )
    
    sql_statements.append(',\n'.join(insert_values) + ';')
    sql_statements.append("")
    
    return '\n'.join(sql_statements)

def gerar_sql_vendedores_lojas():
    """Gera SQL para inserir relacionamentos vendedor-loja"""
    
    # Ler dados dos relacionamentos
    df_rel = pd.read_csv('VENDEDORES_LOJAS_RELACIONAMENTO.csv')
    
    # Mapeamento de lojas
    lojas_mapping = {
        "Mauá": "9a22ccf1-36fe-4b9f-9391-ca31433dc31e",
        "Perus": "da3978c9-bba2-431a-91b7-970a406d3acf",
        "Rio Pequeno": "4e94f51f-3b0f-4e0f-ba73-64982b870f2c",
        "São Mateus": "1c35e0ad-3066-441e-85cc-44c0eb9b3ab4",
        "Suzano": "52f92716-d2ba-441a-ac3c-94bdfabd9722",
        "Suzano 2": "aa7a5646-f7d6-4239-831c-6602fbabb10a"
    }
    
    sql_statements = []
    sql_statements.append("-- =============================================")
    sql_statements.append("-- INSERIR RELACIONAMENTOS VENDEDOR-LOJA")
    sql_statements.append("-- =============================================")
    sql_statements.append("")
    
    # Agrupar por loja
    for loja_nome, loja_uuid in lojas_mapping.items():
        # Filtrar registros desta loja
        registros_loja = df_rel[df_rel['loja_nome'] == loja_nome]
        
        if len(registros_loja) > 0:
            sql_statements.append(f"-- {loja_nome} ({loja_uuid})")
            sql_statements.append("INSERT INTO core.vendedores_lojas (vendedor_id, loja_id, codigo_vendedor_sistema, ativo, data_inicio) VALUES")
            
            insert_values = []
            
            for _, row in registros_loja.iterrows():
                vendedor_uuid = row['vendedor_uuid']
                codigo_sistema = row['codigo_vendedor_sistema'] if pd.notna(row['codigo_vendedor_sistema']) else ''
                
                insert_values.append(
                    f"('{vendedor_uuid}', '{loja_uuid}', '{codigo_sistema}', true, '2023-01-01')"
                )
            
            sql_statements.append(',\n'.join(insert_values) + ';')
            sql_statements.append("")
    
    return '\n'.join(sql_statements)

def gerar_sql_completo():
    """Gera script SQL completo"""
    
    sql_parts = []
    
    # Cabeçalho
    sql_parts.append("-- =============================================")
    sql_parts.append("-- POPULAÇÃO COMPLETA DAS TABELAS REESTRUTURADAS")
    sql_parts.append("-- Gerado automaticamente dos dados processados")
    sql_parts.append(f"-- Data: 2025-10-29")
    sql_parts.append("-- =============================================")
    sql_parts.append("")
    
    # Limpeza inicial
    sql_parts.append("-- Limpar tabelas")
    sql_parts.append("TRUNCATE TABLE core.vendedores_lojas CASCADE;")
    sql_parts.append("TRUNCATE TABLE core.vendedores CASCADE;")
    sql_parts.append("")
    
    # Vendedores únicos
    sql_parts.append(gerar_sql_vendedores_unicos())
    
    # Relacionamentos
    sql_parts.append(gerar_sql_vendedores_lojas())
    
    # Verificações finais
    sql_parts.append("-- =============================================")
    sql_parts.append("-- VERIFICAÇÕES FINAIS")
    sql_parts.append("-- =============================================")
    sql_parts.append("")
    sql_parts.append("-- Contar registros")
    sql_parts.append("SELECT 'vendedores' as tabela, COUNT(*) as total FROM core.vendedores")
    sql_parts.append("UNION ALL")
    sql_parts.append("SELECT 'vendedores_lojas' as tabela, COUNT(*) as total FROM core.vendedores_lojas;")
    sql_parts.append("")
    sql_parts.append("-- Distribuição por loja")
    sql_parts.append("SELECT ")
    sql_parts.append("    l.nome as loja_nome,")
    sql_parts.append("    COUNT(vl.vendedor_id) as total_vendedores")
    sql_parts.append("FROM core.lojas l")
    sql_parts.append("LEFT JOIN core.vendedores_lojas vl ON l.id = vl.loja_id")
    sql_parts.append("GROUP BY l.id, l.nome")
    sql_parts.append("ORDER BY l.nome;")
    sql_parts.append("")
    sql_parts.append("-- Vendedores sem loja")
    sql_parts.append("SELECT ")
    sql_parts.append("    v.nome_padronizado")
    sql_parts.append("FROM core.vendedores v")
    sql_parts.append("LEFT JOIN core.vendedores_lojas vl ON v.id = vl.vendedor_id")
    sql_parts.append("WHERE vl.vendedor_id IS NULL")
    sql_parts.append("ORDER BY v.nome_padronizado;")
    
    return '\n'.join(sql_parts)

def gerar_resumo_dados():
    """Gera resumo dos dados para verificação"""
    
    print("📊 RESUMO DOS DADOS PARA POPULAÇÃO:")
    print("=" * 50)
    
    # Vendedores únicos
    df_vendedores = pd.read_csv('VENDEDORES_UNICOS_UUID.csv')
    print(f"✅ Vendedores únicos: {len(df_vendedores)}")
    
    # Relacionamentos
    df_rel = pd.read_csv('VENDEDORES_LOJAS_RELACIONAMENTO.csv')
    print(f"✅ Relacionamentos vendedor-loja: {len(df_rel)}")
    
    # Distribuição por loja
    print("\n📍 Distribuição por loja:")
    dist = df_rel['loja_nome'].value_counts()
    for loja, count in dist.items():
        print(f"   • {loja}: {count} vendedores")
    
    # Vendedores sem loja
    df_sem_loja = pd.read_csv('VENDEDORES_SEM_LOJA_PARA_ATRIBUIR.csv')
    print(f"\n❓ Vendedores sem loja: {len(df_sem_loja)}")
    
    # Com observações
    com_obs = df_sem_loja[df_sem_loja['observacoes'].notna() & (df_sem_loja['observacoes'] != '')]
    print(f"   • Com observações (identificados): {len(com_obs)}")
    print(f"   • Sem identificação: {len(df_sem_loja) - len(com_obs)}")

def main():
    """Função principal"""
    print("🗄️ GERANDO SQLs PARA POPULAÇÃO DAS TABELAS")
    print("=" * 60)
    
    # Verificar se arquivos existem
    arquivos_necessarios = [
        'VENDEDORES_UNICOS_UUID.csv',
        'VENDEDORES_LOJAS_RELACIONAMENTO.csv',
        'VENDEDORES_SEM_LOJA_PARA_ATRIBUIR.csv'
    ]
    
    for arquivo in arquivos_necessarios:
        if not Path(arquivo).exists():
            print(f"❌ Arquivo necessário não encontrado: {arquivo}")
            return
    
    # Gerar resumo
    gerar_resumo_dados()
    print()
    
    # Gerar SQL completo
    print("🔧 Gerando script SQL...")
    sql_completo = gerar_sql_completo()
    
    # Salvar arquivo
    sql_path = "database/11_populacao_vendedores_completa.sql"
    Path("database").mkdir(exist_ok=True)
    
    with open(sql_path, 'w', encoding='utf-8') as f:
        f.write(sql_completo)
    
    print(f"💾 Script SQL gerado: {sql_path}")
    print()
    
    print("📋 PRÓXIMOS PASSOS:")
    print("1. Revisar o script SQL gerado")
    print("2. Executar a reestruturação (09_reestruturacao_vendedores.sql)")
    print("3. Executar a população (11_populacao_vendedores_completa.sql)")
    print("4. Atribuir lojas aos vendedores sem loja")
    print("5. Atualizar dados de vendas com novos UUIDs")

if __name__ == "__main__":
    main()