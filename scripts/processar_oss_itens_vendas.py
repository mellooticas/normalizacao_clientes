#!/usr/bin/env python3
"""
Script para processar dados OSS e extrair itens de vendas com client_id correto
"""

import pandas as pd
import json
import uuid
from pathlib import Path
from datetime import datetime
import numpy as np
import re

def normalizar_texto(texto):
    """Normaliza texto removendo acentos e caracteres especiais"""
    if pd.isna(texto):
        return None
    texto = str(texto).strip().upper()
    # Remove caracteres especiais mas mantém números e letras
    texto = re.sub(r'[^\w\s]', ' ', texto)
    # Remove espaços múltiplos
    texto = re.sub(r'\s+', ' ', texto)
    return texto.strip()

def extrair_itens_venda_de_linha(row, indice_linha):
    """Extrai todos os itens de venda de uma linha OSS"""
    itens = []
    
    # Mapear colunas de códigos e descrições (até 6 produtos por OS)
    produtos_cols = [
        ('Cod_trello', 'Descrição', 'Valor'),
        ('Cod17', 'Descrição18', 'Valor19'),
        ('Cod20', 'Descrição21', 'Valor22'),
        ('Cod23', 'Descrição24', 'Valor25'),
        ('Cod26', 'Descrição27', 'Valor28'),
    ]
    
    for i, (col_cod, col_desc, col_valor) in enumerate(produtos_cols):
        if col_cod in row and not pd.isna(row[col_cod]):
            codigo = str(row[col_cod]).strip()
            descricao = str(row[col_desc]) if col_desc in row and not pd.isna(row[col_desc]) else ""
            valor = 0.0
            
            try:
                if col_valor in row and not pd.isna(row[col_valor]):
                    valor = float(row[col_valor])
            except (ValueError, TypeError):
                valor = 0.0
            
            if codigo and codigo != "0" and codigo.lower() != "nan":
                item = {
                    'item_venda_uuid': str(uuid.uuid4()),
                    'venda_id': None,  # Será preenchido depois
                    'produto_codigo': codigo,
                    'produto_descricao': normalizar_texto(descricao),
                    'quantidade': 1,  # Assumindo quantidade 1 por item
                    'valor_unitario': valor,
                    'valor_total': valor,
                    'desconto': 0.0,
                    'observacoes': None,
                    'linha_origem': indice_linha + 1,
                    'ordem_produto': i + 1,
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
                itens.append(item)
    
    return itens

def processar_arquivo_oss(arquivo_path):
    """Processa um arquivo OSS e extrai itens de venda"""
    print(f"Processando {arquivo_path}...")
    
    try:
        df = pd.read_csv(arquivo_path, dtype=str, low_memory=False)
        print(f"  - {len(df)} registros encontrados")
        
        todos_itens = []
        stats = {
            'total_linhas': len(df),
            'linhas_com_itens': 0,
            'total_itens': 0
        }
        
        for idx, row in df.iterrows():
            itens_linha = extrair_itens_venda_de_linha(row, idx)
            
            if itens_linha:
                stats['linhas_com_itens'] += 1
                stats['total_itens'] += len(itens_linha)
                
                # Adicionar informações da venda para cada item
                for item in itens_linha:
                    item.update({
                        'cliente_id': row.get('cliente_id'),
                        'cliente_source': row.get('cliente_source'),
                        'cliente_nome': row.get('cliente_nome_normalizado'),
                        'loja_id': row.get('loja_id'),
                        'loja_nome': row.get('loja_nome'),
                        'vendedor_uuid': row.get('vendedor_uuid'),
                        'vendedor_nome': row.get('vendedor_nome_normalizado'),
                        'canal_captacao_uuid': row.get('canal_captacao_uuid'),
                        'canal_captacao_nome': row.get('canal_captacao_nome'),
                        'os_chave': row.get('os_chave'),
                        'numero_os': row.get('numero_os'),
                        'data_compra': row.get('data_compra'),
                        'total_venda': row.get('TOTAL'),
                        'arquivo_origem': arquivo_path.name
                    })
                
                todos_itens.extend(itens_linha)
        
        print(f"  - {stats['linhas_com_itens']} linhas com itens ({stats['total_itens']} itens total)")
        return todos_itens, stats
        
    except Exception as e:
        print(f"  - ERRO: {e}")
        return [], {'erro': str(e)}

def main():
    print("=== PROCESSAMENTO OSS - EXTRAÇÃO DE ITENS DE VENDAS ===")
    print(f"Início: {datetime.now()}")
    
    # Diretórios
    base_dir = Path("data/originais/oss/finais_postgresql_prontos")
    output_dir = Path("data/processados")
    output_dir.mkdir(exist_ok=True)
    
    # Encontrar arquivos com IDs de clientes
    arquivos_ids = list(base_dir.glob("oss_*_clientes_ids.csv"))
    
    if not arquivos_ids:
        print("Nenhum arquivo de clientes com IDs encontrado!")
        return
    
    print(f"Encontrados {len(arquivos_ids)} arquivos para processar:")
    for arquivo in arquivos_ids:
        print(f"  - {arquivo.name}")
    
    # Consolidar todos os itens
    todos_itens = []
    estatisticas_por_loja = {}
    
    for arquivo in arquivos_ids:
        itens, stats = processar_arquivo_oss(arquivo)
        loja_nome = arquivo.name.replace('oss_', '').replace('_clientes_ids.csv', '')
        
        todos_itens.extend(itens)
        estatisticas_por_loja[loja_nome] = stats
    
    print(f"\n=== CONSOLIDAÇÃO FINAL ===")
    print(f"Total de itens extraídos: {len(todos_itens)}")
    
    if not todos_itens:
        print("Nenhum item encontrado para processar!")
        return
    
    # Criar DataFrame final
    df_final = pd.DataFrame(todos_itens)
    
    # Estatísticas detalhadas
    print(f"\n=== ESTATÍSTICAS POR LOJA ===")
    total_geral = 0
    for loja, stats in estatisticas_por_loja.items():
        if 'total_itens' in stats:
            print(f"{loja}: {stats['total_itens']} itens de {stats['linhas_com_itens']} vendas")
            total_geral += stats['total_itens']
        else:
            print(f"{loja}: ERRO - {stats.get('erro', 'Desconhecido')}")
    
    print(f"\nTotal geral: {total_geral} itens")
    
    # Análise de produtos mais comuns
    if not df_final.empty:
        print(f"\n=== ANÁLISE DE PRODUTOS ===")
        produtos_count = df_final['produto_codigo'].value_counts().head(10)
        print("Top 10 códigos de produtos:")
        for codigo, count in produtos_count.items():
            descricao = df_final[df_final['produto_codigo'] == codigo]['produto_descricao'].iloc[0]
            print(f"  {codigo}: {count}x - {descricao}")
        
        # Análise de valores
        valores = df_final['valor_unitario'].astype(float)
        valor_total = valores.sum()
        print(f"\nValor total dos itens: R$ {valor_total:,.2f}")
        print(f"Valor médio por item: R$ {valores.mean():.2f}")
        print(f"Valor mediano: R$ {valores.median():.2f}")
    
    # Salvar resultados
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Arquivo principal
    arquivo_saida = output_dir / f"OSS_ITENS_VENDAS_COMPLETO_{timestamp}.csv"
    df_final.to_csv(arquivo_saida, index=False, encoding='utf-8')
    print(f"\nArquivo salvo: {arquivo_saida}")
    
    # Arquivo para importação Supabase (apenas campos necessários)
    colunas_supabase = [
        'item_venda_uuid', 'venda_id', 'produto_codigo', 'produto_descricao',
        'quantidade', 'valor_unitario', 'valor_total', 'desconto', 'observacoes',
        'created_at', 'updated_at'
    ]
    
    df_supabase = df_final[colunas_supabase].copy()
    arquivo_supabase = output_dir / f"OSS_ITENS_PARA_SUPABASE_{timestamp}.csv"
    df_supabase.to_csv(arquivo_supabase, index=False, encoding='utf-8')
    print(f"Arquivo Supabase: {arquivo_supabase}")
    
    # Relatório de mapeamento cliente_id
    arquivo_mapeamento = output_dir / f"OSS_MAPEAMENTO_CLIENTES_{timestamp}.json"
    mapeamento_clientes = df_final.groupby(['cliente_id', 'cliente_source', 'loja_nome']).agg({
        'cliente_nome': 'first',
        'item_venda_uuid': 'count'
    }).rename(columns={'item_venda_uuid': 'total_itens'}).to_dict('index')
    
    with open(arquivo_mapeamento, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': timestamp,
            'total_clientes_unicos': len(mapeamento_clientes),
            'total_itens': len(df_final),
            'estatisticas_por_loja': estatisticas_por_loja,
            'mapeamento_clientes': {str(k): v for k, v in mapeamento_clientes.items()}
        }, f, indent=2, ensure_ascii=False)
    
    print(f"Mapeamento salvo: {arquivo_mapeamento}")
    
    print(f"\n=== PROCESSAMENTO CONCLUÍDO ===")
    print(f"Fim: {datetime.now()}")

if __name__ == "__main__":
    main()