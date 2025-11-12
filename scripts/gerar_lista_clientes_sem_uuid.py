#!/usr/bin/env python3
"""
Script para gerar CSV com clientes sem UUID
Lista todos os clientes que precisam ser resolvidos
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

def gerar_lista_clientes_sem_uuid():
    """Gera CSV com clientes que não têm UUID"""
    
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    
    print("=== GERANDO LISTA DE CLIENTES SEM UUID ===")
    
    # 1. Carrega dados de vendas definitivos
    vendas_df = pd.read_csv(base_dir / "data" / "vendas_para_importar" / "vendas_definitivo.csv")
    print(f"Total de vendas: {len(vendas_df)}")
    
    # 2. Filtra vendas sem cliente UUID
    vendas_sem_uuid = vendas_df[vendas_df['cliente_id'].isna()]
    print(f"Vendas sem cliente UUID: {len(vendas_sem_uuid)}")
    
    if len(vendas_sem_uuid) == 0:
        print("✅ Todos os clientes já têm UUID!")
        return
    
    # 3. Cria lista única de clientes sem UUID
    clientes_sem_uuid = vendas_sem_uuid[['nome_cliente_temp']].drop_duplicates()
    clientes_sem_uuid = clientes_sem_uuid.dropna()
    
    print(f"Clientes únicos sem UUID: {len(clientes_sem_uuid)}")
    
    # 4. Adiciona estatísticas por cliente
    estatisticas_clientes = []
    
    for _, row in clientes_sem_uuid.iterrows():
        nome_cliente = row['nome_cliente_temp']
        
        # Busca todas as vendas deste cliente
        vendas_cliente = vendas_sem_uuid[vendas_sem_uuid['nome_cliente_temp'] == nome_cliente]
        
        if len(vendas_cliente) > 0:
            total_vendas = len(vendas_cliente)
            valor_total = vendas_cliente['valor_total'].sum()
            valor_entrada = vendas_cliente['valor_entrada'].sum()
            primeira_venda = vendas_cliente['data_venda'].min()
            ultima_venda = vendas_cliente['data_venda'].max()
            
            # Lojas onde comprou
            lojas = vendas_cliente['loja_id'].unique()
            nomes_lojas = []
            mapeamento_lojas = {
                '52f92716-d2ba-441a-ac3c-94bdfabd9722': 'MAUA',
                '9a22ccf1-36fe-4b9f-9391-ca31433dc31e': 'SUZANO',
                'aa7a5646-f7d6-4239-831c-6602fbabb10a': 'SUZANO2',
                'da3978c9-bba2-431a-91b7-970a406d3acf': 'PERUS',
                '4e94f51f-3b0f-4e0f-ba73-64982b870f2c': 'RIO_PEQUENO',
                '1c35e0ad-3066-441e-85cc-44c0eb9b3ab4': 'SAO_MATEUS'
            }
            
            for loja_uuid in lojas:
                nome_loja = mapeamento_lojas.get(loja_uuid, 'DESCONHECIDA')
                nomes_lojas.append(nome_loja)
            
            lojas_str = ', '.join(nomes_lojas)
            
            # Números das OS
            numeros_os = vendas_cliente['numero_venda'].tolist()
            numeros_os_limpos = []
            for os in numeros_os:
                try:
                    if pd.notna(os) and str(os).strip():
                        numeros_os_limpos.append(str(int(float(os))))
                except (ValueError, TypeError):
                    continue
            numeros_os_str = ', '.join(numeros_os_limpos)
            
            estatisticas_clientes.append({
                'nome_cliente': nome_cliente,
                'total_vendas': total_vendas,
                'valor_total': valor_total,
                'valor_entrada': valor_entrada,
                'primeira_venda': primeira_venda,
                'ultima_venda': ultima_venda,
                'lojas': lojas_str,
                'numeros_os': numeros_os_str,
                'status': 'PENDENTE_UUID',
                'observacoes': f'{total_vendas} compras, R$ {valor_total:.2f} total',
                'prioridade': 'ALTA' if valor_total > 1000 or total_vendas > 2 else 'NORMAL'
            })
    
    # 5. Cria DataFrame com estatísticas
    df_clientes_sem_uuid = pd.DataFrame(estatisticas_clientes)
    
    # Ordena por valor total (clientes mais importantes primeiro)
    df_clientes_sem_uuid = df_clientes_sem_uuid.sort_values('valor_total', ascending=False)
    
    # 6. Estatísticas gerais
    print(f"\n=== ESTATÍSTICAS DOS CLIENTES SEM UUID ===")
    print(f"Total de clientes únicos: {len(df_clientes_sem_uuid)}")
    print(f"Valor total perdido: R$ {df_clientes_sem_uuid['valor_total'].sum():,.2f}")
    print(f"Valor entrada perdido: R$ {df_clientes_sem_uuid['valor_entrada'].sum():,.2f}")
    
    # Clientes por prioridade
    alta_prioridade = df_clientes_sem_uuid[df_clientes_sem_uuid['prioridade'] == 'ALTA']
    print(f"Clientes alta prioridade: {len(alta_prioridade)} (>R$ 1000 ou >2 compras)")
    print(f"Clientes prioridade normal: {len(df_clientes_sem_uuid) - len(alta_prioridade)}")
    
    # Top 10 clientes por valor
    print(f"\n=== TOP 10 CLIENTES POR VALOR ===")
    for _, cliente in df_clientes_sem_uuid.head(10).iterrows():
        print(f"  {cliente['nome_cliente']}: R$ {cliente['valor_total']:.2f} ({cliente['total_vendas']} vendas)")
    
    # 7. Salva CSV
    arquivo_saida = base_dir / "data" / "clientes" / "clientes_sem_uuid_para_resolver.csv"
    df_clientes_sem_uuid.to_csv(arquivo_saida, index=False)
    
    print(f"\n=== ARQUIVO GERADO ===")
    print(f"Arquivo: {arquivo_saida}")
    print(f"Total de registros: {len(df_clientes_sem_uuid)}")
    
    # 8. Cria também versão simplificada apenas com nomes
    df_nomes_simples = df_clientes_sem_uuid[['nome_cliente', 'total_vendas', 'valor_total', 'prioridade']].copy()
    arquivo_simples = base_dir / "data" / "clientes" / "nomes_clientes_sem_uuid.csv"
    df_nomes_simples.to_csv(arquivo_simples, index=False)
    
    print(f"Arquivo simplificado: {arquivo_simples}")
    
    # 9. Resumo para importação
    print(f"\n=== RESUMO PARA RESOLUÇÃO ===")
    print(f"📊 {len(df_clientes_sem_uuid)} clientes únicos precisam de UUID")
    print(f"💰 R$ {df_clientes_sem_uuid['valor_total'].sum():,.2f} em vendas sem rastreamento")
    print(f"🔥 {len(alta_prioridade)} clientes de alta prioridade")
    print(f"📈 {df_clientes_sem_uuid['total_vendas'].sum()} vendas afetadas")
    
    print(f"\n=== PRÓXIMOS PASSOS ===")
    print("1. Abrir arquivo clientes_sem_uuid_para_resolver.csv")
    print("2. Começar pelos clientes de ALTA prioridade")
    print("3. Buscar/criar UUIDs no sistema de clientes")
    print("4. Atualizar tabela vendas com: UPDATE vendas.vendas SET cliente_id = 'UUID' WHERE nome_cliente_temp = 'NOME'")
    
    return df_clientes_sem_uuid

if __name__ == "__main__":
    resultado = gerar_lista_clientes_sem_uuid()
    print("\n📋 LISTA DE CLIENTES SEM UUID GERADA!")
    print("✅ Pronta para resolução manual!")