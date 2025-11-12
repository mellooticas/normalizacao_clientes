#!/usr/bin/env python3
"""
Script para consolidar todos os clientes UUID e fazer cruzamento completo
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import re
from fuzzywuzzy import fuzz, process

def consolidar_clientes_uuid():
    """Consolida todos os clientes UUID de todas as lojas"""
    
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    pasta_clientes_uuid = base_dir / "data" / "clientes_uuid"
    
    print("=== CONSOLIDANDO CLIENTES UUID ===")
    
    todos_clientes = []
    
    # Lista arquivos de clientes UUID
    arquivos_clientes = list(pasta_clientes_uuid.glob("clientes_*.csv"))
    
    for arquivo in arquivos_clientes:
        print(f"Processando: {arquivo.name}")
        df = pd.read_csv(arquivo)
        
        # Verifica se tem a coluna cliente_id ou similar
        if 'cliente_id_y' in df.columns:
            df['cliente_id'] = df['cliente_id_y']
        elif 'cliente_id_x' in df.columns:
            df['cliente_id'] = df['cliente_id_x']
        
        print(f"  {len(df)} clientes encontrados")
        
        # Seleciona colunas importantes
        colunas_necessarias = ['cliente_id', 'Nome Completo', 'Cliente', 'loja_nome']
        colunas_disponiveis = [col for col in colunas_necessarias if col in df.columns]
        
        df_selecionado = df[colunas_disponiveis].copy()
        
        # Pega nome do arquivo para identificar loja se não houver coluna
        if 'loja_nome' not in df_selecionado.columns:
            loja_nome = arquivo.name.replace('clientes_', '').replace('.csv', '')
            df_selecionado['loja_nome'] = loja_nome
        
        todos_clientes.append(df_selecionado)
    
    # Combina todos
    clientes_consolidados = pd.concat(todos_clientes, ignore_index=True)
    
    # Remove duplicatas por cliente_id
    clientes_unicos = clientes_consolidados.drop_duplicates(subset=['cliente_id']).copy()
    
    print(f"Total de clientes únicos: {len(clientes_unicos)}")
    
    # Salva arquivo consolidado
    arquivo_consolidado = base_dir / "data" / "clientes_uuid" / "clientes_uuid_consolidado.csv"
    clientes_unicos.to_csv(arquivo_consolidado, index=False)
    
    print(f"Arquivo consolidado salvo: {arquivo_consolidado}")
    
    return clientes_unicos

def normalizar_nome(nome):
    """Normaliza nome para comparação"""
    if pd.isna(nome):
        return ""
    nome = str(nome).upper().strip()
    # Remove acentos, caracteres especiais
    nome = re.sub(r'[ÀÁÂÃÄÅ]', 'A', nome)
    nome = re.sub(r'[ÈÉÊË]', 'E', nome)
    nome = re.sub(r'[ÌÍÎÏ]', 'I', nome)
    nome = re.sub(r'[ÒÓÔÕÖ]', 'O', nome)
    nome = re.sub(r'[ÙÚÛÜ]', 'U', nome)
    nome = re.sub(r'[Ç]', 'C', nome)
    nome = re.sub(r'[^A-Z0-9\s]', '', nome)
    nome = re.sub(r'\s+', ' ', nome)
    return nome.strip()

def fazer_cruzamento_completo():
    """Faz cruzamento completo entre dados com e sem UUID"""
    
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    
    print("\n=== CRUZAMENTO COMPLETO DE CLIENTES ===")
    
    # 1. Consolida clientes UUID primeiro
    clientes_uuid_df = consolidar_clientes_uuid()
    
    # 2. Carrega dados de vendas definitivos (base completa)
    vendas_df = pd.read_csv(base_dir / "data" / "vendas_para_importar" / "vendas_definitivo.csv")
    print(f"Total de vendas: {len(vendas_df)}")
    
    # 3. Separa vendas com e sem UUID
    vendas_com_uuid = vendas_df[vendas_df['cliente_id'].notna()].copy()
    vendas_sem_uuid = vendas_df[vendas_df['cliente_id'].isna()].copy()
    
    print(f"Vendas COM UUID: {len(vendas_com_uuid)}")
    print(f"Vendas SEM UUID: {len(vendas_sem_uuid)}")
    
    # 4. Normaliza nomes para matching
    print(f"\n=== PREPARANDO DADOS PARA CRUZAMENTO ===")
    
    # Cria campo de nome normalizado para clientes UUID
    clientes_uuid_df['nome_busca'] = ''
    
    # Tenta diferentes colunas de nome
    if 'Nome Completo' in clientes_uuid_df.columns:
        clientes_uuid_df['nome_busca'] = clientes_uuid_df['Nome Completo'].apply(normalizar_nome)
    elif 'Cliente' in clientes_uuid_df.columns:
        clientes_uuid_df['nome_busca'] = clientes_uuid_df['Cliente'].apply(normalizar_nome)
    
    # Remove clientes sem nome ou UUID válido
    clientes_uuid_df = clientes_uuid_df[
        (clientes_uuid_df['nome_busca'] != '') & 
        (clientes_uuid_df['cliente_id'].notna())
    ].copy()
    
    # Normaliza nomes das vendas sem UUID
    vendas_sem_uuid['nome_busca'] = vendas_sem_uuid['nome_cliente_temp'].apply(normalizar_nome)
    
    print(f"Clientes únicos para busca: {len(clientes_uuid_df)}")
    print(f"Nomes únicos sem UUID: {vendas_sem_uuid['nome_busca'].nunique()}")
    
    # 5. Faz cruzamento por nome exato
    print(f"\n=== CRUZAMENTO POR NOME EXATO ===")
    
    # Cria dicionário de nomes para UUID
    nome_para_uuid = dict(zip(clientes_uuid_df['nome_busca'], clientes_uuid_df['cliente_id']))
    
    # Aplica matching exato
    vendas_sem_uuid['cliente_id_encontrado'] = vendas_sem_uuid['nome_busca'].map(nome_para_uuid)
    
    matches_exatos = vendas_sem_uuid['cliente_id_encontrado'].notna().sum()
    print(f"Matches exatos: {matches_exatos}")
    
    # 6. Faz cruzamento por similaridade (fuzzy matching)
    print(f"\n=== CRUZAMENTO POR SIMILARIDADE ===")
    
    nomes_sem_match = vendas_sem_uuid[vendas_sem_uuid['cliente_id_encontrado'].isna()]
    nomes_unicos_sem_match = nomes_sem_match['nome_busca'].unique()
    nomes_clientes_disponiveis = clientes_uuid_df['nome_busca'].unique()
    
    print(f"Nomes para busca por similaridade: {len(nomes_unicos_sem_match)}")
    
    matches_fuzzy = {}
    contador = 0
    
    for nome_busca in nomes_unicos_sem_match:
        if len(nome_busca) > 3:  # Só busca nomes com mais de 3 caracteres
            match = process.extractOne(nome_busca, nomes_clientes_disponiveis, scorer=fuzz.ratio)
            if match and match[1] >= 85:  # Similaridade >= 85%
                uuid_encontrado = nome_para_uuid[match[0]]
                matches_fuzzy[nome_busca] = uuid_encontrado
                contador += 1
                if contador <= 10:  # Mostra só os primeiros 10
                    print(f"  {nome_busca} -> {match[0]} (similaridade: {match[1]}%)")
    
    if contador > 10:
        print(f"  ... e mais {contador - 10} matches")
    
    print(f"Matches por similaridade: {len(matches_fuzzy)}")
    
    # Aplica matches fuzzy
    for nome_busca, uuid in matches_fuzzy.items():
        mask = (vendas_sem_uuid['nome_busca'] == nome_busca) & (vendas_sem_uuid['cliente_id_encontrado'].isna())
        vendas_sem_uuid.loc[mask, 'cliente_id_encontrado'] = uuid
    
    # 7. Consolida resultados
    print(f"\n=== CONSOLIDANDO RESULTADOS ===")
    
    # Aplica UUIDs encontrados
    vendas_sem_uuid['cliente_id_final'] = vendas_sem_uuid['cliente_id_encontrado']
    vendas_sem_uuid.loc[vendas_sem_uuid['cliente_id_final'].isna(), 'cliente_id_final'] = np.nan
    
    # Junta com vendas que já tinham UUID
    vendas_com_uuid['cliente_id_final'] = vendas_com_uuid['cliente_id']
    
    # Combina todos os dados
    colunas_necessarias = ['numero_venda', 'cliente_id', 'loja_id', 'vendedor_id', 
                          'data_venda', 'valor_total', 'valor_entrada', 'nome_cliente_temp',
                          'observacoes', 'status', 'cancelado', 'created_at', 'updated_at']
    
    vendas_finais = []
    
    # Adiciona vendas que já tinham UUID
    vendas_finais.append(vendas_com_uuid[colunas_necessarias])
    
    # Adiciona vendas sem UUID (com e sem matches)
    vendas_sem_uuid['cliente_id'] = vendas_sem_uuid['cliente_id_final']
    vendas_finais.append(vendas_sem_uuid[colunas_necessarias])
    
    # Combina tudo
    vendas_completas = pd.concat(vendas_finais, ignore_index=True)
    
    # 8. Estatísticas finais
    print(f"\n=== ESTATÍSTICAS FINAIS ===")
    print(f"Total de vendas: {len(vendas_completas)}")
    
    com_uuid_final = vendas_completas['cliente_id'].notna().sum()
    sem_uuid_final = vendas_completas['cliente_id'].isna().sum()
    
    print(f"COM cliente UUID: {com_uuid_final} ({com_uuid_final/len(vendas_completas)*100:.1f}%)")
    print(f"SEM cliente UUID: {sem_uuid_final} ({sem_uuid_final/len(vendas_completas)*100:.1f}%)")
    
    matches_novos = (vendas_sem_uuid['cliente_id_encontrado'].notna().sum())
    print(f"Novos matches encontrados: {matches_novos}")
    
    valor_total = vendas_completas['valor_total'].sum()
    valor_com_uuid = vendas_completas[vendas_completas['cliente_id'].notna()]['valor_total'].sum()
    
    print(f"Valor total: R$ {valor_total:,.2f}")
    print(f"Valor com UUID: R$ {valor_com_uuid:,.2f} ({valor_com_uuid/valor_total*100:.1f}%)")
    
    # 9. Salva arquivo final completo
    arquivo_final = base_dir / "data" / "vendas_para_importar" / "vendas_completo_com_cruzamento.csv"
    vendas_completas.to_csv(arquivo_final, index=False)
    
    # 10. Salva apenas clientes ainda sem UUID
    vendas_ainda_sem_uuid = vendas_completas[vendas_completas['cliente_id'].isna()]
    arquivo_restantes = base_dir / "data" / "clientes" / "clientes_ainda_sem_uuid.csv"
    
    if len(vendas_ainda_sem_uuid) > 0:
        # Cria lista única de clientes restantes
        clientes_restantes = vendas_ainda_sem_uuid.groupby('nome_cliente_temp').agg({
            'numero_venda': 'count',
            'valor_total': 'sum',
            'valor_entrada': 'sum',
            'data_venda': ['min', 'max']
        }).reset_index()
        
        clientes_restantes.columns = ['nome_cliente', 'total_vendas', 'valor_total', 
                                    'valor_entrada', 'primeira_venda', 'ultima_venda']
        
        clientes_restantes = clientes_restantes.sort_values('valor_total', ascending=False)
        clientes_restantes.to_csv(arquivo_restantes, index=False)
        
        print(f"Clientes ainda sem UUID: {len(clientes_restantes)}")
    
    # 11. Salva detalhes dos matches encontrados
    arquivo_matches = base_dir / "data" / "clientes" / "matches_encontrados.csv"
    
    matches_encontrados = vendas_sem_uuid[vendas_sem_uuid['cliente_id_encontrado'].notna()].copy()
    matches_encontrados = matches_encontrados.groupby(['nome_cliente_temp', 'cliente_id_encontrado']).agg({
        'numero_venda': 'count',
        'valor_total': 'sum'
    }).reset_index()
    
    matches_encontrados.columns = ['nome_cliente', 'cliente_uuid', 'total_vendas', 'valor_total']
    matches_encontrados = matches_encontrados.sort_values('valor_total', ascending=False)
    matches_encontrados.to_csv(arquivo_matches, index=False)
    
    print(f"\n=== ARQUIVOS GERADOS ===")
    print(f"1. Arquivo completo: {arquivo_final}")
    print(f"   📊 {len(vendas_completas)} vendas com máximo de UUIDs")
    
    print(f"2. Matches encontrados: {arquivo_matches}")
    print(f"   🎯 {len(matches_encontrados)} clientes com UUID atribuído")
    
    if len(vendas_ainda_sem_uuid) > 0:
        print(f"3. Clientes restantes: {arquivo_restantes}")
        print(f"   📋 {len(clientes_restantes)} clientes ainda para resolver")
    
    # 12. Comandos para verificação
    print(f"\n=== VERIFICAÇÃO NO BANCO ===")
    print("TRUNCATE TABLE vendas.vendas RESTART IDENTITY CASCADE;")
    print(f"\\copy vendas.vendas FROM '{arquivo_final}' CSV HEADER;")
    print("SELECT COUNT(*), COUNT(cliente_id) as com_cliente FROM vendas.vendas;")
    
    return vendas_completas

if __name__ == "__main__":
    resultado = fazer_cruzamento_completo()
    print("\n🎉 CRUZAMENTO COMPLETO FINALIZADO!")
    print("✅ Máximo de clientes UUID aplicados!")
    print("🚀 Arquivo pronto para importação final!")