#!/usr/bin/env python3
"""
Script helper para gerar comandos SQL de atualização
Facilita o processo de atualização de UUIDs cliente por cliente
"""

import pandas as pd
from pathlib import Path

def gerar_comandos_atualizacao():
    """Gera comandos SQL prontos para executar"""
    
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    
    print("=== GERADOR DE COMANDOS SQL PARA ATUALIZAÇÃO ===")
    
    # 1. Carrega dados de alta prioridade
    arquivo_alta_prio = base_dir / "data" / "clientes" / "clientes_alta_prioridade_uma_os.csv"
    df = pd.read_csv(arquivo_alta_prio)
    
    print(f"Registros de alta prioridade: {len(df)}")
    
    # 2. Agrupa por cliente para facilitar
    clientes_grupo = df.groupby('nome_cliente').agg({
        'numero_os': list,
        'valor_total': 'sum',
        'total_os': 'first',
        'loja_nome': lambda x: ', '.join(x.unique())
    }).reset_index()
    
    clientes_grupo = clientes_grupo.sort_values('valor_total', ascending=False)
    
    print(f"Clientes únicos de alta prioridade: {len(clientes_grupo)}")
    
    # 3. Gera arquivo com comandos SQL
    comandos_sql = []
    
    comandos_sql.append("-- COMANDOS SQL PARA ATUALIZAÇÃO DE CLIENTES SEM UUID")
    comandos_sql.append("-- Execute um cliente por vez, após buscar/criar o UUID no sistema")
    comandos_sql.append("-- Formato: [CLIENTE] - [VALOR] - [OS_NUMBERS]")
    comandos_sql.append("")
    
    for idx, row in clientes_grupo.iterrows():
        nome_cliente = row['nome_cliente']
        valor_total = row['valor_total']
        numeros_os = row['numero_os']
        total_os = row['total_os']
        lojas = row['loja_nome']
        
        comandos_sql.append(f"-- {idx + 1}. CLIENTE: {nome_cliente}")
        comandos_sql.append(f"--    Valor total: R$ {valor_total:.2f}")
        comandos_sql.append(f"--    Total OS: {total_os}")
        comandos_sql.append(f"--    Lojas: {lojas}")
        comandos_sql.append(f"--    OS Numbers: {', '.join(map(str, numeros_os))}")
        comandos_sql.append("")
        
        # Comandos SQL para cada OS
        for os_num in numeros_os:
            comandos_sql.append(f"-- Atualizar OS {os_num}")
            comandos_sql.append(f"UPDATE vendas.vendas")
            comandos_sql.append(f"SET cliente_id = 'UUID_AQUI_{nome_cliente.replace(' ', '_').replace(',', '').replace('(', '').replace(')', '')}'")
            comandos_sql.append(f"WHERE numero_venda = '{os_num}';")
            comandos_sql.append("")
        
        # Verificação
        comandos_sql.append(f"-- Verificar atualização do cliente {nome_cliente}")
        os_list = "', '".join(map(str, numeros_os))
        comandos_sql.append(f"SELECT numero_venda, cliente_id, nome_cliente_temp, valor_total")
        comandos_sql.append(f"FROM vendas.vendas")
        comandos_sql.append(f"WHERE numero_venda IN ('{os_list}');")
        comandos_sql.append("")
        comandos_sql.append("-- " + "="*80)
        comandos_sql.append("")
    
    # 4. Salva arquivo SQL
    arquivo_sql = base_dir / "data" / "clientes" / "comandos_atualizacao_clientes.sql"
    with open(arquivo_sql, 'w', encoding='utf-8') as f:
        f.write('\n'.join(comandos_sql))
    
    # 5. Cria também arquivo de progresso
    df_progresso = clientes_grupo.copy()
    df_progresso['uuid_cliente'] = ''
    df_progresso['status'] = 'PENDENTE'
    df_progresso['data_resolucao'] = ''
    df_progresso['observacoes_resolucao'] = ''
    
    arquivo_progresso = base_dir / "data" / "clientes" / "progresso_resolucao_clientes.csv"
    df_progresso.to_csv(arquivo_progresso, index=False)
    
    # 6. Primeiros 5 clientes para exemplo
    print(f"\n=== TOP 5 CLIENTES PARA COMEÇAR ===")
    for idx, row in clientes_grupo.head(5).iterrows():
        nome_cliente = row['nome_cliente']
        valor_total = row['valor_total']
        numeros_os = row['numero_os']
        print(f"{idx + 1}. {nome_cliente}")
        print(f"   💰 R$ {valor_total:.2f}")
        print(f"   📋 OS: {', '.join(map(str, numeros_os))}")
        print()
    
    print(f"=== ARQUIVOS GERADOS ===")
    print(f"1. Comandos SQL: {arquivo_sql}")
    print(f"   📜 Comandos prontos para executar")
    
    print(f"2. Progresso: {arquivo_progresso}")
    print(f"   📊 Para acompanhar resolução")
    
    print(f"\n=== PROCESSO RECOMENDADO ===")
    print("1. Abrir arquivo 'comandos_atualizacao_clientes.sql'")
    print("2. Para cada cliente:")
    print("   a) Buscar cliente no sistema pelo nome")
    print("   b) Se não existir, criar novo cliente")
    print("   c) Copiar UUID do cliente")
    print("   d) Substituir 'UUID_AQUI_...' pelo UUID real")
    print("   e) Executar comandos UPDATE")
    print("   f) Executar comando SELECT para verificar")
    print("   g) Atualizar planilha de progresso")
    
    print(f"\n=== MONITORAMENTO ===")
    print("-- Verificar progresso geral")
    print("SELECT")
    print("    COUNT(*) as total_vendas,")
    print("    COUNT(cliente_id) as com_uuid,")
    print("    COUNT(*) - COUNT(cliente_id) as sem_uuid,")
    print("    ROUND((COUNT(cliente_id)::float / COUNT(*)) * 100, 2) as percentual")
    print("FROM vendas.vendas;")
    
    return clientes_grupo

if __name__ == "__main__":
    clientes = gerar_comandos_atualizacao()
    print("\n🛠️ COMANDOS SQL GERADOS!")
    print("✅ Prontos para atualização individual!")