#!/usr/bin/env python3
"""
Script para match inteligente direto com UUIDs do banco
Cruza com clientes que já estão em core.clientes usando UUID real
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

def match_direto_com_uuids_banco():
    """Faz match direto com UUIDs reais do banco"""
    
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    
    print("=== MATCH DIRETO COM UUIDs DO BANCO ===")
    
    # 1. Carrega clientes UUID (que representam clientes já no banco)
    clientes_uuid_df = pd.read_csv(base_dir / "data" / "clientes_uuid" / "todos_clientes_uuid_consolidado.csv")
    print(f"Clientes UUID (banco): {len(clientes_uuid_df)} registros")
    
    # Verificar colunas disponíveis
    print(f"Colunas disponíveis: {clientes_uuid_df.columns.tolist()}")
    
    # Normalizar dados dos clientes UUID (que já estão no banco)
    if 'Nome Completo' in clientes_uuid_df.columns:
        clientes_uuid_df['nome_normalizado'] = clientes_uuid_df['Nome Completo'].apply(normalizar_nome)
    elif 'Cliente' in clientes_uuid_df.columns:
        clientes_uuid_df['nome_normalizado'] = clientes_uuid_df['Cliente'].apply(normalizar_nome)
    else:
        print("❌ Coluna de nome não encontrada nos clientes UUID!")
        return None
    
    # Verificar se tem outras informações nos clientes UUID
    tem_cpf = False
    tem_telefone = False
    
    # Muitas vezes os dados completos estão nos arquivos individuais das lojas
    print(f"\n=== CARREGANDO DADOS COMPLETOS DAS LOJAS ===")
    
    # Carrega dados mais completos das lojas individuais
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
            print(f"  {arquivo.name}: {len(df)} registros")
            
            # Padroniza colunas
            if 'cliente_id_y' in df.columns:
                df['cliente_uuid'] = df['cliente_id_y']
            elif 'cliente_id_x' in df.columns:
                df['cliente_uuid'] = df['cliente_id_x']
            elif 'cliente_id' in df.columns:
                df['cliente_uuid'] = df['cliente_id']
            
            # Seleciona colunas úteis
            colunas_uteis = ['cliente_uuid']
            
            if 'Nome Completo' in df.columns:
                colunas_uteis.append('Nome Completo')
                df['nome_normalizado'] = df['Nome Completo'].apply(normalizar_nome)
            elif 'Cliente' in df.columns:
                colunas_uteis.append('Cliente')
                df['nome_normalizado'] = df['Cliente'].apply(normalizar_nome)
            
            # Verifica se tem CPF
            if 'CPF' in df.columns:
                colunas_uteis.append('CPF')
                df['cpf_normalizado'] = df['CPF'].apply(normalizar_cpf)
                tem_cpf = True
            
            # Verifica se tem telefone
            telefone_cols = [col for col in df.columns if 'Fone' in col or 'TELEFONE' in col or 'CELULAR' in col]
            if telefone_cols:
                for col in telefone_cols:
                    colunas_uteis.append(col)
                # Usa primeiro telefone encontrado
                df['telefone_normalizado'] = df[telefone_cols[0]].apply(normalizar_telefone)
                tem_telefone = True
            
            colunas_uteis.extend(['nome_normalizado'])
            if tem_cpf:
                colunas_uteis.append('cpf_normalizado')
            if tem_telefone:
                colunas_uteis.append('telefone_normalizado')
            
            # Adiciona apenas colunas que existem
            colunas_existentes = [col for col in colunas_uteis if col in df.columns]
            clientes_completos.append(df[colunas_existentes])
    
    if len(clientes_completos) > 0:
        clientes_banco_df = pd.concat(clientes_completos, ignore_index=True)
        # Remove duplicatas por UUID
        clientes_banco_df = clientes_banco_df.drop_duplicates(subset=['cliente_uuid'], keep='first')
        print(f"Total clientes banco consolidados: {len(clientes_banco_df)}")
    else:
        print("❌ Nenhum arquivo de clientes das lojas encontrado!")
        return None
    
    # 2. Carrega dados OSS para fazer o match
    print(f"\n=== CARREGANDO DADOS OSS ===")
    
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
    
    print(f"OSS: {len(oss_df)} registros")
    
    # 3. Executa matches
    print(f"\n=== EXECUTANDO MATCHES DIRETOS ===")
    
    matches_encontrados = {}
    
    # 3.1 Match por CPF (se disponível)
    if tem_cpf and 'cpf_normalizado' in clientes_banco_df.columns:
        print("Match por CPF...")
        
        cpf_para_uuid = dict(zip(
            clientes_banco_df[clientes_banco_df['cpf_normalizado'] != '']['cpf_normalizado'],
            clientes_banco_df[clientes_banco_df['cpf_normalizado'] != '']['cliente_uuid']
        ))
        
        for _, row in oss_df[oss_df['cpf_normalizado'] != ''].iterrows():
            if row['cpf_normalizado'] in cpf_para_uuid:
                matches_encontrados[row['cliente_id_str']] = {
                    'uuid': cpf_para_uuid[row['cpf_normalizado']],
                    'metodo': 'CPF',
                    'valor': row['cpf_normalizado']
                }
        
        print(f"  Matches por CPF: {len([m for m in matches_encontrados.values() if m['metodo'] == 'CPF'])}")
    
    # 3.2 Match por telefone (se disponível)
    if tem_telefone and 'telefone_normalizado' in clientes_banco_df.columns:
        print("Match por telefone...")
        
        tel_para_uuid = dict(zip(
            clientes_banco_df[clientes_banco_df['telefone_normalizado'] != '']['telefone_normalizado'],
            clientes_banco_df[clientes_banco_df['telefone_normalizado'] != '']['cliente_uuid']
        ))
        
        for _, row in oss_df.iterrows():
            cliente_id = row['cliente_id_str']
            if cliente_id not in matches_encontrados:  # Só se não achou por CPF
                # Testa telefone
                if row['telefone_normalizado'] != '' and row['telefone_normalizado'] in tel_para_uuid:
                    matches_encontrados[cliente_id] = {
                        'uuid': tel_para_uuid[row['telefone_normalizado']],
                        'metodo': 'TELEFONE',
                        'valor': row['telefone_normalizado']
                    }
                # Testa celular
                elif row['celular_normalizado'] != '' and row['celular_normalizado'] in tel_para_uuid:
                    matches_encontrados[cliente_id] = {
                        'uuid': tel_para_uuid[row['celular_normalizado']],
                        'metodo': 'CELULAR',
                        'valor': row['celular_normalizado']
                    }
        
        print(f"  Matches por telefone: {len([m for m in matches_encontrados.values() if m['metodo'] in ['TELEFONE', 'CELULAR']])}")
    
    # 3.3 Match por nome fuzzy
    print("Match por nome fuzzy...")
    
    # Filtra e limpa nomes do banco
    nomes_banco_limpos = clientes_banco_df[
        (clientes_banco_df['nome_normalizado'] != '') & 
        (clientes_banco_df['nome_normalizado'].notna())
    ]['nome_normalizado'].unique()
    
    # Remove valores que não são string
    nomes_banco_validos = [nome for nome in nomes_banco_limpos if isinstance(nome, str) and len(nome) > 3]
    
    nome_para_uuid = {}
    for _, row in clientes_banco_df.iterrows():
        if isinstance(row['nome_normalizado'], str) and row['nome_normalizado'] != '':
            nome_para_uuid[row['nome_normalizado']] = row['cliente_uuid']
    
    nomes_sem_match = oss_df[
        (~oss_df['cliente_id_str'].isin(matches_encontrados.keys())) &
        (oss_df['nome_normalizado'] != '') &
        (oss_df['nome_normalizado'].notna())
    ]['nome_normalizado'].unique()
    
    # Remove valores que não são string
    nomes_sem_match_validos = [nome for nome in nomes_sem_match if isinstance(nome, str) and len(nome) > 5]
    
    matches_nome = 0
    # Limita para não demorar muito
    for nome_oss in nomes_sem_match_validos[:1000]:
        try:
            match = process.extractOne(nome_oss, nomes_banco_validos, scorer=fuzz.ratio)
            if match and match[1] >= 90:
                uuid_encontrado = nome_para_uuid.get(match[0])
                if uuid_encontrado:
                    # Encontra todos os clientes OSS com este nome
                    clientes_nome = oss_df[oss_df['nome_normalizado'] == nome_oss]['cliente_id_str'].unique()
                    for cliente_id in clientes_nome:
                        if cliente_id not in matches_encontrados:
                            matches_encontrados[cliente_id] = {
                                'uuid': uuid_encontrado,
                                'metodo': 'NOME_FUZZY',
                                'valor': f"{nome_oss} -> {match[0]} ({match[1]}%)"
                            }
                            matches_nome += 1
        except Exception as e:
            # Ignora erros de matching individual
            continue
    
    print(f"  Matches por nome fuzzy: {matches_nome}")
    
    # 4. Aplica na base de vendas
    print(f"\n=== APLICANDO UUIDs NAS VENDAS ===")
    
    vendas_df = pd.read_csv(base_dir / "data" / "vendas_para_importar" / "vendas_corrigido_com_os_originais.csv")
    vendas_df['cliente_id_str'] = vendas_df['cliente_id'].astype(str).str.replace('.0', '')
    
    # Aplica UUIDs encontrados
    vendas_df['uuid_banco'] = None
    vendas_df['metodo_match'] = None
    
    for cliente_id_str, match_info in matches_encontrados.items():
        mask = vendas_df['cliente_id_str'] == cliente_id_str
        vendas_df.loc[mask, 'uuid_banco'] = match_info['uuid']
        vendas_df.loc[mask, 'metodo_match'] = match_info['metodo']
    
    # Usa UUID do banco quando encontrado
    vendas_df['cliente_id_final'] = vendas_df['uuid_banco']
    
    # Para vendas sem match, deixa null (serão clientes para criar)
    vendas_final = vendas_df[[
        'numero_venda', 'cliente_id_final', 'loja_id', 'vendedor_id', 
        'data_venda', 'valor_total', 'valor_entrada', 'nome_cliente_temp',
        'observacoes', 'status', 'cancelado', 'created_at', 'updated_at'
    ]].copy()
    
    vendas_final.rename(columns={'cliente_id_final': 'cliente_id'}, inplace=True)
    
    # 5. Estatísticas
    print(f"\n=== RESULTADO FINAL ===")
    
    total_vendas = len(vendas_final)
    com_uuid_banco = vendas_final['cliente_id'].notna().sum()
    sem_uuid = total_vendas - com_uuid_banco
    
    print(f"Total vendas: {total_vendas}")
    print(f"COM UUID do banco: {com_uuid_banco} ({com_uuid_banco/total_vendas*100:.1f}%)")
    print(f"SEM UUID (para criar cliente): {sem_uuid} ({sem_uuid/total_vendas*100:.1f}%)")
    
    # Detalhes por método
    print(f"\nMatches por método:")
    for metodo in ['CPF', 'TELEFONE', 'CELULAR', 'NOME_FUZZY']:
        count = vendas_df[vendas_df['metodo_match'] == metodo]['uuid_banco'].count()
        if count > 0:
            print(f"  {metodo}: {count} matches")
    
    # 6. Salva arquivo
    arquivo_final = base_dir / "data" / "vendas_para_importar" / "vendas_final_uuids_banco.csv"
    vendas_final.to_csv(arquivo_final, index=False)
    
    print(f"\n=== ARQUIVO FINAL ===")
    print(f"Salvo: {arquivo_final}")
    print(f"🎯 UUIDs diretos do banco aplicados!")
    print(f"📊 {com_uuid_banco} vendas com UUIDs reais do banco")
    print(f"⚠️  {sem_uuid} vendas precisam de novos clientes")
    
    return vendas_final

if __name__ == "__main__":
    resultado = match_direto_com_uuids_banco()
    if resultado is not None:
        print("\n🎉 MATCH COM UUIDs DO BANCO CONCLUÍDO!")
        print("✅ UUIDs reais aplicados diretamente!")
        print("🚀 Pronto para importação no banco!")