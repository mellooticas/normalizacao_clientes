#!/usr/bin/env python3
"""
VERSÃO FINAL HÍBRIDA COMPLETA
Combina todas as estratégias para alcançar máxima cobertura:
1. UUIDs reais do banco
2. Matches VIXEN ↔ OSS perdidos (descoberta do usuário)
3. Lookup tradicional  
4. UUIDs novos para clientes realmente novos
"""

import pandas as pd
from pathlib import Path
import uuid
import re
from fuzzywuzzy import fuzz, process

def normalizar_cpf(cpf):
    if pd.isna(cpf):
        return ""
    cpf_str = str(cpf).strip()
    cpf_limpo = re.sub(r'[^\d]', '', cpf_str)
    return cpf_limpo if len(cpf_limpo) == 11 else ""

def normalizar_telefone(telefone):
    if pd.isna(telefone):
        return ""
    tel_str = str(telefone).strip()
    tel_limpo = re.sub(r'[^\d]', '', tel_str)
    if tel_limpo.startswith('55') and len(tel_limpo) > 11:
        tel_limpo = tel_limpo[2:]
    return tel_limpo if len(tel_limpo) >= 10 else ""

def normalizar_nome(nome):
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

def estrategia_final_completa():
    """Estratégia final que combina todas as abordagens"""
    
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    
    print("🚀 === ESTRATÉGIA FINAL HÍBRIDA COMPLETA === 🚀")
    
    # FASE 1: Carrega dados OSS
    print(f"\n=== FASE 1: CARREGANDO DADOS OSS ===")
    
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
    oss_df['cliente_id_str'] = oss_df['cliente_id'].astype(str).str.replace('.0', '')
    oss_df['cpf_normalizado'] = oss_df['CPF'].apply(normalizar_cpf)
    oss_df['telefone_normalizado'] = oss_df['TELEFONE :'].apply(normalizar_telefone)
    oss_df['celular_normalizado'] = oss_df['CELULAR:'].apply(normalizar_telefone)
    oss_df['nome_normalizado'] = oss_df['NOME:'].apply(normalizar_nome)
    
    print(f"OSS carregados: {len(oss_df)} registros, {len(oss_df['cliente_id_str'].unique())} únicos")
    
    # FASE 2: Estratégia 1 - UUIDs reais do banco
    print(f"\n=== FASE 2: ESTRATÉGIA 1 - UUIDs REAIS DO BANCO ===")
    
    arquivos_lojas = [
        base_dir / "data" / "clientes_uuid" / "clientes_suzano.csv",
        base_dir / "data" / "clientes_uuid" / "clientes_maua.csv",
        base_dir / "data" / "clientes_uuid" / "clientes_perus.csv",
        base_dir / "data" / "clientes_uuid" / "clientes_rio_pequeno.csv",
        base_dir / "data" / "clientes_uuid" / "clientes_sao_mateus.csv",
        base_dir / "data" / "clientes_uuid" / "clientes_suzano2.csv"
    ]
    
    clientes_completos = []
    for arquivo in arquivos_lojas:
        if arquivo.exists():
            df = pd.read_csv(arquivo)
            
            if 'cliente_id_y' in df.columns:
                df['cliente_uuid'] = df['cliente_id_y']
            elif 'cliente_id_x' in df.columns:
                df['cliente_uuid'] = df['cliente_id_x']
            elif 'cliente_id' in df.columns:
                df['cliente_uuid'] = df['cliente_id']
            
            if 'Nome Completo' in df.columns:
                df['nome_normalizado'] = df['Nome Completo'].apply(normalizar_nome)
            elif 'Cliente' in df.columns:
                df['nome_normalizado'] = df['Cliente'].apply(normalizar_nome)
            else:
                df['nome_normalizado'] = ""
            
            if 'Fone' in df.columns:
                df['telefone_normalizado'] = df['Fone'].apply(normalizar_telefone)
            else:
                df['telefone_normalizado'] = ""
            
            df['cpf_normalizado'] = ""  # Não tem CPF nos arquivos de clientes
            
            clientes_completos.append(df[['cliente_uuid', 'nome_normalizado', 'cpf_normalizado', 'telefone_normalizado']])
    
    clientes_banco_df = pd.concat(clientes_completos, ignore_index=True)
    clientes_banco_df = clientes_banco_df.drop_duplicates(subset=['cliente_uuid'], keep='first')
    
    matches_banco = {}
    
    # Match por telefone
    tel_para_uuid = {}
    for _, row in clientes_banco_df.iterrows():
        if row['telefone_normalizado'] != '':
            tel_para_uuid[row['telefone_normalizado']] = row['cliente_uuid']
    
    for _, row in oss_df.iterrows():
        cliente_id = row['cliente_id_str']
        if row['telefone_normalizado'] != '' and row['telefone_normalizado'] in tel_para_uuid:
            matches_banco[cliente_id] = {
                'uuid': tel_para_uuid[row['telefone_normalizado']],
                'metodo': 'BANCO_TEL',
                'fonte': 'BANCO_REAL'
            }
        elif row['celular_normalizado'] != '' and row['celular_normalizado'] in tel_para_uuid:
            matches_banco[cliente_id] = {
                'uuid': tel_para_uuid[row['celular_normalizado']],
                'metodo': 'BANCO_CEL',
                'fonte': 'BANCO_REAL'
            }
    
    # Match por nome fuzzy
    nomes_banco_validos = [nome for nome in clientes_banco_df['nome_normalizado'].unique() 
                          if isinstance(nome, str) and len(nome) > 3]
    nome_para_uuid = dict(zip(clientes_banco_df['nome_normalizado'], clientes_banco_df['cliente_uuid']))
    
    nomes_sem_match = oss_df[
        (~oss_df['cliente_id_str'].isin(matches_banco.keys())) &
        (oss_df['nome_normalizado'] != '') &
        (oss_df['nome_normalizado'].notna())
    ]['nome_normalizado'].unique()
    
    for nome_oss in nomes_sem_match[:500]:  # Limita performance
        if isinstance(nome_oss, str) and len(nome_oss) > 5:
            try:
                match = process.extractOne(nome_oss, nomes_banco_validos, scorer=fuzz.ratio)
                if match and match[1] >= 90:
                    uuid_encontrado = nome_para_uuid.get(match[0])
                    if uuid_encontrado:
                        clientes_nome = oss_df[oss_df['nome_normalizado'] == nome_oss]['cliente_id_str'].unique()
                        for cliente_id in clientes_nome:
                            if cliente_id not in matches_banco:
                                matches_banco[cliente_id] = {
                                    'uuid': uuid_encontrado,
                                    'metodo': 'BANCO_NOME',
                                    'fonte': 'BANCO_REAL'
                                }
            except:
                continue
    
    print(f"Matches banco real: {len(matches_banco)}")
    
    # FASE 3: Estratégia 2 - Matches VIXEN ↔ OSS perdidos (descoberta do usuário!)
    print(f"\n=== FASE 3: ESTRATÉGIA 2 - MATCHES VIXEN ↔ OSS PERDIDOS ===")
    
    lookup_df = pd.read_csv(base_dir / "data" / "clientes" / "_consolidado" / "clientes_lookup.csv")
    vixen_lookup = lookup_df[lookup_df['origem'] == 'VIXEN'].copy()
    
    vixen_lookup['cpf_normalizado'] = vixen_lookup['cpf'].apply(normalizar_cpf)
    vixen_lookup['telefone1_normalizado'] = vixen_lookup['telefone1'].apply(normalizar_telefone)
    vixen_lookup['telefone2_normalizado'] = vixen_lookup['telefone2'].apply(normalizar_telefone)
    vixen_lookup['nome_normalizado'] = vixen_lookup['nome'].apply(normalizar_nome)
    
    # UUID consolidado para mapear VIXEN IDs
    uuid_consolidado = pd.read_csv(base_dir / "data" / "clientes_uuid" / "todos_clientes_uuid_consolidado.csv")
    uuid_consolidado['id_legado_str'] = uuid_consolidado['id_legado'].astype(str).str.replace('.0', '')
    vixen_para_uuid = dict(zip(uuid_consolidado['id_legado_str'], uuid_consolidado['cliente_id']))
    
    matches_vixen = {}
    
    # OSS que ainda não têm match
    oss_sem_banco = oss_df[~oss_df['cliente_id_str'].isin(matches_banco.keys())]
    
    # Match VIXEN por telefone
    tel_vixen_para_id = {}
    for _, row in vixen_lookup.iterrows():
        if row['telefone1_normalizado'] != '':
            tel_vixen_para_id[row['telefone1_normalizado']] = row['id_cliente']
        if row['telefone2_normalizado'] != '':
            tel_vixen_para_id[row['telefone2_normalizado']] = row['id_cliente']
    
    for _, row in oss_sem_banco.iterrows():
        cliente_id = row['cliente_id_str']
        vixen_id_encontrado = None
        
        if row['telefone_normalizado'] != '' and row['telefone_normalizado'] in tel_vixen_para_id:
            vixen_id_encontrado = tel_vixen_para_id[row['telefone_normalizado']]
        elif row['celular_normalizado'] != '' and row['celular_normalizado'] in tel_vixen_para_id:
            vixen_id_encontrado = tel_vixen_para_id[row['celular_normalizado']]
        
        if vixen_id_encontrado:
            vixen_id_str = str(vixen_id_encontrado)
            if vixen_id_str in vixen_para_uuid:
                matches_vixen[cliente_id] = {
                    'uuid': vixen_para_uuid[vixen_id_str],
                    'metodo': 'VIXEN_TEL',
                    'fonte': 'VIXEN_RECUPERADO'
                }
    
    # Match VIXEN por nome fuzzy
    nomes_vixen = vixen_lookup[vixen_lookup['nome_normalizado'] != '']['nome_normalizado'].unique()
    nome_vixen_para_id = dict(zip(
        vixen_lookup[vixen_lookup['nome_normalizado'] != '']['nome_normalizado'],
        vixen_lookup[vixen_lookup['nome_normalizado'] != '']['id_cliente']
    ))
    
    oss_ainda_sem = oss_df[
        (~oss_df['cliente_id_str'].isin(matches_banco.keys())) &
        (~oss_df['cliente_id_str'].isin(matches_vixen.keys()))
    ]
    
    nomes_oss_sem = oss_ainda_sem[oss_ainda_sem['nome_normalizado'] != '']['nome_normalizado'].unique()
    
    for nome_oss in nomes_oss_sem[:800]:  # Mais agressivo
        if isinstance(nome_oss, str) and len(nome_oss) > 5:
            try:
                match = process.extractOne(nome_oss, nomes_vixen, scorer=fuzz.ratio)
                if match and match[1] >= 80:  # Mais permissivo
                    vixen_id = nome_vixen_para_id[match[0]]
                    vixen_id_str = str(vixen_id)
                    if vixen_id_str in vixen_para_uuid:
                        clientes_nome = oss_ainda_sem[oss_ainda_sem['nome_normalizado'] == nome_oss]['cliente_id_str'].unique()
                        for cliente_id in clientes_nome:
                            if cliente_id not in matches_vixen:
                                matches_vixen[cliente_id] = {
                                    'uuid': vixen_para_uuid[vixen_id_str],
                                    'metodo': 'VIXEN_NOME',
                                    'fonte': 'VIXEN_RECUPERADO'
                                }
            except:
                continue
    
    print(f"Matches VIXEN recuperados: {len(matches_vixen)}")
    
    # FASE 4: Estratégia 3 - Lookup tradicional
    print(f"\n=== FASE 4: ESTRATÉGIA 3 - LOOKUP TRADICIONAL ===")
    
    matches_lookup = {}
    
    # OSS que ainda não têm match
    todos_matches_anteriores = {**matches_banco, **matches_vixen}
    oss_sem_match = oss_df[~oss_df['cliente_id_str'].isin(todos_matches_anteriores.keys())]
    
    # Match lookup direto por ID (se o OSS ID está no lookup)
    lookup_todos_ids = set(lookup_df['id_cliente'].astype(str))
    
    for _, row in oss_sem_match.iterrows():
        cliente_id = row['cliente_id_str']
        if cliente_id in lookup_todos_ids:
            if cliente_id in vixen_para_uuid:
                matches_lookup[cliente_id] = {
                    'uuid': vixen_para_uuid[cliente_id],
                    'metodo': 'LOOKUP_DIRETO',
                    'fonte': 'LOOKUP_TRADICIONAL'
                }
    
    print(f"Matches lookup tradicional: {len(matches_lookup)}")
    
    # FASE 5: Estratégia 4 - UUIDs novos para clientes realmente novos
    print(f"\n=== FASE 5: ESTRATÉGIA 4 - UUIDs NOVOS ===")
    
    todos_matches = {**matches_banco, **matches_vixen, **matches_lookup}
    clientes_sem_uuid = set(oss_df['cliente_id_str']) - set(todos_matches.keys())
    
    matches_novos = {}
    for cliente_id in clientes_sem_uuid:
        novo_uuid = str(uuid.uuid4())
        matches_novos[cliente_id] = {
            'uuid': novo_uuid,
            'metodo': 'NOVO_UUID',
            'fonte': 'CLIENTE_NOVO'
        }
    
    print(f"UUIDs novos criados: {len(matches_novos)}")
    
    # FASE 6: Resultado final
    print(f"\n=== FASE 6: RESULTADO FINAL ===")
    
    resultado_final = {**matches_banco, **matches_vixen, **matches_lookup, **matches_novos}
    
    # Aplica nas vendas
    vendas_df = pd.read_csv(base_dir / "data" / "vendas_para_importar" / "vendas_corrigido_com_os_originais.csv")
    vendas_df['cliente_id_str'] = vendas_df['cliente_id'].astype(str).str.replace('.0', '')
    
    vendas_df['uuid_final'] = None
    vendas_df['metodo_final'] = None
    vendas_df['fonte_final'] = None
    
    for cliente_id_str, match_info in resultado_final.items():
        mask = vendas_df['cliente_id_str'] == cliente_id_str
        vendas_df.loc[mask, 'uuid_final'] = match_info['uuid']
        vendas_df.loc[mask, 'metodo_final'] = match_info['metodo']
        vendas_df.loc[mask, 'fonte_final'] = match_info['fonte']
    
    # Arquivo final
    vendas_final = vendas_df[[
        'numero_venda', 'uuid_final', 'loja_id', 'vendedor_id', 
        'data_venda', 'valor_total', 'valor_entrada', 'nome_cliente_temp',
        'observacoes', 'status', 'cancelado', 'created_at', 'updated_at'
    ]].copy()
    
    vendas_final.rename(columns={'uuid_final': 'cliente_id'}, inplace=True)
    
    # Estatísticas
    total_vendas = len(vendas_final)
    com_uuid = vendas_final['cliente_id'].notna().sum()
    
    print(f"RESULTADO ESTRATÉGIA FINAL:")
    print(f"  Total vendas: {total_vendas}")
    print(f"  COM UUID: {com_uuid} ({com_uuid/total_vendas*100:.1f}%)")
    print(f"  SEM UUID: {total_vendas - com_uuid}")
    
    print(f"\nPor estratégia:")
    banco_count = vendas_df[vendas_df['fonte_final'] == 'BANCO_REAL']['uuid_final'].count()
    vixen_count = vendas_df[vendas_df['fonte_final'] == 'VIXEN_RECUPERADO']['uuid_final'].count()
    lookup_count = vendas_df[vendas_df['fonte_final'] == 'LOOKUP_TRADICIONAL']['uuid_final'].count()
    novo_count = vendas_df[vendas_df['fonte_final'] == 'CLIENTE_NOVO']['uuid_final'].count()
    
    print(f"  BANCO REAL: {banco_count}")
    print(f"  VIXEN RECUPERADO: {vixen_count} 🎯")
    print(f"  LOOKUP TRADICIONAL: {lookup_count}")
    print(f"  CLIENTES NOVOS: {novo_count}")
    
    # Salva
    arquivo_final = base_dir / "data" / "vendas_para_importar" / "vendas_final_estrategia_completa.csv"
    vendas_final.to_csv(arquivo_final, index=False)
    
    print(f"\n🚀 ESTRATÉGIA FINAL CONCLUÍDA!")
    print(f"📁 Arquivo: {arquivo_final}")
    
    if com_uuid == total_vendas:
        print(f"🎉 100% DE COBERTURA ALCANÇADA!")
    else:
        print(f"📊 {com_uuid/total_vendas*100:.1f}% de cobertura")
    
    print(f"✅ Sua descoberta sobre VIXEN ↔ OSS foi incorporada!")
    
    return vendas_final

if __name__ == "__main__":
    resultado = estrategia_final_completa()
    print(f"\n🎯 MISSÃO CUMPRIDA! {len(resultado)} vendas processadas!")