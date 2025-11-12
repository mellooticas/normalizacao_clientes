#!/usr/bin/env python3
"""
Script para match inteligente usando CPF, telefone e nome do lookup
Aumenta significativamente a cobertura de UUIDs
"""

import pandas as pd
import numpy as np
from pathlib import Path
import re
from fuzzywuzzy import fuzz, process

def normalizar_cpf(cpf):
    """Normaliza CPF removendo pontuação"""
    if pd.isna(cpf):
        return ""
    cpf_str = str(cpf).strip()
    # Remove pontos, traços e espaços
    cpf_limpo = re.sub(r'[^\d]', '', cpf_str)
    return cpf_limpo if len(cpf_limpo) == 11 else ""

def normalizar_telefone(telefone):
    """Normaliza telefone removendo pontuação"""
    if pd.isna(telefone):
        return ""
    tel_str = str(telefone).strip()
    # Remove tudo que não é número
    tel_limpo = re.sub(r'[^\d]', '', tel_str)
    # Remove código do país se houver (55)
    if tel_limpo.startswith('55') and len(tel_limpo) > 11:
        tel_limpo = tel_limpo[2:]
    return tel_limpo if len(tel_limpo) >= 10 else ""

def normalizar_nome(nome):
    """Normaliza nome para comparação"""
    if pd.isna(nome):
        return ""
    nome = str(nome).upper().strip()
    # Remove acentos
    nome = re.sub(r'[ÀÁÂÃÄÅ]', 'A', nome)
    nome = re.sub(r'[ÈÉÊË]', 'E', nome)
    nome = re.sub(r'[ÌÍÎÏ]', 'I', nome)
    nome = re.sub(r'[ÒÓÔÕÖ]', 'O', nome)
    nome = re.sub(r'[ÙÚÛÜ]', 'U', nome)
    nome = re.sub(r'[Ç]', 'C', nome)
    nome = re.sub(r'[^A-Z\s]', '', nome)
    nome = re.sub(r'\s+', ' ', nome)
    return nome.strip()

def match_inteligente_lookup():
    """Faz match usando CPF, telefone e nome do lookup"""
    
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    
    print("=== MATCH INTELIGENTE COM LOOKUP ===")
    
    # 1. Carrega dados
    lookup_df = pd.read_csv(base_dir / "data" / "clientes" / "_consolidado" / "clientes_lookup.csv")
    
    # Carrega dados originais OSS que têm mais informações do cliente
    arquivos_oss = [
        base_dir / "data" / "originais" / "oss" / "finais_postgresql_prontos" / "oss_suzano_clientes_ids.csv",
        base_dir / "data" / "originais" / "oss" / "finais_postgresql_prontos" / "oss_maua_clientes_ids.csv",
        base_dir / "data" / "originais" / "oss" / "finais_postgresql_prontos" / "oss_perus_clientes_ids.csv",
        base_dir / "data" / "originais" / "oss" / "finais_postgresql_prontos" / "oss_rio_pequeno_clientes_ids.csv",
        base_dir / "data" / "originais" / "oss" / "finais_postgresql_prontos" / "oss_sao_mateus_clientes_ids.csv",
        base_dir / "data" / "originais" / "oss" / "finais_postgresql_prontos" / "oss_suzano2_clientes_ids.csv"
    ]
    
    # Consolida dados OSS com informações de CPF/telefone
    todos_oss = []
    for arquivo in arquivos_oss:
        if arquivo.exists():
            df = pd.read_csv(arquivo)
            todos_oss.append(df)
    
    if len(todos_oss) > 0:
        oss_df = pd.concat(todos_oss, ignore_index=True)
    else:
        print("❌ Arquivos OSS não encontrados!")
        return None
    
    # Carrega clientes UUID
    clientes_uuid_df = pd.read_csv(base_dir / "data" / "clientes_uuid" / "todos_clientes_uuid_consolidado.csv")
    
    print(f"Lookup: {len(lookup_df)} registros")
    print(f"OSS: {len(oss_df)} registros")
    print(f"Clientes UUID: {len(clientes_uuid_df)} registros")
    
    # 2. Normaliza dados do lookup
    print(f"\n=== NORMALIZANDO DADOS LOOKUP ===")
    
    lookup_df['cpf_normalizado'] = lookup_df['cpf'].apply(normalizar_cpf)
    lookup_df['telefone1_normalizado'] = lookup_df['telefone1'].apply(normalizar_telefone)
    lookup_df['telefone2_normalizado'] = lookup_df['telefone2'].apply(normalizar_telefone)
    lookup_df['nome_normalizado'] = lookup_df['nome'].apply(normalizar_nome)
    
    # Remove registros sem dados úteis
    lookup_util = lookup_df[
        (lookup_df['cpf_normalizado'] != '') |
        (lookup_df['telefone1_normalizado'] != '') |
        (lookup_df['telefone2_normalizado'] != '') |
        (lookup_df['nome_normalizado'] != '')
    ].copy()
    
    print(f"Lookup útil: {len(lookup_util)} registros")
    print(f"  Com CPF: {(lookup_util['cpf_normalizado'] != '').sum()}")
    print(f"  Com telefone1: {(lookup_util['telefone1_normalizado'] != '').sum()}")
    print(f"  Com telefone2: {(lookup_util['telefone2_normalizado'] != '').sum()}")
    print(f"  Com nome: {(lookup_util['nome_normalizado'] != '').sum()}")
    
    # 3. Normaliza dados OSS
    print(f"\n=== NORMALIZANDO DADOS OSS ===")
    
    # Normaliza CPF, telefones e nomes nos dados OSS
    oss_df['cpf_normalizado'] = oss_df['CPF'].apply(normalizar_cpf)
    oss_df['telefone_normalizado'] = oss_df['TELEFONE :'].apply(normalizar_telefone)
    oss_df['celular_normalizado'] = oss_df['CELULAR:'].apply(normalizar_telefone)
    oss_df['nome_normalizado'] = oss_df['NOME:'].apply(normalizar_nome)
    oss_df['cliente_id_str'] = oss_df['cliente_id'].astype(str)
    
    print(f"OSS com dados úteis:")
    print(f"  Com CPF: {(oss_df['cpf_normalizado'] != '').sum()}")
    print(f"  Com telefone: {(oss_df['telefone_normalizado'] != '').sum()}")
    print(f"  Com celular: {(oss_df['celular_normalizado'] != '').sum()}")
    print(f"  Com nome: {(oss_df['nome_normalizado'] != '').sum()}")
    
    # 4. Faz matches por diferentes critérios
    print(f"\n=== EXECUTANDO MATCHES ===")
    
    matches_encontrados = {}
    
    # 4.1 Match por CPF
    print("Match por CPF...")
    cpf_para_id = dict(zip(lookup_util[lookup_util['cpf_normalizado'] != '']['cpf_normalizado'], 
                          lookup_util[lookup_util['cpf_normalizado'] != '']['id_cliente']))
    
    for _, row in oss_df[oss_df['cpf_normalizado'] != ''].iterrows():
        if row['cpf_normalizado'] in cpf_para_id:
            matches_encontrados[row['cliente_id_str']] = {
                'lookup_id': cpf_para_id[row['cpf_normalizado']],
                'metodo': 'CPF',
                'valor_match': row['cpf_normalizado']
            }
    
    print(f"  Matches por CPF: {len([m for m in matches_encontrados.values() if m['metodo'] == 'CPF'])}")
    
    # 4.2 Match por telefone (telefone/celular OSS vs telefone1/telefone2 lookup)
    print("Match por telefone...")
    tel_para_id = {}
    
    # Cria dicionário de telefones do lookup
    for _, row in lookup_util.iterrows():
        if row['telefone1_normalizado'] != '':
            tel_para_id[row['telefone1_normalizado']] = row['id_cliente']
        if row['telefone2_normalizado'] != '':
            tel_para_id[row['telefone2_normalizado']] = row['id_cliente']
    
    # Busca matches nos OSS
    for _, row in oss_df.iterrows():
        cliente_id = row['cliente_id_str']
        if cliente_id not in matches_encontrados:  # Só se não achou por CPF
            # Testa telefone
            if row['telefone_normalizado'] != '' and row['telefone_normalizado'] in tel_para_id:
                matches_encontrados[cliente_id] = {
                    'lookup_id': tel_para_id[row['telefone_normalizado']],
                    'metodo': 'TELEFONE',
                    'valor_match': row['telefone_normalizado']
                }
            # Testa celular
            elif row['celular_normalizado'] != '' and row['celular_normalizado'] in tel_para_id:
                matches_encontrados[cliente_id] = {
                    'lookup_id': tel_para_id[row['celular_normalizado']],
                    'metodo': 'CELULAR',
                    'valor_match': row['celular_normalizado']
                }
    
    print(f"  Matches por telefone: {len([m for m in matches_encontrados.values() if m['metodo'] in ['TELEFONE', 'CELULAR']])}")
    
    # 4.3 Match por nome (fuzzy)
    print("Match por nome fuzzy...")
    nomes_lookup = lookup_util[lookup_util['nome_normalizado'] != '']['nome_normalizado'].unique()
    nome_para_id = dict(zip(lookup_util[lookup_util['nome_normalizado'] != '']['nome_normalizado'],
                           lookup_util[lookup_util['nome_normalizado'] != '']['id_cliente']))
    
    nomes_sem_match = oss_df[
        (~oss_df['cliente_id_str'].isin(matches_encontrados.keys())) &
        (oss_df['nome_normalizado'] != '')
    ]['nome_normalizado'].unique()
    
    matches_nome = 0
    for nome_oss in nomes_sem_match[:1000]:  # Limita para não demorar muito
        if len(nome_oss) > 5:  # Só nomes com mais de 5 caracteres
            match = process.extractOne(nome_oss, nomes_lookup, scorer=fuzz.ratio)
            if match and match[1] >= 90:  # Similaridade >= 90%
                lookup_id = nome_para_id[match[0]]
                # Encontra todos os clientes OSS com este nome
                clientes_nome = oss_df[oss_df['nome_normalizado'] == nome_oss]['cliente_id_str'].unique()
                for cliente_id in clientes_nome:
                    if cliente_id not in matches_encontrados:
                        matches_encontrados[cliente_id] = {
                            'lookup_id': lookup_id,
                            'metodo': 'NOME_FUZZY',
                            'valor_match': f"{nome_oss} -> {match[0]} ({match[1]}%)"
                        }
                        matches_nome += 1
    
    print(f"  Matches por nome fuzzy: {matches_nome}")
    
    # 5. Aplica os UUIDs encontrados
    print(f"\n=== APLICANDO UUIDS ===")
    
    # Carrega vendas
    vendas_df = pd.read_csv(base_dir / "data" / "vendas_para_importar" / "vendas_corrigido_com_os_originais.csv")
    vendas_df['cliente_id_str'] = vendas_df['cliente_id'].astype(str).str.replace('.0', '')
    
    # Cria mapeamento lookup_id -> UUID
    clientes_uuid_df['id_legado_str'] = clientes_uuid_df['id_legado'].astype(str).str.replace('.0', '')
    lookup_para_uuid = dict(zip(clientes_uuid_df['id_legado_str'], clientes_uuid_df['cliente_id']))
    
    # Aplica matches
    vendas_df['uuid_encontrado'] = None
    vendas_df['metodo_match'] = None
    
    for cliente_id_str, match_info in matches_encontrados.items():
        lookup_id_str = str(match_info['lookup_id'])
        if lookup_id_str in lookup_para_uuid:
            uuid = lookup_para_uuid[lookup_id_str]
            mask = vendas_df['cliente_id_str'] == cliente_id_str
            vendas_df.loc[mask, 'uuid_encontrado'] = uuid
            vendas_df.loc[mask, 'metodo_match'] = match_info['metodo']
    
    # 6. Consolida resultado final
    print(f"\n=== RESULTADO FINAL ===")
    
    # Usa UUID encontrado ou mantém o que já tinha
    vendas_df['cliente_id_final'] = vendas_df['uuid_encontrado'].fillna(vendas_df['cliente_id'])
    
    # Remove colunas auxiliares
    vendas_final = vendas_df[[
        'numero_venda', 'cliente_id_final', 'loja_id', 'vendedor_id', 
        'data_venda', 'valor_total', 'valor_entrada', 'nome_cliente_temp',
        'observacoes', 'status', 'cancelado', 'created_at', 'updated_at'
    ]].copy()
    
    vendas_final.rename(columns={'cliente_id_final': 'cliente_id'}, inplace=True)
    
    # Estatísticas
    total_vendas = len(vendas_final)
    com_uuid = vendas_final['cliente_id'].notna().sum()
    novos_matches = vendas_df['uuid_encontrado'].notna().sum()
    
    print(f"Total vendas: {total_vendas}")
    print(f"COM UUID: {com_uuid} ({com_uuid/total_vendas*100:.1f}%)")
    print(f"SEM UUID: {total_vendas - com_uuid} ({(total_vendas - com_uuid)/total_vendas*100:.1f}%)")
    print(f"Novos matches encontrados: {novos_matches}")
    
    # Detalhes por método
    print(f"\nDetalhes por método:")
    for metodo in ['CPF', 'TELEFONE', 'CELULAR', 'NOME_FUZZY']:
        count = vendas_df[vendas_df['metodo_match'] == metodo]['uuid_encontrado'].count()
        if count > 0:
            print(f"  {metodo}: {count} matches")
    
    # 7. Salva arquivo final
    arquivo_final = base_dir / "data" / "vendas_para_importar" / "vendas_final_match_inteligente.csv"
    vendas_final.to_csv(arquivo_final, index=False)
    
    print(f"\n=== ARQUIVO FINAL ===")
    print(f"Salvo: {arquivo_final}")
    print(f"📊 {com_uuid} vendas com UUID ({com_uuid/total_vendas*100:.1f}%)")
    print(f"🎯 +{novos_matches} novos matches pelo lookup!")
    
    # 8. Comandos SQL
    print(f"\n=== COMANDOS SQL ===")
    print(f"TRUNCATE TABLE vendas.vendas RESTART IDENTITY CASCADE;")
    print(f"\\copy vendas.vendas FROM '{arquivo_final}' CSV HEADER;")
    print(f"SELECT COUNT(*), COUNT(cliente_id) FROM vendas.vendas;")
    
    return vendas_final

if __name__ == "__main__":
    resultado = match_inteligente_lookup()
    if resultado is not None:
        print("\n🎉 MATCH INTELIGENTE CONCLUÍDO!")
        print("✅ Cobertura maximizada com CPF, telefone e nome!")
        print("🚀 Arquivo final pronto para importação!")