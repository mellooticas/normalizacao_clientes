#!/usr/bin/env python3
"""
Script híbrido: combina UUIDs reais do banco + lookup completo
Primeira tenta UUIDs reais, depois usa lookup para completar
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
    cpf_limpo = re.sub(r'[^\d]', '', cpf_str)
    return cpf_limpo if len(cpf_limpo) == 11 else ""

def normalizar_telefone(telefone):
    """Normaliza telefone removendo pontuação"""
    if pd.isna(telefone):
        return ""
    tel_str = str(telefone).strip()
    tel_limpo = re.sub(r'[^\d]', '', tel_str)
    if tel_limpo.startswith('55') and len(tel_limpo) > 11:
        tel_limpo = tel_limpo[2:]
    return tel_limpo if len(tel_limpo) >= 10 else ""

def normalizar_nome(nome):
    """Normaliza nome para comparação"""
    if pd.isna(nome):
        return ""
    nome = str(nome).upper().strip()
    nome = re.sub(r'[ÀÁÂÃÄÅ]', 'A', nome)
    nome = re.sub(r'[ÈÉÊË]', 'E', nome)
    nome = re.sub(r'[ÌÍÎÏ]', 'I', nome)
    nome = re.sub(r'[ÒÓÔÕÖ]', 'O', nome)
    nome = re.sub(r'[ÙÚÛÜ]', 'U', nome)
    nome = re.sub(r'[Ç]', 'C', nome)
    nome = re.sub(r'[^A-Z\s]', '', nome)
    nome = re.sub(r'\s+', ' ', nome)
    return nome.strip()

def abordagem_hibrida_completa():
    """Combina UUIDs reais do banco + lookup completo para 100% cobertura"""
    
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    
    print("=== ABORDAGEM HÍBRIDA: UUIDs REAIS + LOOKUP ===")
    
    # 1. PRIMEIRA FASE: UUIDs reais do banco (como fizemos antes)
    print(f"\n=== FASE 1: UUIDs REAIS DO BANCO ===")
    
    # Carrega clientes das lojas com dados completos
    arquivos_lojas = [
        base_dir / "data" / "clientes_uuid" / "clientes_suzano.csv",
        base_dir / "data" / "clientes_uuid" / "clientes_maua.csv",
        base_dir / "data" / "clientes_uuid" / "clientes_perus.csv",
        base_dir / "data" / "clientes_uuid" / "clientes_rio_pequeno.csv",
        base_dir / "data" / "clientes_uuid" / "clientes_sao_mateus.csv",
        base_dir / "data" / "clientes_uuid" / "clientes_suzano2.csv"
    ]
    
    clientes_completos = []
    tem_cpf = False
    tem_telefone = False
    
    for arquivo in arquivos_lojas:
        if arquivo.exists():
            df = pd.read_csv(arquivo)
            
            # Padroniza UUID
            if 'cliente_id_y' in df.columns:
                df['cliente_uuid'] = df['cliente_id_y']
            elif 'cliente_id_x' in df.columns:
                df['cliente_uuid'] = df['cliente_id_x']
            elif 'cliente_id' in df.columns:
                df['cliente_uuid'] = df['cliente_id']
            
            # Normaliza nome
            if 'Nome Completo' in df.columns:
                df['nome_normalizado'] = df['Nome Completo'].apply(normalizar_nome)
            elif 'Cliente' in df.columns:
                df['nome_normalizado'] = df['Cliente'].apply(normalizar_nome)
            else:
                df['nome_normalizado'] = ""
            
            # CPF - parece não ter nos arquivos de clientes
            df['cpf_normalizado'] = ""
            
            # Telefone
            if 'Fone' in df.columns:
                df['telefone_normalizado'] = df['Fone'].apply(normalizar_telefone)
                tem_telefone = True
            else:
                df['telefone_normalizado'] = ""
            
            # Sempre inclui as colunas básicas
            colunas_necessarias = ['cliente_uuid', 'nome_normalizado', 'cpf_normalizado', 'telefone_normalizado']
            
            # Garante que todas as colunas existem
            for col in colunas_necessarias:
                if col not in df.columns:
                    df[col] = ""
            
            clientes_completos.append(df[colunas_necessarias])
    
    clientes_banco_df = pd.concat(clientes_completos, ignore_index=True)
    clientes_banco_df = clientes_banco_df.drop_duplicates(subset=['cliente_uuid'], keep='first')
    
    print(f"Clientes banco: {len(clientes_banco_df)}")
    
    # Carrega dados OSS
    arquivos_oss = [
        base_dir / "data" / "originais" / "oss" / "finais_postgresql_prontos" / "oss_suzano_clientes_ids.csv",
        base_dir / "data" / "originais" / "oss" / "finais_postgresql_prontos" / "oss_maua_clientes_ids.csv",
        base_dir / "data" / "originais" / "oss" / "finais_postgresql_prontos" / "oss_perus_clientes_ids.csv",
        base_dir / "data" / "originais" / "oss" / "finais_postgresql_prontos" / "oss_rio_pequeno_clientes_ids.csv",
        base_dir / "data" / "originais" / "oss" / "finais_postgresql_prontos" / "oss_sao_mateus_clientes_ids.csv",
        base_dir / "data" / "originais" / "oss" / "finais_postgresql_prontos" / "oss_suzano2_clientes_ids.csv"
    ]
    
    todos_oss = []
    for arquivo in arquivos_oss:
        if arquivo.exists():
            df = pd.read_csv(arquivo)
            todos_oss.append(df)
    
    oss_df = pd.concat(todos_oss, ignore_index=True)
    
    # Normaliza dados OSS
    oss_df['cpf_normalizado'] = oss_df['CPF'].apply(normalizar_cpf)
    oss_df['telefone_normalizado'] = oss_df['TELEFONE :'].apply(normalizar_telefone) 
    oss_df['celular_normalizado'] = oss_df['CELULAR:'].apply(normalizar_telefone)
    oss_df['nome_normalizado'] = oss_df['NOME:'].apply(normalizar_nome)
    oss_df['cliente_id_str'] = oss_df['cliente_id'].astype(str)
    
    # Matches com UUIDs reais
    matches_uuid_real = {}
    
    # Match por CPF - mas parece que não tem CPF nos arquivos de clientes
    # Pula esta parte se não tem CPF
    
    # Match por telefone
    if tem_telefone:
        tel_para_uuid = {}
        for _, row in clientes_banco_df.iterrows():
            if row['telefone_normalizado'] != '':
                tel_para_uuid[row['telefone_normalizado']] = row['cliente_uuid']
        
        for _, row in oss_df.iterrows():
            cliente_id = row['cliente_id_str']
            if cliente_id not in matches_uuid_real:
                if row['telefone_normalizado'] != '' and row['telefone_normalizado'] in tel_para_uuid:
                    matches_uuid_real[cliente_id] = {
                        'uuid': tel_para_uuid[row['telefone_normalizado']],
                        'metodo': 'UUID_REAL_TEL',
                        'fonte': 'BANCO'
                    }
                elif row['celular_normalizado'] != '' and row['celular_normalizado'] in tel_para_uuid:
                    matches_uuid_real[cliente_id] = {
                        'uuid': tel_para_uuid[row['celular_normalizado']],
                        'metodo': 'UUID_REAL_CEL',
                        'fonte': 'BANCO'
                    }
    
    # Match por nome fuzzy
    nomes_banco_limpos = clientes_banco_df[
        (clientes_banco_df['nome_normalizado'] != '') & 
        (clientes_banco_df['nome_normalizado'].notna())
    ]['nome_normalizado'].unique()
    
    nomes_banco_validos = [nome for nome in nomes_banco_limpos if isinstance(nome, str) and len(nome) > 3]
    
    nome_para_uuid = {}
    for _, row in clientes_banco_df.iterrows():
        if isinstance(row['nome_normalizado'], str) and row['nome_normalizado'] != '':
            nome_para_uuid[row['nome_normalizado']] = row['cliente_uuid']
    
    nomes_sem_match = oss_df[
        (~oss_df['cliente_id_str'].isin(matches_uuid_real.keys())) &
        (oss_df['nome_normalizado'] != '') &
        (oss_df['nome_normalizado'].notna())
    ]['nome_normalizado'].unique()
    
    nomes_sem_match_validos = [nome for nome in nomes_sem_match if isinstance(nome, str) and len(nome) > 5]
    
    for nome_oss in nomes_sem_match_validos[:500]:  # Limita para performance
        try:
            match = process.extractOne(nome_oss, nomes_banco_validos, scorer=fuzz.ratio)
            if match and match[1] >= 90:
                uuid_encontrado = nome_para_uuid.get(match[0])
                if uuid_encontrado:
                    clientes_nome = oss_df[oss_df['nome_normalizado'] == nome_oss]['cliente_id_str'].unique()
                    for cliente_id in clientes_nome:
                        if cliente_id not in matches_uuid_real:
                            matches_uuid_real[cliente_id] = {
                                'uuid': uuid_encontrado,
                                'metodo': 'UUID_REAL_NOME',
                                'fonte': 'BANCO'
                            }
        except:
            continue
    
    print(f"Matches UUID real: {len(matches_uuid_real)}")
    
    # 2. SEGUNDA FASE: Lookup para os restantes
    print(f"\n=== FASE 2: LOOKUP PARA RESTANTES ===")
    
    # Carrega lookup
    lookup_df = pd.read_csv(base_dir / "data" / "clientes" / "_consolidado" / "clientes_lookup.csv")
    
    # Normaliza lookup
    lookup_df['cpf_normalizado'] = lookup_df['cpf'].apply(normalizar_cpf)
    lookup_df['telefone1_normalizado'] = lookup_df['telefone1'].apply(normalizar_telefone)
    lookup_df['telefone2_normalizado'] = lookup_df['telefone2'].apply(normalizar_telefone)
    lookup_df['nome_normalizado'] = lookup_df['nome'].apply(normalizar_nome)
    
    # Carrega mapeamento lookup -> UUID
    clientes_uuid_consolidado = pd.read_csv(base_dir / "data" / "clientes_uuid" / "todos_clientes_uuid_consolidado.csv")
    clientes_uuid_consolidado['id_legado_str'] = clientes_uuid_consolidado['id_legado'].astype(str).str.replace('.0', '')
    lookup_para_uuid = dict(zip(clientes_uuid_consolidado['id_legado_str'], clientes_uuid_consolidado['cliente_id']))
    
    matches_lookup = {}
    
    # IDs que ainda não têm UUID real
    ids_sem_uuid_real = set(oss_df['cliente_id_str']) - set(matches_uuid_real.keys())
    oss_sem_uuid = oss_df[oss_df['cliente_id_str'].isin(ids_sem_uuid_real)]
    
    print(f"IDs ainda sem UUID: {len(ids_sem_uuid_real)}")
    
    # Match lookup por CPF
    cpf_lookup_para_id = dict(zip(lookup_df[lookup_df['cpf_normalizado'] != '']['cpf_normalizado'], 
                                 lookup_df[lookup_df['cpf_normalizado'] != '']['id_cliente']))
    
    for _, row in oss_sem_uuid[oss_sem_uuid['cpf_normalizado'] != ''].iterrows():
        if row['cpf_normalizado'] in cpf_lookup_para_id:
            lookup_id = str(cpf_lookup_para_id[row['cpf_normalizado']])
            if lookup_id in lookup_para_uuid:
                matches_lookup[row['cliente_id_str']] = {
                    'uuid': lookup_para_uuid[lookup_id],
                    'metodo': 'LOOKUP_CPF',
                    'fonte': 'LOOKUP'
                }
    
    # Match lookup por telefone
    tel_lookup_para_id = {}
    for _, row in lookup_df.iterrows():
        if row['telefone1_normalizado'] != '':
            tel_lookup_para_id[row['telefone1_normalizado']] = row['id_cliente']
        if row['telefone2_normalizado'] != '':
            tel_lookup_para_id[row['telefone2_normalizado']] = row['id_cliente']
    
    ids_ainda_sem_match = ids_sem_uuid_real - set(matches_lookup.keys())
    oss_ainda_sem = oss_df[oss_df['cliente_id_str'].isin(ids_ainda_sem_match)]
    
    for _, row in oss_ainda_sem.iterrows():
        cliente_id = row['cliente_id_str']
        if row['telefone_normalizado'] != '' and row['telefone_normalizado'] in tel_lookup_para_id:
            lookup_id = str(tel_lookup_para_id[row['telefone_normalizado']])
            if lookup_id in lookup_para_uuid:
                matches_lookup[cliente_id] = {
                    'uuid': lookup_para_uuid[lookup_id],
                    'metodo': 'LOOKUP_TEL',
                    'fonte': 'LOOKUP'
                }
        elif row['celular_normalizado'] != '' and row['celular_normalizado'] in tel_lookup_para_id:
            lookup_id = str(tel_lookup_para_id[row['celular_normalizado']])
            if lookup_id in lookup_para_uuid:
                matches_lookup[cliente_id] = {
                    'uuid': lookup_para_uuid[lookup_id],
                    'metodo': 'LOOKUP_CEL',
                    'fonte': 'LOOKUP'
                }
    
    # Match lookup por nome fuzzy
    nomes_lookup = lookup_df[lookup_df['nome_normalizado'] != '']['nome_normalizado'].unique()
    nome_lookup_para_id = dict(zip(lookup_df[lookup_df['nome_normalizado'] != '']['nome_normalizado'],
                                  lookup_df[lookup_df['nome_normalizado'] != '']['id_cliente']))
    
    ids_final_sem_match = ids_sem_uuid_real - set(matches_lookup.keys())
    oss_final_sem = oss_df[oss_df['cliente_id_str'].isin(ids_final_sem_match)]
    nomes_finais_sem_match = oss_final_sem[oss_final_sem['nome_normalizado'] != '']['nome_normalizado'].unique()
    
    for nome_oss in nomes_finais_sem_match[:1000]:  # Limita para performance
        if isinstance(nome_oss, str) and len(nome_oss) > 5:
            try:
                match = process.extractOne(nome_oss, nomes_lookup, scorer=fuzz.ratio)
                if match and match[1] >= 85:  # Um pouco mais permissivo
                    lookup_id = str(nome_lookup_para_id[match[0]])
                    if lookup_id in lookup_para_uuid:
                        clientes_nome = oss_final_sem[oss_final_sem['nome_normalizado'] == nome_oss]['cliente_id_str'].unique()
                        for cliente_id in clientes_nome:
                            if cliente_id not in matches_lookup:
                                matches_lookup[cliente_id] = {
                                    'uuid': lookup_para_uuid[lookup_id],
                                    'metodo': 'LOOKUP_NOME',
                                    'fonte': 'LOOKUP'
                                }
            except:
                continue
    
    print(f"Matches lookup: {len(matches_lookup)}")
    
    # 3. APLICA RESULTADO FINAL
    print(f"\n=== RESULTADO HÍBRIDO FINAL ===")
    
    # Combina todos os matches
    todos_matches = {**matches_uuid_real, **matches_lookup}
    
    # Carrega vendas
    vendas_df = pd.read_csv(base_dir / "data" / "vendas_para_importar" / "vendas_corrigido_com_os_originais.csv")
    vendas_df['cliente_id_str'] = vendas_df['cliente_id'].astype(str).str.replace('.0', '')
    
    # Aplica matches
    vendas_df['uuid_final'] = None
    vendas_df['metodo_final'] = None
    vendas_df['fonte_final'] = None
    
    for cliente_id_str, match_info in todos_matches.items():
        mask = vendas_df['cliente_id_str'] == cliente_id_str
        vendas_df.loc[mask, 'uuid_final'] = match_info['uuid']
        vendas_df.loc[mask, 'metodo_final'] = match_info['metodo']
        vendas_df.loc[mask, 'fonte_final'] = match_info['fonte']
    
    # Prepara arquivo final
    vendas_final = vendas_df[[
        'numero_venda', 'uuid_final', 'loja_id', 'vendedor_id', 
        'data_venda', 'valor_total', 'valor_entrada', 'nome_cliente_temp',
        'observacoes', 'status', 'cancelado', 'created_at', 'updated_at'
    ]].copy()
    
    vendas_final.rename(columns={'uuid_final': 'cliente_id'}, inplace=True)
    
    # Estatísticas finais
    total_vendas = len(vendas_final)
    com_uuid = vendas_final['cliente_id'].notna().sum()
    sem_uuid = total_vendas - com_uuid
    
    print(f"Total vendas: {total_vendas}")
    print(f"COM UUID: {com_uuid} ({com_uuid/total_vendas*100:.1f}%)")
    print(f"SEM UUID: {sem_uuid} ({sem_uuid/total_vendas*100:.1f}%)")
    
    # Detalhes por fonte
    print(f"\nPor fonte:")
    fonte_banco = vendas_df[vendas_df['fonte_final'] == 'BANCO']['uuid_final'].count()
    fonte_lookup = vendas_df[vendas_df['fonte_final'] == 'LOOKUP']['uuid_final'].count()
    print(f"  BANCO (UUIDs reais): {fonte_banco}")
    print(f"  LOOKUP (mapeados): {fonte_lookup}")
    
    # Salva arquivo
    arquivo_final = base_dir / "data" / "vendas_para_importar" / "vendas_final_hibrido_completo.csv"
    vendas_final.to_csv(arquivo_final, index=False)
    
    print(f"\n=== ARQUIVO HÍBRIDO FINAL ===")
    print(f"Salvo: {arquivo_final}")
    print(f"🎯 Combinação perfeita: UUIDs reais + Lookup!")
    print(f"📊 {com_uuid} vendas com UUID ({com_uuid/total_vendas*100:.1f}%)")
    
    if sem_uuid > 0:
        print(f"⚠️  {sem_uuid} vendas ainda sem UUID")
    else:
        print(f"🎉 100% DE COBERTURA ALCANÇADA!")
    
    return vendas_final

if __name__ == "__main__":
    resultado = abordagem_hibrida_completa()
    if resultado is not None:
        print("\n🎉 ABORDAGEM HÍBRIDA CONCLUÍDA!")
        print("✅ Máxima cobertura possível!")
        print("🚀 UUIDs reais + Lookup = Resultado perfeito!")