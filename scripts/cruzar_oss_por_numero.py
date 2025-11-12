#!/usr/bin/env python3
"""
Script para cruzar itens OSS com vendas existentes usando numero_venda/numero_os
"""

import pandas as pd
import json
import uuid
from pathlib import Path
from datetime import datetime

def normalizar_numero(valor):
    """Normaliza número para comparação"""
    if pd.isna(valor):
        return None
    
    try:
        # Remove .0 e converte para float para comparação
        numero = str(valor).replace('.0', '').strip()
        if numero.isdigit():
            return float(numero)
        return float(valor)
    except (ValueError, TypeError):
        return None

def main():
    print("=== CRUZAMENTO OSS COM VENDAS POR NÚMERO ===")
    print(f"Início: {datetime.now()}")
    
    # Carregar vendas existentes
    print("\n1. Carregando dados...")
    vendas_file = "data/vendas_para_importar/vendas_TODAS_RENUMERADAS_SEM_DUPLICATAS.csv"
    vendas_df = pd.read_csv(vendas_file, dtype=str, low_memory=False)
    print(f"  - {len(vendas_df)} vendas carregadas")
    
    # Carregar itens OSS
    itens_files = list(Path("data/processados").glob("OSS_ITENS_VENDAS_COMPLETO_*.csv"))
    itens_file = sorted(itens_files)[-1]
    itens_df = pd.read_csv(itens_file, dtype=str, low_memory=False)
    print(f"  - {len(itens_df)} itens OSS carregados")
    
    # Criar índices para cruzamento rápido
    print("\n2. Preparando índices para cruzamento...")
    
    # Normalizar números nas vendas
    vendas_df['numero_venda_norm'] = vendas_df['numero_venda'].apply(normalizar_numero)
    
    # Remover duplicatas mantendo a primeira ocorrência
    vendas_unicas = vendas_df.dropna(subset=['numero_venda_norm']).drop_duplicates(subset=['numero_venda_norm'])
    vendas_por_numero = vendas_unicas.set_index('numero_venda_norm').to_dict('index')
    
    print(f"  - {len(vendas_df)} vendas totais")
    print(f"  - {len(vendas_unicas)} vendas com números únicos")
    print(f"  - {len(vendas_por_numero)} vendas indexadas para cruzamento")
    
    # Normalizar números OSS
    itens_df['numero_os_norm'] = itens_df['numero_os'].apply(normalizar_numero)
    print(f"  - Itens OSS com números válidos: {itens_df['numero_os_norm'].notna().sum()}")
    
    # Estatísticas
    stats = {
        'total_itens': len(itens_df),
        'itens_com_numero': 0,
        'matches_encontrados': 0,
        'matches_por_loja': {},
        'novas_vendas_criadas': 0,
        'valor_total_matches': 0.0,
        'valor_total_novas': 0.0
    }
    
    # Processar cruzamento
    print("\n3. Realizando cruzamento...")
    itens_processados = []
    
    for idx, item in itens_df.iterrows():
        if idx % 1000 == 0:
            print(f"  Processando item {idx}/{len(itens_df)}...")
        
        item_processado = item.copy()
        numero_os = item['numero_os_norm']
        loja_nome = item['loja_nome']
        
        if numero_os is not None:
            stats['itens_com_numero'] += 1
            
            # Buscar venda existente
            if numero_os in vendas_por_numero:
                venda_existente = vendas_por_numero[numero_os]
                
                # Usar dados da venda existente
                item_processado['venda_id'] = venda_existente.get('numero_venda')  # Usar numero_venda como ID
                item_processado['venda_uuid'] = str(uuid.uuid4())  # Gerar UUID para item
                item_processado['match_tipo'] = "NUMERO_OS"
                item_processado['venda_cliente_id'] = venda_existente.get('cliente_id')
                item_processado['venda_valor_total'] = venda_existente.get('valor_total')
                item_processado['venda_data'] = venda_existente.get('data_venda')
                item_processado['venda_status'] = venda_existente.get('status')
                
                stats['matches_encontrados'] += 1
                stats['matches_por_loja'][loja_nome] = stats['matches_por_loja'].get(loja_nome, 0) + 1
                
                try:
                    valor = float(item['valor_unitario'] or 0)
                    stats['valor_total_matches'] += valor
                except (ValueError, TypeError):
                    pass
            else:
                # Criar nova venda
                item_processado['venda_id'] = str(uuid.uuid4())
                item_processado['venda_uuid'] = str(uuid.uuid4())
                item_processado['match_tipo'] = "NOVA_VENDA"
                item_processado['venda_cliente_id'] = None
                stats['novas_vendas_criadas'] += 1
                
                try:
                    valor = float(item['valor_unitario'] or 0)
                    stats['valor_total_novas'] += valor
                except (ValueError, TypeError):
                    pass
        else:
            # Item sem número válido - criar nova venda
            item_processado['venda_id'] = str(uuid.uuid4())
            item_processado['venda_uuid'] = str(uuid.uuid4())
            item_processado['match_tipo'] = "SEM_NUMERO"
            item_processado['venda_cliente_id'] = None
            stats['novas_vendas_criadas'] += 1
        
        itens_processados.append(item_processado)
    
    # Criar DataFrame final
    df_final = pd.DataFrame(itens_processados)
    
    print(f"\n=== RESULTADOS DO CRUZAMENTO ===")
    print(f"Total de itens processados: {stats['total_itens']}")
    print(f"Itens com número válido: {stats['itens_com_numero']}")
    print(f"Matches encontrados: {stats['matches_encontrados']}")
    print(f"Novas vendas criadas: {stats['novas_vendas_criadas']}")
    print(f"Taxa de match: {(stats['matches_encontrados'] / stats['total_itens'] * 100):.1f}%")
    
    if stats['matches_por_loja']:
        print(f"\n=== MATCHES POR LOJA ===")
        for loja, count in stats['matches_por_loja'].items():
            print(f"{loja}: {count} matches")
    
    print(f"\nValor total matches: R$ {stats['valor_total_matches']:,.2f}")
    print(f"Valor total novas vendas: R$ {stats['valor_total_novas']:,.2f}")
    
    # Distribuição por tipo de match
    if not df_final.empty:
        print(f"\n=== DISTRIBUIÇÃO POR TIPO DE MATCH ===")
        match_counts = df_final['match_tipo'].value_counts()
        for match_type, count in match_counts.items():
            porcentagem = (count / len(df_final)) * 100
            print(f"{match_type}: {count} ({porcentagem:.1f}%)")
    
    # Salvar resultados
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("data/processados")
    
    # Arquivo completo
    arquivo_completo = output_dir / f"OSS_ITENS_CRUZADOS_POR_NUMERO_{timestamp}.csv"
    df_final.to_csv(arquivo_completo, index=False, encoding='utf-8')
    print(f"\nArquivo completo salvo: {arquivo_completo}")
    
    # Separar matches e novas vendas
    matches_df = df_final[df_final['match_tipo'] == 'NUMERO_OS'].copy()
    novas_df = df_final[df_final['match_tipo'].isin(['NOVA_VENDA', 'SEM_NUMERO'])].copy()
    
    if not matches_df.empty:
        # Arquivo apenas com matches (itens que encontraram vendas existentes)
        arquivo_matches = output_dir / f"OSS_ITENS_MATCHES_PARA_SUPABASE_{timestamp}.csv"
        
        # Colunas para Supabase itens_venda
        colunas_supabase = [
            'item_venda_uuid', 'venda_id', 'produto_codigo', 'produto_descricao',
            'quantidade', 'valor_unitario', 'valor_total', 'desconto', 'observacoes',
            'created_at', 'updated_at'
        ]
        
        # Preparar dados para Supabase
        matches_supabase = matches_df.copy()
        matches_supabase['item_venda_uuid'] = matches_supabase['venda_uuid']  # UUID único para item
        
        # Garantir que todas as colunas existem
        for col in colunas_supabase:
            if col not in matches_supabase.columns:
                matches_supabase[col] = None
        
        matches_final = matches_supabase[colunas_supabase]
        matches_final.to_csv(arquivo_matches, index=False, encoding='utf-8')
        print(f"Arquivo matches Supabase: {arquivo_matches}")
    
    # Arquivo com novas vendas (para criar vendas separadas)
    if not novas_df.empty:
        arquivo_novas = output_dir / f"OSS_NOVAS_VENDAS_{timestamp}.csv"
        novas_df.to_csv(arquivo_novas, index=False, encoding='utf-8')
        print(f"Arquivo novas vendas: {arquivo_novas}")
    
    # Relatório detalhado
    relatorio = {
        'timestamp': timestamp,
        'estatisticas': stats,
        'distribuicao_matches': match_counts.to_dict() if not df_final.empty else {},
        'arquivo_vendas_usado': vendas_file,
        'arquivo_itens_usado': str(itens_file),
        'metodo_cruzamento': 'numero_venda_numero_os',
        'total_arquivos_gerados': 3 if not matches_df.empty and not novas_df.empty else 2
    }
    
    arquivo_relatorio = output_dir / f"OSS_RELATORIO_CRUZAMENTO_NUMERO_{timestamp}.json"
    with open(arquivo_relatorio, 'w', encoding='utf-8') as f:
        json.dump(relatorio, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"Relatório: {arquivo_relatorio}")
    
    print(f"\n=== PROCESSAMENTO CONCLUÍDO ===")
    print(f"Fim: {datetime.now()}")
    
    return df_final, stats

if __name__ == "__main__":
    main()