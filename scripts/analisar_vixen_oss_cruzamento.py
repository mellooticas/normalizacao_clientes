#!/usr/bin/env python3
"""
Análise do cruzamento VIXEN ↔ OSS
Hipótese: clientes VIXEN que voltaram a comprar em OSs podem ter sido perdidos no cruzamento
"""

import pandas as pd
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

def analisar_cruzamento_vixen_oss():
    """Analisa se o cruzamento VIXEN ↔ OSS perdeu clientes"""
    
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    
    print("=== ANÁLISE CRUZAMENTO VIXEN ↔ OSS ===")
    
    # 1. Carrega clientes lookup (tem origem VIXEN e OS)
    lookup_df = pd.read_csv(base_dir / "data" / "clientes" / "_consolidado" / "clientes_lookup.csv")
    
    print(f"Total clientes lookup: {len(lookup_df)}")
    
    # Separar por origem
    vixen_lookup = lookup_df[lookup_df['origem'] == 'VIXEN'].copy()
    oss_lookup = lookup_df[lookup_df['origem'] == 'OS'].copy()
    
    print(f"Clientes VIXEN no lookup: {len(vixen_lookup)}")
    print(f"Clientes OS no lookup: {len(oss_lookup)}")
    
    # 2. Carrega vendas sem UUID (nosso problema)
    vendas_df = pd.read_csv(base_dir / "data" / "vendas_para_importar" / "vendas_corrigido_com_os_originais.csv")
    vendas_df['cliente_id_str'] = vendas_df['cliente_id'].astype(str).str.replace('.0', '')
    
    # Carrega UUID consolidado para ver quais não têm
    uuid_consolidado = pd.read_csv(base_dir / "data" / "clientes_uuid" / "todos_clientes_uuid_consolidado.csv")
    uuid_consolidado['id_legado_str'] = uuid_consolidado['id_legado'].astype(str).str.replace('.0', '')
    uuid_unicos = set(uuid_consolidado['id_legado_str'])
    
    # IDs das vendas que não têm UUID
    vendas_sem_uuid_ids = set(vendas_df['cliente_id_str']) - uuid_unicos
    vendas_sem_uuid = vendas_df[vendas_df['cliente_id_str'].isin(vendas_sem_uuid_ids)]
    
    print(f"\nVendas sem UUID: {len(vendas_sem_uuid)}")
    print(f"IDs únicos sem UUID: {len(vendas_sem_uuid_ids)}")
    
    # 3. Análise: esses IDs sem UUID estão no lookup original?
    lookup_todos_ids = set(lookup_df['id_cliente'].astype(str))
    
    # IDs sem UUID que ESTÃO no lookup (deveriam ter UUID!)
    sem_uuid_mas_no_lookup = vendas_sem_uuid_ids & lookup_todos_ids
    
    print(f"\n🔍 IDs sem UUID que ESTÃO no lookup: {len(sem_uuid_mas_no_lookup)}")
    print(f"Isso representa {len(sem_uuid_mas_no_lookup)/len(vendas_sem_uuid_ids)*100:.1f}% dos IDs sem UUID")
    
    if len(sem_uuid_mas_no_lookup) > 0:
        print(f"⚠️  PROBLEMA ENCONTRADO! Esses IDs deveriam ter UUID!")
        
        # Analisa a origem desses IDs problemáticos
        lookup_problematico = lookup_df[lookup_df['id_cliente'].astype(str).isin(sem_uuid_mas_no_lookup)]
        origem_problematica = lookup_problematico['origem'].value_counts()
        
        print(f"\nOrigem dos IDs problemáticos:")
        for origem, count in origem_problematica.items():
            print(f"  {origem}: {count}")
    
    # 4. TENTA MATCH DIRETO VIXEN → VENDAS SEM UUID
    print(f"\n=== TENTATIVA DE MATCH DIRETO VIXEN → VENDAS SEM UUID ===")
    
    # Normaliza dados VIXEN
    vixen_lookup['cpf_normalizado'] = vixen_lookup['cpf'].apply(normalizar_cpf)
    vixen_lookup['telefone1_normalizado'] = vixen_lookup['telefone1'].apply(normalizar_telefone)
    vixen_lookup['telefone2_normalizado'] = vixen_lookup['telefone2'].apply(normalizar_telefone)
    vixen_lookup['nome_normalizado'] = vixen_lookup['nome'].apply(normalizar_nome)
    
    # Carrega dados OSS originais para comparar
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
    
    # Filtra OSS apenas com IDs sem UUID
    oss_sem_uuid = oss_df[oss_df['cliente_id_str'].isin(vendas_sem_uuid_ids)]
    
    print(f"OSS sem UUID para analisar: {len(oss_sem_uuid)}")
    
    # MATCH POR CPF
    matches_cpf = {}
    if len(vixen_lookup[vixen_lookup['cpf_normalizado'] != '']) > 0:
        cpf_vixen_para_id = dict(zip(
            vixen_lookup[vixen_lookup['cpf_normalizado'] != '']['cpf_normalizado'],
            vixen_lookup[vixen_lookup['cpf_normalizado'] != '']['id_cliente']
        ))
        
        for _, row in oss_sem_uuid[oss_sem_uuid['cpf_normalizado'] != ''].iterrows():
            if row['cpf_normalizado'] in cpf_vixen_para_id:
                vixen_id = cpf_vixen_para_id[row['cpf_normalizado']]
                matches_cpf[row['cliente_id_str']] = {
                    'vixen_id': vixen_id,
                    'oss_nome': row['NOME:'],
                    'metodo': 'CPF'
                }
    
    print(f"Matches por CPF OSS → VIXEN: {len(matches_cpf)}")
    
    # MATCH POR TELEFONE
    matches_telefone = {}
    tel_vixen_para_id = {}
    for _, row in vixen_lookup.iterrows():
        if row['telefone1_normalizado'] != '':
            tel_vixen_para_id[row['telefone1_normalizado']] = row['id_cliente']
        if row['telefone2_normalizado'] != '':
            tel_vixen_para_id[row['telefone2_normalizado']] = row['id_cliente']
    
    for _, row in oss_sem_uuid.iterrows():
        oss_id = row['cliente_id_str']
        if oss_id not in matches_cpf:  # Só se não teve match por CPF
            if row['telefone_normalizado'] != '' and row['telefone_normalizado'] in tel_vixen_para_id:
                vixen_id = tel_vixen_para_id[row['telefone_normalizado']]
                matches_telefone[oss_id] = {
                    'vixen_id': vixen_id,
                    'oss_nome': row['NOME:'],
                    'metodo': 'TELEFONE'
                }
            elif row['celular_normalizado'] != '' and row['celular_normalizado'] in tel_vixen_para_id:
                vixen_id = tel_vixen_para_id[row['celular_normalizado']]
                matches_telefone[oss_id] = {
                    'vixen_id': vixen_id,
                    'oss_nome': row['NOME:'],
                    'metodo': 'CELULAR'
                }
    
    print(f"Matches por TELEFONE OSS → VIXEN: {len(matches_telefone)}")
    
    # MATCH POR NOME (fuzzy)
    matches_nome = {}
    nomes_vixen = vixen_lookup[vixen_lookup['nome_normalizado'] != '']['nome_normalizado'].unique()
    nome_vixen_para_id = dict(zip(
        vixen_lookup[vixen_lookup['nome_normalizado'] != '']['nome_normalizado'],
        vixen_lookup[vixen_lookup['nome_normalizado'] != '']['id_cliente']
    ))
    
    oss_sem_match = oss_sem_uuid[
        (~oss_sem_uuid['cliente_id_str'].isin(matches_cpf.keys())) &
        (~oss_sem_uuid['cliente_id_str'].isin(matches_telefone.keys()))
    ]
    
    nomes_oss_sem_match = oss_sem_match[
        oss_sem_match['nome_normalizado'] != ''
    ]['nome_normalizado'].unique()
    
    print(f"Tentando match por nome para {len(nomes_oss_sem_match)} nomes únicos...")
    
    for nome_oss in nomes_oss_sem_match[:500]:  # Limita para performance
        if isinstance(nome_oss, str) and len(nome_oss) > 5:
            try:
                match = process.extractOne(nome_oss, nomes_vixen, scorer=fuzz.ratio)
                if match and match[1] >= 85:  # 85% similaridade
                    vixen_id = nome_vixen_para_id[match[0]]
                    # Encontra todos os OSS com esse nome
                    oss_com_nome = oss_sem_match[oss_sem_match['nome_normalizado'] == nome_oss]
                    for _, row in oss_com_nome.iterrows():
                        if row['cliente_id_str'] not in matches_nome:
                            matches_nome[row['cliente_id_str']] = {
                                'vixen_id': vixen_id,
                                'oss_nome': row['NOME:'],
                                'vixen_nome': match[0],
                                'similaridade': match[1],
                                'metodo': 'NOME_FUZZY'
                            }
            except:
                continue
    
    print(f"Matches por NOME OSS → VIXEN: {len(matches_nome)}")
    
    # 5. RESULTADO TOTAL
    todos_matches = {**matches_cpf, **matches_telefone, **matches_nome}
    
    print(f"\n=== RESULTADO CRUZAMENTO VIXEN → OSS ===")
    print(f"Total matches encontrados: {len(todos_matches)}")
    print(f"IDs sem UUID que conseguimos linkar ao VIXEN: {len(todos_matches)}")
    print(f"Percentual recuperado: {len(todos_matches)/len(vendas_sem_uuid_ids)*100:.1f}%")
    
    if len(todos_matches) > 0:
        print(f"\n🎉 SUCESSO! Encontramos {len(todos_matches)} clientes VIXEN que voltaram a comprar!")
        print(f"Isso confirma sua hipótese!")
        
        # Amostra dos matches
        print(f"\nAmostra dos matches encontrados:")
        count = 0
        for oss_id, match_info in todos_matches.items():
            if count < 10:
                print(f"  OSS ID: {oss_id} → VIXEN ID: {match_info['vixen_id']} [{match_info['metodo']}]")
                print(f"    Nome OSS: {match_info['oss_nome']}")
                if 'vixen_nome' in match_info:
                    print(f"    Nome VIXEN: {match_info['vixen_nome']} (sim: {match_info['similaridade']}%)")
                count += 1
    
    return todos_matches

if __name__ == "__main__":
    resultado = analisar_cruzamento_vixen_oss()
    print(f"\n✅ Análise concluída! Encontrados {len(resultado)} matches VIXEN → OSS")