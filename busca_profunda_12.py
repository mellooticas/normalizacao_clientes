import pandas as pd
import re

vixen = 'dados_processados/originais/clientes/normalizados/VIXEN.csv'
clientes_rows = 'dados_processados/originais/estruturas_do_banco/clientes_rows.csv'

print('='*80)
print('BUSCA PROFUNDA - CRUZAMENTO POR MULTIPLOS CAMPOS')
print('='*80)

# Carregar
df_vixen = pd.read_csv(vixen, sep=';', encoding='utf-8')
df_rows = pd.read_csv(clientes_rows, sep=',', encoding='utf-8', on_bad_lines='skip')

# Filtrar os 12 sem UUID
sem_uuid = df_vixen[df_vixen['cliente_id'].isna()].copy()

print(f'\nRegistros para buscar: {len(sem_uuid)}')
print(f'Registros no banco: {len(df_rows):,}')

# Normalizar campos para busca
def normalizar_texto(texto):
    if pd.isna(texto):
        return ''
    texto = str(texto).lower().strip()
    texto = re.sub(r'[^a-z0-9]', '', texto)
    return texto

def normalizar_telefone(fone):
    if pd.isna(fone):
        return ''
    fone = str(fone)
    fone = re.sub(r'[^0-9]', '', fone)
    # Pegar ultimos 8-9 digitos (numero sem DDD)
    if len(fone) >= 8:
        return fone[-9:]
    return fone

# Preparar campos do VIXEN
sem_uuid['nome_norm'] = sem_uuid['Nome Completo'].apply(normalizar_texto)
sem_uuid['fone_norm'] = sem_uuid['Fone'].apply(normalizar_telefone)
sem_uuid['email_norm'] = sem_uuid['E-mail'].apply(normalizar_texto)
sem_uuid['data_nasc'] = pd.to_datetime(sem_uuid['Dt de aniversário'], format='%d/%m/%Y', errors='coerce')

# Preparar campos do clientes_rows
df_rows['nome_norm'] = df_rows['nome'].apply(normalizar_texto)
df_rows['email_norm'] = df_rows['email'].apply(normalizar_texto) if 'email' in df_rows.columns else ''
df_rows['data_nasc'] = pd.to_datetime(df_rows['data_nascimento'], errors='coerce')

# Extrair ID VIXEN das observacoes
def extrair_id_vixen(obs):
    if pd.isna(obs):
        return None
    match = re.search(r'ID VIXEN:\s*(\d+)', str(obs))
    if match:
        return int(match.group(1))
    return None

df_rows['id_vixen_obs'] = df_rows['observacoes'].apply(extrair_id_vixen) if 'observacoes' in df_rows.columns else None

print('\n' + '='*80)
print('ESTRATEGIAS DE BUSCA:')
print('='*80)

matches_encontrados = []

for idx, row_vixen in sem_uuid.iterrows():
    print(f'\nBuscando: {row_vixen["Nome Completo"]} (ID VIXEN: {row_vixen["ID"]})')
    
    candidatos = []
    
    # ESTRATEGIA 0: ID VIXEN (mais confiavel - direto das observacoes)
    if pd.notna(row_vixen['ID']) and 'id_vixen_obs' in df_rows.columns:
        match_id_vixen = df_rows[df_rows['id_vixen_obs'] == int(row_vixen['ID'])]
        if len(match_id_vixen) > 0:
            candidatos.append(('ID_VIXEN', match_id_vixen))
            print(f'  *** MATCH DIRETO POR ID_VIXEN: {len(match_id_vixen)} candidato(s) ***')
    
    # ESTRATEGIA 1: EMAIL
    if row_vixen['email_norm'] and row_vixen['email_norm'] not in ['nan', 'naotem', 'naotememail', 'contato', 'suzano', 'maua', 'oticas', 'oticaslancaster']:
        match_email = df_rows[df_rows['email_norm'] == row_vixen['email_norm']]
        if len(match_email) > 0:
            candidatos.append(('EMAIL', match_email))
            print(f'  OK Match por EMAIL: {len(match_email)} candidato(s)')
    
    # ESTRATEGIA 2: NOME PARCIAL + DATA NASCIMENTO
    if pd.notna(row_vixen['data_nasc']):
        # Pegar primeiras palavras do nome (2-3 palavras)
        palavras_nome = row_vixen['Nome Completo'].split()[:2]
        nome_parcial = ' '.join(palavras_nome).lower()
        
        match_parcial = df_rows[
            (df_rows['nome'].str.lower().str.contains(nome_parcial, na=False, regex=False)) &
            (df_rows['data_nasc'] == row_vixen['data_nasc'])
        ]
        if len(match_parcial) > 0:
            candidatos.append(('NOME_PARCIAL+DATA', match_parcial))
            print(f'  OK Match por NOME_PARCIAL+DATA: {len(match_parcial)} candidato(s)')
    
    # ESTRATEGIA 3: ULTIMAS PALAVRAS DO NOME + DATA
    if pd.notna(row_vixen['data_nasc']):
        palavras_nome = row_vixen['Nome Completo'].split()
        if len(palavras_nome) >= 2:
            sobrenome = palavras_nome[-1].lower()
            
            match_sobrenome = df_rows[
                (df_rows['nome'].str.lower().str.contains(sobrenome, na=False, regex=False)) &
                (df_rows['data_nasc'] == row_vixen['data_nasc'])
            ]
            if len(match_sobrenome) > 0:
                candidatos.append(('SOBRENOME+DATA', match_sobrenome))
                print(f'  OK Match por SOBRENOME+DATA: {len(match_sobrenome)} candidato(s)')
    
    # ESTRATEGIA 4: PARTES DO NOME (para nomes truncados tipo JOSE GERA)
    palavras = row_vixen['Nome Completo'].split()
    if len(palavras) >= 2:
        for palavra in palavras:
            if len(palavra) >= 4:  # Palavras com 4+ letras
                match_palavra = df_rows[df_rows['nome'].str.contains(palavra, case=False, na=False, regex=False)]
                if len(match_palavra) > 0 and len(match_palavra) < 20:  # Evitar nomes muito comuns
                    candidatos.append((f'CONTEM_{palavra.upper()}', match_palavra))
                    print(f'  OK Match por palavra {palavra.upper()}: {len(match_palavra)} candidato(s)')
    
    # Analisar candidatos
    if candidatos:
        print(f'\n  CANDIDATOS ENCONTRADOS:')
        
        # Priorizar matches por ID_VIXEN e EMAIL
        melhor_match = None
        melhor_metodo = None
        
        for metodo, df_match in candidatos:
            if metodo in ['ID_VIXEN', 'EMAIL'] and len(df_match) == 1:
                melhor_match = df_match.iloc[0]
                melhor_metodo = metodo
                break
        
        if melhor_match is None:
            # Se nao tem ID_VIXEN/EMAIL unico, pegar primeiro candidato
            melhor_metodo, df_match = candidatos[0]
            melhor_match = df_match.iloc[0]
        
        print(f'\n  MELHOR CANDIDATO (via {melhor_metodo}):')
        print(f'    UUID: {melhor_match["id"]}')
        print(f'    Nome BD: {melhor_match["nome"]}')
        print(f'    Email BD: {melhor_match.get("email", "N/A")}')
        print(f'    Data Nasc BD: {melhor_match["data_nascimento"]}')
        print(f'    Observacoes: {str(melhor_match.get("observacoes", ""))[:80]}...')
        
        matches_encontrados.append({
            'index': idx,
            'nome_vixen': row_vixen['Nome Completo'],
            'nome_bd': melhor_match['nome'],
            'uuid': melhor_match['id'],
            'metodo': melhor_metodo
        })
    else:
        print(f'  NENHUM CANDIDATO encontrado')

print(f'\n\n' + '='*80)
print('RESUMO DA BUSCA PROFUNDA')
print('='*80)

print(f'\nTotal buscado: 12')
print(f'Matches encontrados: {len(matches_encontrados)}')
print(f'Ainda sem match: {12 - len(matches_encontrados)}')

if matches_encontrados:
    print(f'\nMATCHES ENCONTRADOS:')
    for i, match in enumerate(matches_encontrados, 1):
        print(f'\n{i}. Via {match["metodo"]}:')
        print(f'   VIXEN: {match["nome_vixen"]}')
        print(f'   BD:    {match["nome_bd"]}')
        print(f'   UUID:  {match["uuid"]}')
    
    # Aplicar matches no arquivo
    print(f'\n' + '='*80)
    print('APLICANDO MATCHES NO ARQUIVO')
    print('='*80)
    
    for match in matches_encontrados:
        df_vixen.loc[match['index'], 'cliente_id'] = match['uuid']
        df_vixen.loc[match['index'], 'match_metodo'] = f"PROFUNDO_{match['metodo']}"
    
    # Salvar
    df_vixen.to_csv(vixen, sep=';', index=False, encoding='utf-8')
    
    print(f'\nOK Arquivo atualizado com {len(matches_encontrados)} novos matches!')
    
    # Estatisticas finais
    com_uuid = df_vixen['cliente_id'].notna().sum()
    sem_uuid_final = df_vixen['cliente_id'].isna().sum()
    total = len(df_vixen)
    
    print(f'\nESTATISTICAS FINAIS:')
    print(f'  Total: {total:,}')
    print(f'  Com UUID: {com_uuid:,} ({com_uuid/total*100:.2f}%)')
    print(f'  Sem UUID: {sem_uuid_final:,} ({sem_uuid_final/total*100:.2f}%)')
else:
    print(f'\nNenhum novo match encontrado.')
