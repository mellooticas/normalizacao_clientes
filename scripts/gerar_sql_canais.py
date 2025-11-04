#!/usr/bin/env python3
"""
Script para gerar SQL de população dos canais de captação
"""

import json

def gerar_sql_canais_captacao():
    """Gera SQL para inserir canais de captação no banco"""
    
    # Carregar mapeamento final
    with open('mapeamento_canais_captacao_uuid_final.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    canais_uuid = data['canais_captacao_uuid']
    
    print("📝 GERANDO SQL PARA CANAIS DE CAPTAÇÃO")
    print("=" * 50)
    
    sql_content = [
        "-- ===============================================",
        "-- POPULAÇÃO DE CANAIS DE CAPTAÇÃO (COMO CONHECEU)",
        "-- ===============================================",
        f"-- Gerado automaticamente em: {data['data_geracao']}",
        f"-- Total de canais: {len(canais_uuid)}",
        "",
        "-- Limpar tabela existente (se houver)",
        "TRUNCATE TABLE marketing.canais_captacao CASCADE;",
        "",
        f"-- Inserir {len(canais_uuid)} canais de captação únicos",
        "INSERT INTO marketing.canais_captacao (",
        "    id,",
        "    nome,",
        "    codigo,", 
        "    descricao,",
        "    tipo_canal,",
        "    ativo,",
        "    criado_em",
        ") VALUES"
    ]
    
    # Gerar inserções
    inserções = []
    
    for nome_canal, uuid_canal in sorted(canais_uuid.items()):
        # Extrair código se houver
        if " - " in nome_canal:
            codigo = nome_canal.split(" - ")[0].strip()
            descricao = nome_canal.split(" - ", 1)[1].strip()
        else:
            codigo = nome_canal[:10].upper()
            descricao = nome_canal
        
        # Determinar tipo do canal
        if any(x in nome_canal.upper() for x in ['REDE', 'SOCIAL', 'WHATSAPP', 'GOOGLE']):
            tipo_canal = 'DIGITAL'
        elif any(x in nome_canal.upper() for x in ['INDICAÇÃO', 'AMIGO']):
            tipo_canal = 'INDICACAO'
        elif any(x in nome_canal.upper() for x in ['CLIENTE', 'ORÇAMENTO']):
            tipo_canal = 'ORGANICO'
        elif any(x in nome_canal.upper() for x in ['TELEMARKETING', 'ABORDAGEM', 'DIVULGADOR']):
            tipo_canal = 'ATIVO'
        elif 'SAÚDE' in nome_canal.upper():
            tipo_canal = 'MEDICO'
        else:
            tipo_canal = 'OUTROS'
        
        inserção = f"    ('{uuid_canal}', '{nome_canal}', '{codigo}', '{descricao}', '{tipo_canal}', true, NOW())"
        inserções.append(inserção)
    
    # Adicionar inserções ao SQL
    sql_content.extend([",\n".join(inserções) + ";"])
    
    # Adicionar estatísticas
    sql_content.extend([
        "",
        "-- ===============================================",
        "-- ESTATÍSTICAS DOS CANAIS",
        "-- ===============================================",
        "",
        f"-- Total de canais inseridos: {len(canais_uuid)}",
        "",
        "-- Verificar inserção:",
        "SELECT ",
        "    tipo_canal,",
        "    COUNT(*) as quantidade",
        "FROM marketing.canais_captacao",
        "GROUP BY tipo_canal",
        "ORDER BY quantidade DESC;",
        "",
        "-- Listar todos os canais:",
        "SELECT id, nome, codigo, tipo_canal, ativo",
        "FROM marketing.canais_captacao", 
        "ORDER BY nome;",
        ""
    ])
    
    # Salvar SQL
    sql_final = "\n".join(sql_content)
    
    with open('database/11_populacao_canais_captacao.sql', 'w', encoding='utf-8') as f:
        f.write(sql_final)
    
    print(f"✅ SQL gerado com {len(canais_uuid)} canais")
    print(f"💾 Salvo em: database/11_populacao_canais_captacao.sql")
    
    # Exibir resumo por tipo
    tipos = {}
    for nome_canal in canais_uuid.keys():
        if any(x in nome_canal.upper() for x in ['REDE', 'SOCIAL', 'WHATSAPP', 'GOOGLE']):
            tipo = 'DIGITAL'
        elif any(x in nome_canal.upper() for x in ['INDICAÇÃO', 'AMIGO']):
            tipo = 'INDICACAO'
        elif any(x in nome_canal.upper() for x in ['CLIENTE', 'ORÇAMENTO']):
            tipo = 'ORGANICO'
        elif any(x in nome_canal.upper() for x in ['TELEMARKETING', 'ABORDAGEM', 'DIVULGADOR']):
            tipo = 'ATIVO'
        elif 'SAÚDE' in nome_canal.upper():
            tipo = 'MEDICO'
        else:
            tipo = 'OUTROS'
        
        tipos[tipo] = tipos.get(tipo, 0) + 1
    
    print(f"\n📊 RESUMO POR TIPO:")
    for tipo, qtd in sorted(tipos.items()):
        print(f"   • {tipo}: {qtd} canais")

if __name__ == "__main__":
    gerar_sql_canais_captacao()