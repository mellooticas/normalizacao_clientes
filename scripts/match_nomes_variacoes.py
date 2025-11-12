#!/usr/bin/env python3
"""
Match agressivo por nomes com pequenas variações
Foca em capturar casos como: CARLA ARIANE FERREIR vs CARLA ARIANE FERREIRA LOPES
"""

import pandas as pd
from pathlib import Path
import re
from fuzzywuzzy import fuzz, process
import uuid

def normalizar_nome_agressivo(nome):
    """Normalização mais agressiva para matching"""
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
    
    # Remove pontuação e caracteres especiais
    nome = re.sub(r'[^A-Z\s]', '', nome)
    
    # Remove múltiplos espaços
    nome = re.sub(r'\s+', ' ', nome)
    
    # Remove palavras muito comuns que podem causar falsos positivos
    palavras_comuns = ['DA', 'DE', 'DO', 'DOS', 'DAS', 'E', 'O', 'A', 'AS', 'OS']
    palavras = nome.split()
    palavras_filtradas = [p for p in palavras if p not in palavras_comuns or len(palavras) <= 3]
    
    return ' '.join(palavras_filtradas).strip()

def extrair_primeiro_ultimo_nome(nome):
    """Extrai primeiro e último nome para matching mais flexível"""
    if not nome:
        return ""
    palavras = nome.split()
    if len(palavras) == 1:
        return palavras[0]
    elif len(palavras) == 2:
        return f"{palavras[0]} {palavras[1]}"
    else:
        return f"{palavras[0]} {palavras[-1]}"

def match_nomes_variacoes():
    """Faz match específico para nomes com pequenas variações"""
    
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    
    print("🎯 === MATCH AGRESSIVO NOMES COM VARIAÇÕES ===")
    
    # 1. Carrega dados OSS
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
    oss_df['nome_normalizado'] = oss_df['NOME:'].apply(normalizar_nome_agressivo)
    oss_df['nome_primeiro_ultimo'] = oss_df['nome_normalizado'].apply(extrair_primeiro_ultimo_nome)
    
    print(f"OSS carregados: {len(oss_df)} registros")
    
    # 2. Identifica OSS sem UUID
    uuid_consolidado = pd.read_csv(base_dir / "data" / "clientes_uuid" / "todos_clientes_uuid_consolidado.csv")
    uuid_consolidado['id_legado_str'] = uuid_consolidado['id_legado'].astype(str).str.replace('.0', '')
    uuid_existentes = set(uuid_consolidado['id_legado_str'])
    
    oss_sem_uuid = oss_df[~oss_df['cliente_id_str'].isin(uuid_existentes)].copy()
    print(f"OSS sem UUID: {len(oss_sem_uuid)}")
    
    # 3. Carrega VIXEN do lookup
    lookup_df = pd.read_csv(base_dir / "data" / "clientes" / "_consolidado" / "clientes_lookup.csv")
    vixen_lookup = lookup_df[lookup_df['origem'] == 'VIXEN'].copy()
    vixen_lookup['nome_normalizado'] = vixen_lookup['nome'].apply(normalizar_nome_agressivo)
    vixen_lookup['nome_primeiro_ultimo'] = vixen_lookup['nome_normalizado'].apply(extrair_primeiro_ultimo_nome)
    
    print(f"VIXEN carregados: {len(vixen_lookup)}")
    
    # 4. Mapeamento VIXEN para UUID
    vixen_para_uuid = dict(zip(uuid_consolidado['id_legado_str'], uuid_consolidado['cliente_id']))
    
    # 5. ESTRATÉGIAS DE MATCHING PROGRESSIVAS
    
    # 5.1. Match exato por nome normalizado
    print(f"\n=== MATCH EXATO NORMALIZADO ===")
    matches_exato = {}
    
    nome_vixen_para_id = dict(zip(
        vixen_lookup[vixen_lookup['nome_normalizado'] != '']['nome_normalizado'],
        vixen_lookup[vixen_lookup['nome_normalizado'] != '']['id_cliente']
    ))
    
    for _, row in oss_sem_uuid.iterrows():
        if row['nome_normalizado'] != '' and row['nome_normalizado'] in nome_vixen_para_id:
            vixen_id = str(nome_vixen_para_id[row['nome_normalizado']])
            if vixen_id in vixen_para_uuid:
                matches_exato[row['cliente_id_str']] = {
                    'uuid': vixen_para_uuid[vixen_id],
                    'vixen_id': vixen_id,
                    'metodo': 'NOME_EXATO',
                    'oss_nome': row['NOME:'],
                    'vixen_nome': row['nome_normalizado']
                }
    
    print(f"Matches exatos: {len(matches_exato)}")
    
    # 5.2. Match por primeiro + último nome
    print(f"\n=== MATCH PRIMEIRO + ÚLTIMO NOME ===")
    matches_primeiro_ultimo = {}
    
    primeiro_ultimo_vixen_para_id = dict(zip(
        vixen_lookup[vixen_lookup['nome_primeiro_ultimo'] != '']['nome_primeiro_ultimo'],
        vixen_lookup[vixen_lookup['nome_primeiro_ultimo'] != '']['id_cliente']
    ))
    
    oss_restantes = oss_sem_uuid[~oss_sem_uuid['cliente_id_str'].isin(matches_exato.keys())]
    
    for _, row in oss_restantes.iterrows():
        if row['nome_primeiro_ultimo'] != '' and row['nome_primeiro_ultimo'] in primeiro_ultimo_vixen_para_id:
            vixen_id = str(primeiro_ultimo_vixen_para_id[row['nome_primeiro_ultimo']])
            if vixen_id in vixen_para_uuid:
                matches_primeiro_ultimo[row['cliente_id_str']] = {
                    'uuid': vixen_para_uuid[vixen_id],
                    'vixen_id': vixen_id,
                    'metodo': 'PRIMEIRO_ULTIMO',
                    'oss_nome': row['NOME:'],
                    'vixen_nome': row['nome_primeiro_ultimo']
                }
    
    print(f"Matches primeiro+último: {len(matches_primeiro_ultimo)}")
    
    # 5.3. Match fuzzy progressivo (várias similaridades)
    print(f"\n=== MATCH FUZZY PROGRESSIVO ===")
    
    matches_fuzzy = {}
    nomes_vixen_unicos = vixen_lookup[vixen_lookup['nome_normalizado'] != '']['nome_normalizado'].unique()
    
    # Remove matches já encontrados
    todos_matches_anteriores = {**matches_exato, **matches_primeiro_ultimo}
    oss_para_fuzzy = oss_sem_uuid[~oss_sem_uuid['cliente_id_str'].isin(todos_matches_anteriores.keys())]
    
    nomes_oss_para_fuzzy = oss_para_fuzzy[oss_para_fuzzy['nome_normalizado'] != '']['nome_normalizado'].unique()
    
    print(f"Nomes OSS para fuzzy: {len(nomes_oss_para_fuzzy)}")
    print(f"Nomes VIXEN disponíveis: {len(nomes_vixen_unicos)}")
    
    # Tenta diferentes níveis de similaridade
    similaridades = [95, 90, 85, 80, 75]
    
    for similaridade_min in similaridades:
        print(f"\n  Tentando similaridade >= {similaridade_min}%...")
        matches_nivel = 0
        
        for nome_oss in nomes_oss_para_fuzzy[:1000]:  # Limita para performance
            if isinstance(nome_oss, str) and len(nome_oss) > 3:
                try:
                    # Testa múltiplos scorers
                    match_ratio = process.extractOne(nome_oss, nomes_vixen_unicos, scorer=fuzz.ratio)
                    match_partial = process.extractOne(nome_oss, nomes_vixen_unicos, scorer=fuzz.partial_ratio)
                    match_token = process.extractOne(nome_oss, nomes_vixen_unicos, scorer=fuzz.token_sort_ratio)
                    
                    # Escolhe o melhor match
                    melhor_match = None
                    melhor_score = 0
                    
                    for match in [match_ratio, match_partial, match_token]:
                        if match and match[1] >= similaridade_min and match[1] > melhor_score:
                            melhor_match = match
                            melhor_score = match[1]
                    
                    if melhor_match:
                        nome_vixen_encontrado = melhor_match[0]
                        vixen_id = str(nome_vixen_para_id.get(nome_vixen_encontrado))
                        
                        if vixen_id in vixen_para_uuid:
                            # Encontra todos os OSS com esse nome
                            oss_com_nome = oss_para_fuzzy[oss_para_fuzzy['nome_normalizado'] == nome_oss]
                            
                            for _, row in oss_com_nome.iterrows():
                                cliente_id = row['cliente_id_str']
                                if cliente_id not in matches_fuzzy:
                                    matches_fuzzy[cliente_id] = {
                                        'uuid': vixen_para_uuid[vixen_id],
                                        'vixen_id': vixen_id,
                                        'metodo': f'FUZZY_{similaridade_min}',
                                        'oss_nome': row['NOME:'],
                                        'vixen_nome': nome_vixen_encontrado,
                                        'similaridade': melhor_score
                                    }
                                    matches_nivel += 1
                
                except Exception as e:
                    continue
        
        print(f"    Matches nível {similaridade_min}%: {matches_nivel}")
        
        if matches_nivel == 0:
            break  # Não vale a pena tentar similaridades menores
    
    print(f"Total matches fuzzy: {len(matches_fuzzy)}")
    
    # 6. RESULTADO FINAL
    print(f"\n=== RESULTADO FINAL MATCHING NOMES ===")
    
    todos_matches_nomes = {**matches_exato, **matches_primeiro_ultimo, **matches_fuzzy}
    
    print(f"Total matches por variações de nomes: {len(todos_matches_nomes)}")
    print(f"  Exatos: {len(matches_exato)}")
    print(f"  Primeiro+Último: {len(matches_primeiro_ultimo)}")
    print(f"  Fuzzy: {len(matches_fuzzy)}")
    
    # 7. Exemplos dos matches encontrados
    print(f"\n=== EXEMPLOS DOS MATCHES ENCONTRADOS ===")
    
    count = 0
    for cliente_id, match_info in todos_matches_nomes.items():
        if count < 15:
            print(f"OSS {cliente_id}: {match_info['oss_nome']}")
            print(f"  → VIXEN {match_info['vixen_id']}: {match_info['vixen_nome']}")
            print(f"  → Método: {match_info['metodo']}")
            if 'similaridade' in match_info:
                print(f"  → Similaridade: {match_info['similaridade']}%")
            print()
            count += 1
    
    # 8. Salva resultados
    matches_df = pd.DataFrame([
        {
            'oss_cliente_id': cliente_id,
            'uuid_encontrado': info['uuid'],
            'vixen_id': info['vixen_id'],
            'metodo': info['metodo'],
            'oss_nome': info['oss_nome'],
            'vixen_nome': info['vixen_nome'],
            'similaridade': info.get('similaridade', 100)
        }
        for cliente_id, info in todos_matches_nomes.items()
    ])
    
    arquivo_matches = base_dir / "data" / "matches_nomes_variacoes.csv"
    matches_df.to_csv(arquivo_matches, index=False)
    
    print(f"🎯 MATCHES SALVOS: {arquivo_matches}")
    print(f"📊 {len(todos_matches_nomes)} clientes recuperados por variações de nomes!")
    print(f"✅ Estratégia de nomes com pequenas variações concluída!")
    
    return todos_matches_nomes

if __name__ == "__main__":
    resultado = match_nomes_variacoes()
    print(f"\n🎉 SUCESSO! {len(resultado)} matches por variações de nomes!")