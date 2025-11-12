#!/usr/bin/env python3
"""
Script para normalizar clientes sem UUID
Cada linha terá apenas 1 número de OS, dividindo valores proporcionalmente
"""

import pandas as pd
from pathlib import Path
import re

def normalizar_clientes_uma_os_por_linha():
    """Normaliza dados para ter uma OS por linha"""
    
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    
    print("=== NORMALIZANDO CLIENTES - UMA OS POR LINHA ===")
    
    # 1. Carrega dados de vendas definitivos
    vendas_df = pd.read_csv(base_dir / "data" / "vendas_para_importar" / "vendas_definitivo.csv")
    print(f"Total de vendas: {len(vendas_df)}")
    
    # 2. Filtra vendas sem cliente UUID
    vendas_sem_uuid = vendas_df[vendas_df['cliente_id'].isna()].copy()
    print(f"Vendas sem cliente UUID: {len(vendas_sem_uuid)}")
    
    if len(vendas_sem_uuid) == 0:
        print("✅ Todos os clientes já têm UUID!")
        return
    
    # 3. Prepara lista normalizada
    registros_normalizados = []
    
    # Mapeamento de lojas
    mapeamento_lojas = {
        '52f92716-d2ba-441a-ac3c-94bdfabd9722': 'MAUA',
        '9a22ccf1-36fe-4b9f-9391-ca31433dc31e': 'SUZANO',
        'aa7a5646-f7d6-4239-831c-6602fbabb10a': 'SUZANO2',
        'da3978c9-bba2-431a-91b7-970a406d3acf': 'PERUS',
        '4e94f51f-3b0f-4e0f-ba73-64982b870f2c': 'RIO_PEQUENO',
        '1c35e0ad-3066-441e-85cc-44c0eb9b3ab4': 'SAO_MATEUS'
    }
    
    print(f"\n=== PROCESSANDO REGISTROS ===")
    
    # 4. Processa cada venda
    for idx, row in vendas_sem_uuid.iterrows():
        nome_cliente = row['nome_cliente_temp']
        numero_os = row['numero_venda']
        valor_total = row['valor_total']
        valor_entrada = row['valor_entrada']
        data_venda = row['data_venda']
        loja_uuid = row['loja_id']
        loja_nome = mapeamento_lojas.get(loja_uuid, 'DESCONHECIDA')
        
        # Converte numero_os para string e limpa
        try:
            if pd.notna(numero_os):
                numero_os_str = str(int(float(numero_os)))
            else:
                numero_os_str = "SEM_OS"
        except (ValueError, TypeError):
            numero_os_str = "INVALIDO"
        
        # Cria registro individual por OS
        registro = {
            'nome_cliente': nome_cliente,
            'numero_os': numero_os_str,
            'valor_total': float(valor_total) if pd.notna(valor_total) else 0.0,
            'valor_entrada': float(valor_entrada) if pd.notna(valor_entrada) else 0.0,
            'data_venda': data_venda,
            'loja_nome': loja_nome,
            'loja_uuid': loja_uuid,
            'status': 'PENDENTE_UUID',
            'observacoes': f'OS {numero_os_str} - R$ {valor_total:.2f}',
            'prioridade': 'ALTA' if (pd.notna(valor_total) and float(valor_total) > 1000) else 'NORMAL'
        }
        
        registros_normalizados.append(registro)
    
    # 5. Cria DataFrame normalizado
    df_normalizado = pd.DataFrame(registros_normalizados)
    print(f"Registros normalizados: {len(df_normalizado)}")
    
    # 6. Agrupa por cliente para estatísticas
    print(f"\n=== CALCULANDO ESTATÍSTICAS POR CLIENTE ===")
    
    estatisticas_clientes = df_normalizado.groupby('nome_cliente').agg({
        'numero_os': 'count',  # total de OS
        'valor_total': 'sum',   # valor total
        'valor_entrada': 'sum', # entrada total
        'data_venda': ['min', 'max'],  # primeira e última venda
        'loja_nome': lambda x: ', '.join(x.unique()),  # lojas
        'prioridade': lambda x: 'ALTA' if 'ALTA' in x.values else 'NORMAL'
    }).reset_index()
    
    # Achata colunas
    estatisticas_clientes.columns = [
        'nome_cliente', 'total_os', 'valor_total_cliente', 'valor_entrada_cliente',
        'primeira_venda', 'ultima_venda', 'lojas_cliente', 'prioridade_cliente'
    ]
    
    # 7. Merge com dados normalizados
    df_final = df_normalizado.merge(
        estatisticas_clientes[['nome_cliente', 'total_os', 'valor_total_cliente', 'prioridade_cliente']], 
        on='nome_cliente'
    )
    
    # 8. Ordena por prioridade e valor
    df_final = df_final.sort_values(['prioridade_cliente', 'valor_total_cliente', 'valor_total'], 
                                   ascending=[False, False, False])
    
    # 9. Estatísticas finais
    print(f"\n=== ESTATÍSTICAS FINAIS ===")
    print(f"Total de registros (uma OS por linha): {len(df_final)}")
    
    clientes_unicos = df_final['nome_cliente'].nunique()
    print(f"Clientes únicos: {clientes_unicos}")
    
    valor_total_geral = df_final['valor_total'].sum()
    valor_entrada_geral = df_final['valor_entrada'].sum()
    print(f"Valor total: R$ {valor_total_geral:,.2f}")
    print(f"Valor entrada: R$ {valor_entrada_geral:,.2f}")
    
    # Prioridades
    alta_prioridade = df_final[df_final['prioridade_cliente'] == 'ALTA']
    print(f"Registros alta prioridade: {len(alta_prioridade)}")
    print(f"Registros prioridade normal: {len(df_final) - len(alta_prioridade)}")
    
    # 10. Top clientes
    print(f"\n=== TOP 10 CLIENTES (por valor total) ===")
    top_clientes = estatisticas_clientes.sort_values('valor_total_cliente', ascending=False).head(10)
    for _, cliente in top_clientes.iterrows():
        print(f"  {cliente['nome_cliente']}: R$ {cliente['valor_total_cliente']:.2f} ({cliente['total_os']} OS)")
    
    # 11. Salva arquivos
    
    # Arquivo detalhado (uma OS por linha)
    arquivo_detalhado = base_dir / "data" / "clientes" / "clientes_sem_uuid_uma_os_por_linha.csv"
    df_final.to_csv(arquivo_detalhado, index=False)
    
    # Arquivo apenas clientes alta prioridade
    arquivo_alta_prioridade = base_dir / "data" / "clientes" / "clientes_alta_prioridade_uma_os.csv"
    df_alta_prio = df_final[df_final['prioridade_cliente'] == 'ALTA']
    df_alta_prio.to_csv(arquivo_alta_prioridade, index=False)
    
    # Arquivo resumo por cliente
    arquivo_resumo = base_dir / "data" / "clientes" / "resumo_clientes_sem_uuid.csv"
    estatisticas_clientes.to_csv(arquivo_resumo, index=False)
    
    print(f"\n=== ARQUIVOS GERADOS ===")
    print(f"1. Detalhado (uma OS por linha): {arquivo_detalhado}")
    print(f"   📊 {len(df_final)} registros")
    
    print(f"2. Alta prioridade: {arquivo_alta_prioridade}")
    print(f"   🔥 {len(df_alta_prio)} registros de alta prioridade")
    
    print(f"3. Resumo por cliente: {arquivo_resumo}")
    print(f"   👥 {len(estatisticas_clientes)} clientes únicos")
    
    # 12. Instrções de uso
    print(f"\n=== COMO USAR ===")
    print("1. Abrir 'clientes_alta_prioridade_uma_os.csv' para começar")
    print("2. Para cada linha (uma OS):")
    print("   - Buscar cliente no sistema pelo nome")
    print("   - Se não existir, criar novo cliente")
    print("   - Anotar UUID do cliente")
    print("   - Executar: UPDATE vendas.vendas SET cliente_id = 'UUID' WHERE numero_venda = 'NUMERO_OS'")
    print("3. Verificar: SELECT * FROM vendas.vendas WHERE numero_venda = 'NUMERO_OS'")
    
    print(f"\n=== EXEMPLO DE ATUALIZAÇÃO ===")
    if len(df_alta_prio) > 0:
        exemplo = df_alta_prio.iloc[0]
        print(f"Cliente: {exemplo['nome_cliente']}")
        print(f"OS: {exemplo['numero_os']}")
        print(f"Valor: R$ {exemplo['valor_total']:.2f}")
        print(f"SQL: UPDATE vendas.vendas SET cliente_id = 'UUID_AQUI' WHERE numero_venda = '{exemplo['numero_os']}';")
    
    return df_final, estatisticas_clientes

if __name__ == "__main__":
    registros, clientes = normalizar_clientes_uma_os_por_linha()
    print("\n🎯 NORMALIZAÇÃO CONCLUÍDA!")
    print("✅ Uma OS por linha, pronto para resolução individual!")