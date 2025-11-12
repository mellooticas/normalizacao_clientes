#!/usr/bin/env python3
"""
Gerador de SQL para estrutura completa de canais de aquisição com UUID
"""

import json

def gerar_sql_canais_aquisicao():
    """Gera SQL completo para tabela de canais de aquisição"""
    
    print("🏗️  GERANDO ESTRUTURA SQL PARA CANAIS DE AQUISIÇÃO")
    print("=" * 60)
    
    # Carregar mapeamento completo
    with open('mapeamento_canais_aquisicao_completo.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    canais = data['canais']
    
    sql_content = [
        "-- ===============================================",
        "-- ESTRUTURA COMPLETA DE CANAIS DE AQUISIÇÃO",
        "-- ===============================================",
        f"-- Gerado automaticamente em: {data['data_geracao']}",
        f"-- Total de canais: {len(canais)}",
        "",
        "-- Remover tabela anterior se existir",
        "DROP TABLE IF EXISTS marketing.canais_captacao CASCADE;",
        "DROP TABLE IF EXISTS marketing.canais_aquisicao CASCADE;",
        "",
        "-- Criar tabela com estrutura UUID",
        "CREATE TABLE marketing.canais_aquisicao (",
        "    id UUID NOT NULL DEFAULT gen_random_uuid(),",
        "    codigo VARCHAR(10) NOT NULL,",
        "    nome VARCHAR(100) NOT NULL,",
        "    descricao TEXT NULL,",
        "    categoria VARCHAR(50) NOT NULL,",
        "    ativo BOOLEAN NOT NULL DEFAULT true,",
        "    criado_em TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),",
        "    atualizado_em TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),",
        "    ",
        "    CONSTRAINT canais_aquisicao_pkey PRIMARY KEY (id),",
        "    CONSTRAINT canais_aquisicao_codigo_key UNIQUE (codigo)",
        ");",
        "",
        "-- Criar índices para performance",
        "CREATE INDEX idx_canais_aquisicao_codigo ON marketing.canais_aquisicao (codigo);",
        "CREATE INDEX idx_canais_aquisicao_categoria ON marketing.canais_aquisicao (categoria);",
        "CREATE INDEX idx_canais_aquisicao_ativo ON marketing.canais_aquisicao (ativo);",
        "CREATE INDEX idx_canais_aquisicao_nome ON marketing.canais_aquisicao (nome);",
        "",
        "-- Trigger para atualizar timestamp",
        "CREATE OR REPLACE FUNCTION update_updated_at_column()",
        "RETURNS TRIGGER AS $$",
        "BEGIN",
        "    NEW.atualizado_em = NOW();",
        "    RETURN NEW;",
        "END;",
        "$$ language 'plpgsql';",
        "",
        "CREATE TRIGGER update_canais_aquisicao_updated_at",
        "    BEFORE UPDATE ON marketing.canais_aquisicao",
        "    FOR EACH ROW",
        "    EXECUTE FUNCTION update_updated_at_column();",
        "",
        f"-- Inserir {len(canais)} canais de aquisição",
        "INSERT INTO marketing.canais_aquisicao (",
        "    id,",
        "    codigo,",
        "    nome,",
        "    descricao,",
        "    categoria,",
        "    ativo",
        ") VALUES"
    ]
    
    # Gerar inserções
    inserções = []
    
    for canal in sorted(canais, key=lambda x: x['codigo']):
        codigo = str(canal['codigo'])
        nome = canal['nome'].replace("'", "''")  # Escapar aspas simples
        descricao = nome  # Usar o nome como descrição por padrão
        categoria = canal['categoria']
        uuid_canal = canal['uuid']
        
        inserção = f"    ('{uuid_canal}', '{codigo}', '{nome}', '{descricao}', '{categoria}', true)"
        inserções.append(inserção)
    
    # Adicionar inserções ao SQL
    sql_content.extend([",\n".join(inserções) + ";"])
    
    # Adicionar estatísticas e consultas
    sql_content.extend([
        "",
        "-- ===============================================",
        "-- ESTATÍSTICAS E CONSULTAS",
        "-- ===============================================",
        "",
        f"-- Total de canais inseridos: {len(canais)}",
        "",
        "-- Verificar inserção por categoria:",
        "SELECT ",
        "    categoria,",
        "    COUNT(*) as quantidade,",
        "    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentual",
        "FROM marketing.canais_aquisicao",
        "GROUP BY categoria",
        "ORDER BY quantidade DESC;",
        "",
        "-- Listar todos os canais por categoria:",
        "SELECT ",
        "    categoria,",
        "    codigo,",
        "    nome,",
        "    ativo",
        "FROM marketing.canais_aquisicao",
        "ORDER BY categoria, CAST(codigo AS INTEGER);",
        "",
        "-- Top 10 canais mais baixos (provavelmente mais importantes):",
        "SELECT ",
        "    codigo,",
        "    nome,",
        "    categoria",
        "FROM marketing.canais_aquisicao",
        "ORDER BY CAST(codigo AS INTEGER)",
        "LIMIT 10;",
        "",
        "-- Contar por categoria:",
    ])
    
    # Adicionar contagem por categoria
    categorias = {}
    for canal in canais:
        cat = canal['categoria']
        categorias[cat] = categorias.get(cat, 0) + 1
    
    for categoria, qtd in sorted(categorias.items(), key=lambda x: x[1], reverse=True):
        sql_content.append(f"-- {categoria}: {qtd} canais")
    
    sql_content.extend([
        "",
        "-- ===============================================",
        "-- COMENTÁRIOS SOBRE AS CATEGORIAS",
        "-- ===============================================",
        "-- MEDICO: Médicos e profissionais de saúde que indicam pacientes",
        "-- DIVULGADOR: Pessoas físicas que fazem divulgação ativa",
        "-- DIGITAL: Canais online (redes sociais, site, WhatsApp, Google)",
        "-- RADIO: Estações de rádio e propaganda sonora",
        "-- CONVENIO: Planos de saúde e convênios médicos",
        "-- INDICACAO: Indicações de clientes, amigos e outras lojas",
        "-- MARKETING: Campanhas, outdoor, panfletos, placas",
        "-- FARMACIA: Parcerias com farmácias e drogarias",
        "-- INSTITUCIONAL: Órgãos públicos, sindicatos, SUS",
        "-- PARCERIA: Empresas parceiras (Magazine Luiza, supermercados)",
        "-- ABORDAGEM: Abordagem direta, telemarketing, passagem",
        "-- RELIGIOSO: Igrejas e instituições religiosas",
        "-- OUTROS: Demais canais não categorizados especificamente",
        ""
    ])
    
    # Salvar SQL
    sql_final = "\n".join(sql_content)
    
    with open('database/12_estrutura_canais_aquisicao.sql', 'w', encoding='utf-8') as f:
        f.write(sql_final)
    
    print(f"✅ SQL gerado com {len(canais)} canais")
    print(f"💾 Salvo em: database/12_estrutura_canais_aquisicao.sql")
    
    # Exibir estatísticas por categoria
    print(f"\n📊 DISTRIBUIÇÃO POR CATEGORIA:")
    for categoria, qtd in sorted(categorias.items(), key=lambda x: x[1], reverse=True):
        perc = (qtd / len(canais)) * 100
        print(f"   • {categoria:15}: {qtd:3d} canais ({perc:5.1f}%)")
    
    print(f"\n🎯 PRÓXIMOS PASSOS:")
    print(f"   1. Executar SQL no Supabase:")
    print(f"      database/12_estrutura_canais_aquisicao.sql")
    print(f"   2. Mapear canais encontrados nos CSVs")
    print(f"   3. Criar relacionamento com as OS")
    print(f"   4. Validar integridade dos dados")
    
    return sql_final

if __name__ == "__main__":
    gerar_sql_canais_aquisicao()