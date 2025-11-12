#!/usr/bin/env python3
"""
SCRIPT FINAL: Gera arquivo para importação (97.1%) + arquivo pendente (2.9%)
"""

import pandas as pd
from pathlib import Path
import uuid
from datetime import datetime

def gerar_arquivos_finais():
    """Gera arquivo pronto para importar + arquivo pendente para resolver depois"""
    
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    
    print("🚀 === GERANDO ARQUIVOS FINAIS === 🚀")
    
    # 1. Carrega vendas
    vendas_df = pd.read_csv(base_dir / "data" / "vendas_para_importar" / "vendas_corrigido_com_os_originais.csv")
    vendas_df['cliente_id_str'] = vendas_df['cliente_id'].astype(str).str.replace('.0', '')
    
    total_vendas = len(vendas_df)
    print(f"📊 Total vendas: {total_vendas}")
    
    # 2. Carrega matches por nomes
    matches_nomes = pd.read_csv(base_dir / "data" / "matches_nomes_variacoes.csv")
    matches_nomes['oss_cliente_id_str'] = matches_nomes['oss_cliente_id'].astype(str)
    matches_nomes_dict = dict(zip(matches_nomes['oss_cliente_id_str'], matches_nomes['uuid_encontrado']))
    
    # 3. Carrega UUID consolidado (lookup tradicional)
    uuid_consolidado = pd.read_csv(base_dir / "data" / "clientes_uuid" / "todos_clientes_uuid_consolidado.csv")
    uuid_consolidado['id_legado_str'] = uuid_consolidado['id_legado'].astype(str).str.replace('.0', '')
    lookup_dict = dict(zip(uuid_consolidado['id_legado_str'], uuid_consolidado['cliente_id']))
    
    # 4. Aplica UUIDs nas vendas
    vendas_df['cliente_uuid_final'] = None
    vendas_df['fonte_uuid'] = None
    
    # Prioridade 1: Matches por nomes
    mask_nomes = vendas_df['cliente_id_str'].isin(matches_nomes_dict.keys())
    vendas_df.loc[mask_nomes, 'cliente_uuid_final'] = vendas_df.loc[mask_nomes, 'cliente_id_str'].map(matches_nomes_dict)
    vendas_df.loc[mask_nomes, 'fonte_uuid'] = 'MATCH_NOMES'
    
    # Prioridade 2: Lookup tradicional (para os que não tiveram match por nomes)
    mask_lookup = (vendas_df['cliente_uuid_final'].isna()) & (vendas_df['cliente_id_str'].isin(lookup_dict.keys()))
    vendas_df.loc[mask_lookup, 'cliente_uuid_final'] = vendas_df.loc[mask_lookup, 'cliente_id_str'].map(lookup_dict)
    vendas_df.loc[mask_lookup, 'fonte_uuid'] = 'LOOKUP_TRADICIONAL'
    
    # 5. Separa vendas com UUID vs sem UUID
    vendas_com_uuid = vendas_df[vendas_df['cliente_uuid_final'].notna()].copy()
    vendas_sem_uuid = vendas_df[vendas_df['cliente_uuid_final'].isna()].copy()
    
    print(f"✅ Vendas COM UUID: {len(vendas_com_uuid)} ({len(vendas_com_uuid)/total_vendas*100:.1f}%)")
    print(f"⏳ Vendas SEM UUID: {len(vendas_sem_uuid)} ({len(vendas_sem_uuid)/total_vendas*100:.1f}%)")
    
    # 6. ARQUIVO 1: Vendas prontas para importar (97.1%)
    vendas_importar = vendas_com_uuid[[
        'numero_venda', 'cliente_uuid_final', 'loja_id', 'vendedor_id', 
        'data_venda', 'valor_total', 'valor_entrada', 'nome_cliente_temp',
        'observacoes', 'status', 'cancelado', 'created_at', 'updated_at'
    ]].copy()
    
    vendas_importar.rename(columns={'cliente_uuid_final': 'cliente_id'}, inplace=True)
    
    # Arquivo para importação
    arquivo_importar = base_dir / "data" / "vendas_para_importar" / "vendas_PRONTO_PARA_IMPORTAR_97pct.csv"
    vendas_importar.to_csv(arquivo_importar, index=False)
    
    print(f"\n📁 ARQUIVO 1 - PRONTO PARA IMPORTAR:")
    print(f"   Arquivo: {arquivo_importar}")
    print(f"   Vendas: {len(vendas_importar)} (97.1%)")
    print(f"   Status: ✅ PRONTO PARA TRUNCATE E IMPORT")
    
    # 7. ARQUIVO 2: Vendas pendentes (2.9%)
    vendas_pendentes = vendas_sem_uuid[[
        'numero_venda', 'cliente_id', 'cliente_id_str', 'loja_id', 'vendedor_id', 
        'data_venda', 'valor_total', 'valor_entrada', 'nome_cliente_temp',
        'observacoes', 'status', 'cancelado', 'created_at', 'updated_at'
    ]].copy()
    
    # Adiciona informações úteis para resolver depois
    vendas_pendentes['data_processamento'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    vendas_pendentes['cliente_uuid_encontrar'] = None  # Para preencher quando encontrar
    vendas_pendentes['observacoes_uuid'] = 'UUID não encontrado - investigar se é cliente novo ou erro de match'
    
    # Arquivo pendente
    arquivo_pendente = base_dir / "data" / "vendas_para_importar" / "vendas_PENDENTES_UUID_3pct.csv"
    vendas_pendentes.to_csv(arquivo_pendente, index=False)
    
    print(f"\n📁 ARQUIVO 2 - PENDENTES PARA RESOLVER:")
    print(f"   Arquivo: {arquivo_pendente}")
    print(f"   Vendas: {len(vendas_pendentes)} (2.9%)")
    print(f"   Status: ⏳ INVESTIGAR UUIDs DEPOIS")
    
    # 8. Análise dos pendentes
    print(f"\n🔍 ANÁLISE DOS PENDENTES:")
    
    # Por padrão de ID
    padroes_pendentes = {}
    for _, row in vendas_pendentes.iterrows():
        id_str = row['cliente_id_str']
        if id_str.startswith('5000'):
            padroes_pendentes['5000xxx'] = padroes_pendentes.get('5000xxx', 0) + 1
        elif id_str.startswith('6000'):
            padroes_pendentes['6000xxx'] = padroes_pendentes.get('6000xxx', 0) + 1
        else:
            padroes_pendentes['outros'] = padroes_pendentes.get('outros', 0) + 1
    
    for padrao, count in padroes_pendentes.items():
        print(f"   {padrao}: {count} vendas")
    
    # Por loja
    lojas_pendentes = vendas_pendentes['loja_id'].value_counts()
    print(f"\n   Por loja:")
    for loja_id, count in lojas_pendentes.items():
        print(f"   {loja_id}: {count} vendas")
    
    # 9. Estatísticas finais por fonte
    print(f"\n📊 ESTATÍSTICAS FONTES UUID (vendas prontas):")
    fontes = vendas_com_uuid['fonte_uuid'].value_counts()
    for fonte, count in fontes.items():
        print(f"   {fonte}: {count} vendas")
    
    # 10. Comandos SQL para importação
    print(f"\n🛠️  COMANDOS PARA IMPORTAÇÃO:")
    print(f"   1. TRUNCATE TABLE vendas.vendas;")
    print(f"   2. \\copy vendas.vendas FROM '{arquivo_importar}' CSV HEADER;")
    print(f"   3. SELECT COUNT(*) FROM vendas.vendas; -- Deve retornar {len(vendas_importar)}")
    
    return {
        'vendas_importar': vendas_importar,
        'vendas_pendentes': vendas_pendentes,
        'arquivo_importar': arquivo_importar,
        'arquivo_pendente': arquivo_pendente
    }

if __name__ == "__main__":
    resultado = gerar_arquivos_finais()
    
    print(f"\n🎉 === MISSÃO QUASE CUMPRIDA! === 🎉")
    print(f"✅ {len(resultado['vendas_importar'])} vendas PRONTAS para importar")
    print(f"⏳ {len(resultado['vendas_pendentes'])} vendas para resolver depois") 
    print(f"🎯 97.1% DE SUCESSO na primeira rodada!")
    print(f"🚀 Arquivos gerados e prontos para uso!")