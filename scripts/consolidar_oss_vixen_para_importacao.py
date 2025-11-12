#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Consolida clientes OSS_SUZANO_MAUA + VIXEN para importação única no banco

ESTRATÉGIA:
1. Deduplica OSS internamente (múltiplas OS do mesmo cliente)
2. Mescla OSS deduplicated + VIXEN
3. Gera arquivo final pronto para importação
"""

import pandas as pd
import re
from pathlib import Path
from datetime import datetime
from fuzzywuzzy import fuzz
import unicodedata

# ================================================================================
# CONFIGURAÇÕES
# ================================================================================
DIR_BASE = Path(__file__).parent.parent
DIR_DADOS = DIR_BASE / 'dados_processados' / 'originais' / 'clientes' / 'normalizados'

ARQUIVO_OSS = DIR_DADOS / 'OSS_SUZANO_MAUA.csv'
ARQUIVO_VIXEN = DIR_DADOS / 'VIXEN.csv'
ARQUIVO_SAIDA = DIR_DADOS / f'CLIENTES_OSS_VIXEN_CONSOLIDADO_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'

# ================================================================================
# FUNÇÕES DE NORMALIZAÇÃO
# ================================================================================

def normalizar_texto(texto):
    """Remove acentos, converte para maiúsculas, remove extras"""
    if pd.isna(texto) or str(texto).strip() == '':
        return ''
    texto = str(texto).strip().upper()
    # Remove acentos
    texto = ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )
    # Remove espaços múltiplos
    texto = re.sub(r'\s+', ' ', texto)
    return texto

def normalizar_cpf(cpf):
    """Remove formatação do CPF"""
    if pd.isna(cpf) or str(cpf).strip() == '':
        return ''
    cpf = str(cpf).strip()
    cpf = re.sub(r'[^\d]', '', cpf)
    return cpf if len(cpf) == 11 else ''

def normalizar_telefone(telefone):
    """Remove formatação do telefone"""
    if pd.isna(telefone) or str(telefone).strip() == '':
        return ''
    telefone = str(telefone).strip()
    telefone = re.sub(r'[^\d]', '', telefone)
    # Remove 0 inicial de DDD se tiver 11 ou 12 dígitos começando com 0
    if len(telefone) in [11, 12] and telefone.startswith('0'):
        telefone = telefone[1:]
    return telefone if len(telefone) >= 10 else ''

def validar_cpf(cpf):
    """Valida CPF com dígito verificador"""
    if not cpf or len(cpf) != 11:
        return False
    
    # CPFs inválidos conhecidos
    if cpf in ['00000000000', '11111111111', '22222222222', '33333333333',
               '44444444444', '55555555555', '66666666666', '77777777777',
               '88888888888', '99999999999']:
        return False
    
    # Verifica primeiro dígito
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    digito1 = 0 if (soma % 11) < 2 else 11 - (soma % 11)
    if int(cpf[9]) != digito1:
        return False
    
    # Verifica segundo dígito
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    digito2 = 0 if (soma % 11) < 2 else 11 - (soma % 11)
    if int(cpf[10]) != digito2:
        return False
    
    return True

def identificar_sexo_por_nome(nome):
    """Identifica sexo pelo primeiro nome usando listas comuns brasileiras"""
    if pd.isna(nome) or str(nome).strip() == '':
        return None
    
    nome_str = str(nome).strip().upper()
    primeiro_nome = nome_str.split()[0] if nome_str else ''
    
    # Remove prefixos numéricos (ex: "0CARLOS" -> "CARLOS")
    if primeiro_nome and primeiro_nome[0].isdigit():
        primeiro_nome = ''.join([c for c in primeiro_nome if not c.isdigit()]).strip()
    
    # Listas de nomes femininos comuns
    nomes_femininos = {
        'MARIA', 'ANA', 'JULIANA', 'MARIANA', 'ADRIANA', 'PATRICIA', 'FERNANDA',
        'AMANDA', 'JESSICA', 'ALINE', 'CAMILA', 'CARLA', 'CLAUDIA', 'DANIELA',
        'FABIANA', 'GABRIELA', 'LUCIANA', 'MONICA', 'RENATA', 'SANDRA', 'SILVIA',
        'SIMONE', 'TATIANA', 'VANESSA', 'BEATRIZ', 'BRUNA', 'CAROLINA', 'CRISTINA',
        'DEBORA', 'ELAINE', 'ELIZABETE', 'FERNANDA', 'GISELE', 'HELENA', 'ISABELA',
        'JAQUELINE', 'JULIA', 'KARINA', 'LARISSA', 'LETICIA', 'LUANA', 'LUCIA',
        'MARCELA', 'MARCIA', 'NATALIA', 'PAULA', 'PRISCILA', 'RAFAELA', 'REGINA',
        'ROBERTA', 'ROSANGELA', 'SABRINA', 'SOLANGE', 'TANIA', 'VERA', 'VIVIANE',
        'ROSA', 'RITA', 'MARTA', 'INES', 'JOANA', 'ANDREA', 'DENISE', 'LIVIA',
        'ISABELLE', 'EMANUELA', 'GABRIELLE', 'BIANCA', 'ALICE', 'LARISSA', 'MELISSA',
        'IZILDINHA', 'ELIENE', 'ABANITA', 'ABIA', 'ABIGAIL', 'ABIQUEILA', 'ADA',
        'ADAIAS', 'ELZA', 'UILMA', 'VITORIA', 'DARCI'
    }
    
    # Listas de nomes masculinos comuns
    nomes_masculinos = {
        'CARLOS', 'JOSE', 'JOAO', 'ANTONIO', 'FRANCISCO', 'PAULO', 'PEDRO',
        'LUCAS', 'GABRIEL', 'RAFAEL', 'MARCOS', 'BRUNO', 'ANDRE', 'FELIPE',
        'RODRIGO', 'FERNANDO', 'GUSTAVO', 'LEONARDO', 'MATHEUS', 'HENRIQUE',
        'DIEGO', 'RICARDO', 'THIAGO', 'EDUARDO', 'VINICIUS', 'ALESSANDRO',
        'CRISTIANO', 'DANIEL', 'FABIO', 'GUILHERME', 'MARCELO', 'MAURICIO',
        'NELSON', 'OSCAR', 'PAULO', 'RENATO', 'ROBERTO', 'SERGIO', 'TIAGO',
        'WAGNER', 'ALESSANDRO', 'EMIDIO', 'JACINTO', 'VALDIVO', 'EZEQUIEL',
        'ORLANDO', 'JORGE', 'AFONSO', 'ABEL', 'ABINE', 'ABRAAO', 'ADAILTON',
        'ADALBERTO', 'ANTONIO', 'MAURICIU', 'FABIO'
    }
    
    if primeiro_nome in nomes_femininos:
        return 'F'
    elif primeiro_nome in nomes_masculinos:
        return 'M'
    
    # Terminações típicas
    if primeiro_nome.endswith(('A', 'ANA', 'INA', 'ELLE', 'INHA')):
        return 'F'
    elif primeiro_nome.endswith(('O', 'OS', 'OR', 'AL', 'EL', 'IM')):
        return 'M'
    
    return None

def normalizar_data(data):
    """Converte data para formato YYYY-MM-DD"""
    if pd.isna(data) or str(data).strip() == '':
        return None
    
    data_str = str(data).strip()
    
    # Se for número (Excel serial date), converte
    try:
        num = float(data_str)
        # Excel serial date: dias desde 01/01/1900
        if 1 <= num <= 60000:  # Range válido: 1900 a ~2064
            # Excel tem bug: considera 1900 como bissexto (não é)
            # Ajuste: subtrair 2 dias se >= 60 (após 29/02/1900)
            excel_epoch = datetime(1899, 12, 30)  # Ajuste para bug do Excel
            dt = excel_epoch + pd.Timedelta(days=num)
            if 1900 <= dt.year <= 2025:
                return dt.strftime('%Y-%m-%d')
    except:
        pass
    
    # Tenta vários formatos de string
    formatos = [
        '%Y-%m-%d',
        '%d/%m/%Y',
        '%d-%m-%Y',
        '%Y/%m/%d',
    ]
    
    for formato in formatos:
        try:
            dt = datetime.strptime(data_str, formato)
            # Valida ano razoável
            if 1900 <= dt.year <= 2025:
                return dt.strftime('%Y-%m-%d')
        except:
            continue
    
    return None

# ================================================================================
# FASE 1: DEDUPLICAÇÃO INTERNA DO OSS
# ================================================================================

def deduplicate_oss(df_oss):
    """
    Deduplica OSS identificando cliente único através de:
    1. CPF válido (prioridade máxima)
    2. Telefone + Nome similar (fuzzy match >= 90%)
    3. Se nenhum match, considera cliente novo
    
    Retorna DataFrame com clientes únicos
    """
    print("\n" + "="*80)
    print("FASE 1: DEDUPLICAÇÃO INTERNA DO OSS")
    print("="*80)
    
    print(f"\n1. Dados originais: {len(df_oss)} OS")
    
    # Normaliza campos
    print("\n2. Normalizando campos...")
    df_oss['cpf_norm'] = df_oss['CPF'].apply(normalizar_cpf)
    df_oss['cpf_valido'] = df_oss['cpf_norm'].apply(lambda x: validar_cpf(x) if x else False)
    
    # Telefone - tenta ambas colunas
    if 'TELEFONE  :' in df_oss.columns:
        df_oss['tel_norm'] = df_oss['TELEFONE  :'].apply(normalizar_telefone)
    elif 'TELEFONE:' in df_oss.columns:
        df_oss['tel_norm'] = df_oss['TELEFONE:'].apply(normalizar_telefone)
    else:
        df_oss['tel_norm'] = ''
    
    df_oss['nome_norm'] = df_oss['NOME:'].apply(normalizar_texto)
    df_oss['data_nasc'] = df_oss['DT NASC'].apply(normalizar_data)
    df_oss['data_compra'] = df_oss['DATA DE COMPRA'].apply(normalizar_data)
    
    print(f"   ✓ CPFs válidos: {df_oss['cpf_valido'].sum()}")
    print(f"   ✓ Telefones válidos: {(df_oss['tel_norm'] != '').sum()}")
    print(f"   ✓ Nomes válidos: {(df_oss['nome_norm'] != '').sum()}")
    
    # Ordena por data de compra (mais antiga primeiro)
    df_oss = df_oss.sort_values('data_compra')
    
    # Agrupa clientes
    print("\n3. Identificando clientes únicos...")
    clientes = []
    id_cliente_map = {}  # OSS ID -> Cliente Único ID
    next_cliente_id = 1
    
    for idx, row in df_oss.iterrows():
        # Verifica se já foi identificado
        if row['ID_CLIENTE'] in id_cliente_map:
            continue
        
        cliente_id = f"OSS_{next_cliente_id:06d}"
        id_cliente_map[row['ID_CLIENTE']] = cliente_id
        
        # Lista de OSs deste cliente
        oss_ids = [row['OS N°']]
        
        # Busca outras OS do mesmo cliente
        cpf_ref = row['cpf_norm']
        tel_ref = row['tel_norm']
        nome_ref = row['nome_norm']
        
        # Se tem CPF válido, busca por CPF
        if row['cpf_valido'] and cpf_ref:
            matches = df_oss[
                (df_oss['cpf_norm'] == cpf_ref) & 
                (df_oss['cpf_valido'] == True) &
                (~df_oss['ID_CLIENTE'].isin(id_cliente_map.keys()))
            ]
            for match_idx, match_row in matches.iterrows():
                id_cliente_map[match_row['ID_CLIENTE']] = cliente_id
                oss_ids.append(match_row['OS N°'])
        
        # Se tem telefone, busca por telefone + nome similar
        elif tel_ref:
            matches = df_oss[
                (df_oss['tel_norm'] == tel_ref) &
                (~df_oss['ID_CLIENTE'].isin(id_cliente_map.keys()))
            ]
            for match_idx, match_row in matches.iterrows():
                # Compara nomes com fuzzy
                if nome_ref and match_row['nome_norm']:
                    similaridade = fuzz.ratio(nome_ref, match_row['nome_norm'])
                    if similaridade >= 90:
                        id_cliente_map[match_row['ID_CLIENTE']] = cliente_id
                        oss_ids.append(match_row['OS N°'])
        
        # Monta registro do cliente único
        # Prepara observações com info das OS
        obs_parts = []
        obs_parts.append(f"Loja: {row['LOJA']}")
        obs_parts.append(f"Total OS: {len(oss_ids)}")
        if len(oss_ids) > 1:
            obs_parts.append(f"OS: {', '.join(map(str, oss_ids[:5]))}")  # Primeiras 5 OS
            if len(oss_ids) > 5:
                obs_parts.append(f"... (+{len(oss_ids)-5} OS)")
        else:
            obs_parts.append(f"OS: {oss_ids[0]}")
        
        # Telefone para observações também
        telefone_obs = row.get('TELEFONE  :', row.get('TELEFONE:', ''))
        celular_obs = row.get('CELULAR:', '')
        
        clientes.append({
            'id_legado': row['ID_CLIENTE'],
            'nome': row['NOME:'],
            'cpf': cpf_ref if row['cpf_valido'] else None,  # Já está normalizado como string
            'rg': None,  # OSS não tem RG
            'data_nascimento': row['data_nasc'],
            'sexo': identificar_sexo_por_nome(row['NOME:']),  # Identifica por nome
            'email': row.get('EMAIL:', '') if row.get('EMAIL:', '') not in ['0', ''] else None,
            'status': 'ATIVO',
            'origem': 'OSS_SUZANO_MAUA',
            'tags': f'{{loja:{row["LOJA"]},fonte:OSS}}',  # Formato PostgreSQL correto
            'observacoes': ' | '.join(obs_parts),
            'cliente_desde': row['data_compra'],
            'telefone_principal': telefone_obs,  # Temporário - depois vai para core.telefones
            'celular': celular_obs  # Temporário - depois vai para core.telefones
        })
        
        next_cliente_id += 1
        
        if next_cliente_id % 100 == 0:
            print(f"   Processando... {next_cliente_id} clientes únicos identificados")
    
    df_clientes = pd.DataFrame(clientes)
    
    print(f"\n4. Resultado da deduplicação:")
    print(f"   - Total de OS: {len(df_oss)}")
    print(f"   - Clientes únicos: {len(df_clientes)}")
    print(f"   - Média de OS por cliente: {len(df_oss) / len(df_clientes):.2f}")
    print(f"   - Clientes com CPF válido: {df_clientes['cpf'].notna().sum()} ({df_clientes['cpf'].notna().sum()/len(df_clientes)*100:.1f}%)")
    
    return df_clientes

# ================================================================================
# FASE 2: PROCESSAMENTO VIXEN
# ================================================================================

def processar_vixen(df_vixen):
    """
    Processa dados VIXEN para formato padrão
    """
    print("\n" + "="*80)
    print("FASE 2: PROCESSAMENTO VIXEN")
    print("="*80)
    
    print(f"\n1. Registros VIXEN: {len(df_vixen)}")
    
    # Monta telefone completo (DDD + Fone.1)
    def montar_telefone_vixen(row):
        ddd = str(row.get('DDD', '')).strip()
        fone1 = str(row.get('Fone.1', '')).strip()
        if ddd and fone1:
            return f"({ddd}) {fone1}"
        return fone1
    
    # Normaliza CPF
    print("\n2. Validando CPFs...")
    df_vixen['cpf_norm'] = df_vixen['Cliente'].apply(normalizar_cpf)
    df_vixen['cpf_valido'] = df_vixen['cpf_norm'].apply(lambda x: validar_cpf(x) if x else False)
    print(f"   ✓ CPFs válidos: {df_vixen['cpf_valido'].sum()} ({df_vixen['cpf_valido'].sum()/len(df_vixen)*100:.1f}%)")
    
    # Monta DataFrame padrão
    clientes_vixen = []
    for idx, row in df_vixen.iterrows():
        email_vixen = row.get('E-mail', '')
        # Limpa emails inválidos
        if email_vixen in ['0', '', 'nan'] or pd.isna(email_vixen):
            email_vixen = None
        
        # Usa Dh.inclusão como cliente_desde
        data_inclusao = normalizar_data(row.get('Dh.inclusão', ''))
        
        # Sexo: usa do VIXEN se tiver, senão identifica por nome
        sexo_vixen = row.get('Sexo', '')
        if pd.notna(sexo_vixen) and str(sexo_vixen).strip() in ['M', 'F', 'm', 'f']:
            sexo_final = str(sexo_vixen).strip().upper()
        else:
            sexo_final = identificar_sexo_por_nome(row['Nome Completo'])
        
        clientes_vixen.append({
            'id_legado': f"VIXEN_{row['ID']}",
            'nome': row['Nome Completo'],
            'cpf': row['cpf_norm'] if row['cpf_valido'] else None,  # Já está normalizado como string
            'rg': None,  # VIXEN não tem RG
            'data_nascimento': normalizar_data(row.get('Dt de aniversário', '')),
            'sexo': sexo_final,  # Usa VIXEN ou identifica por nome
            'email': email_vixen,
            'status': 'ATIVO',
            'origem': 'VIXEN',
            'tags': '{fonte:VIXEN}',  # Formato PostgreSQL correto
            'observacoes': f"ID VIXEN: {row['ID']}",
            'cliente_desde': data_inclusao,  # Agora usa Dh.inclusão!
            'telefone_principal': montar_telefone_vixen(row),  # Temporário
            'celular': None  # VIXEN não separa
        })
    
    df_clientes_vixen = pd.DataFrame(clientes_vixen)
    
    print(f"\n3. Processamento concluído:")
    print(f"   - Total clientes: {len(df_clientes_vixen)}")
    print(f"   - Com CPF válido: {df_clientes_vixen['cpf'].notna().sum()}")
    
    return df_clientes_vixen

# ================================================================================
# FASE 3: CONSOLIDAÇÃO
# ================================================================================

def consolidar_clientes(df_oss, df_vixen):
    """
    Consolida OSS + VIXEN removendo duplicações entre bases
    """
    print("\n" + "="*80)
    print("FASE 3: CONSOLIDAÇÃO OSS + VIXEN")
    print("="*80)
    
    print(f"\n1. Resumo antes da consolidação:")
    print(f"   - Clientes OSS: {len(df_oss)}")
    print(f"   - Clientes VIXEN: {len(df_vixen)}")
    print(f"   - Total (com possíveis duplicações): {len(df_oss) + len(df_vixen)}")
    
    # Identifica duplicações entre OSS e VIXEN por CPF
    print(f"\n2. Buscando duplicações por CPF...")
    df_oss_com_cpf = df_oss[df_oss['cpf'].notna()]
    df_vixen_com_cpf = df_vixen[df_vixen['cpf'].notna()]
    
    cpfs_oss = set(df_oss_com_cpf['cpf'])
    cpfs_vixen = set(df_vixen_com_cpf['cpf'])
    cpfs_duplicados = cpfs_oss.intersection(cpfs_vixen)
    
    print(f"   ✓ {len(cpfs_duplicados)} CPFs presentes em ambas bases")
    
    # Remove duplicados do VIXEN (mantém OSS que tem mais info)
    df_vixen_unicos = df_vixen[~df_vixen['cpf'].isin(cpfs_duplicados)]
    
    print(f"\n3. Resultado da consolidação:")
    print(f"   - Clientes OSS (mantidos): {len(df_oss)}")
    print(f"   - Clientes VIXEN únicos: {len(df_vixen_unicos)}")
    print(f"   - CPFs duplicados removidos: {len(cpfs_duplicados)}")
    print(f"   - TOTAL CONSOLIDADO: {len(df_oss) + len(df_vixen_unicos)}")
    
    # Concatena
    df_consolidado = pd.concat([df_oss, df_vixen_unicos], ignore_index=True)
    
    # Adiciona ID único final
    df_consolidado['id'] = range(1, len(df_consolidado) + 1)
    df_consolidado['id'] = df_consolidado['id'].apply(lambda x: f"CLI_{x:06d}")
    
    return df_consolidado

# ================================================================================
# MAIN
# ================================================================================

def main():
    print("="*80)
    print("CONSOLIDAÇÃO OSS + VIXEN PARA IMPORTAÇÃO")
    print("="*80)
    print(f"\nData/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nArquivos de entrada:")
    print(f"  - OSS: {ARQUIVO_OSS}")
    print(f"  - VIXEN: {ARQUIVO_VIXEN}")
    print(f"\nArquivo de saída:")
    print(f"  - {ARQUIVO_SAIDA}")
    
    # Lê arquivos
    print("\n" + "="*80)
    print("CARREGANDO DADOS")
    print("="*80)
    
    print("\n1. Lendo OSS_SUZANO_MAUA.csv...")
    df_oss = pd.read_csv(ARQUIVO_OSS, sep=';', encoding='utf-8', low_memory=False)
    print(f"   ✓ {len(df_oss)} registros (OS)")
    
    print("\n2. Lendo VIXEN.csv...")
    df_vixen = pd.read_csv(ARQUIVO_VIXEN, sep=';', encoding='utf-8', low_memory=False)
    print(f"   ✓ {len(df_vixen)} registros (clientes)")
    
    # Fase 1: Deduplica OSS
    df_clientes_oss = deduplicate_oss(df_oss)
    
    # Fase 2: Processa VIXEN
    df_clientes_vixen = processar_vixen(df_vixen)
    
    # Fase 3: Consolida
    df_final = consolidar_clientes(df_clientes_oss, df_clientes_vixen)
    
    # Reordena colunas para match com banco
    colunas_banco = [
        'id_legado', 'nome', 'cpf', 'rg', 'data_nascimento', 'sexo',
        'email', 'status', 'origem', 'tags', 'observacoes', 'cliente_desde'
    ]
    
    # Colunas temporárias (telefones serão importados depois em core.telefones)
    colunas_temp = ['telefone_principal', 'celular']
    
    colunas_ordem = colunas_banco + colunas_temp
    
    # Adiciona colunas que podem estar faltando
    for col in colunas_ordem:
        if col not in df_final.columns:
            df_final[col] = None
    
    df_final = df_final[colunas_ordem]
    
    # CORREÇÃO: Garante que CPF seja string com zeros à esquerda (evita notação científica)
    if 'cpf' in df_final.columns:
        # Converte para string preservando zeros à esquerda
        def formatar_cpf(cpf):
            if pd.isna(cpf) or cpf == '' or cpf == 'nan' or cpf == 'None':
                return None
            cpf_str = str(cpf).replace('.0', '')  # Remove .0 se tiver
            # Adiciona zeros à esquerda se necessário (CPF tem 11 dígitos)
            if cpf_str.isdigit() and len(cpf_str) < 11:
                cpf_str = cpf_str.zfill(11)
            return cpf_str if len(cpf_str) == 11 else None
        
        df_final['cpf'] = df_final['cpf'].apply(formatar_cpf)
    
    # Converte id_legado para string também
    if 'id_legado' in df_final.columns:
        df_final['id_legado'] = df_final['id_legado'].astype(str)
    
    # Salva SEM aspas desnecessárias (quoting=0 = QUOTE_MINIMAL)
    print("\n" + "="*80)
    print("SALVANDO ARQUIVO FINAL")
    print("="*80)
    
    df_final.to_csv(ARQUIVO_SAIDA, sep=';', index=False, encoding='utf-8', quoting=0, na_rep='')
    print(f"\n✅ Arquivo salvo: {ARQUIVO_SAIDA}")
    print(f"   - Total de registros: {len(df_final)}")
    
    # Estatísticas finais
    print("\n" + "="*80)
    print("ESTATÍSTICAS FINAIS")
    print("="*80)
    
    print(f"\nPor origem:")
    print(df_final['origem'].value_counts().to_string())
    
    print(f"\nDados preenchidos:")
    print(f"  - CPF: {df_final['cpf'].notna().sum()} ({df_final['cpf'].notna().sum()/len(df_final)*100:.1f}%)")
    print(f"  - RG: {df_final['rg'].notna().sum()} ({df_final['rg'].notna().sum()/len(df_final)*100:.1f}%)")
    print(f"  - Data Nasc: {df_final['data_nascimento'].notna().sum()} ({df_final['data_nascimento'].notna().sum()/len(df_final)*100:.1f}%)")
    print(f"  - Sexo: {df_final['sexo'].notna().sum()} ({df_final['sexo'].notna().sum()/len(df_final)*100:.1f}%)")
    print(f"  - Telefone: {df_final['telefone_principal'].notna().sum()} ({df_final['telefone_principal'].notna().sum()/len(df_final)*100:.1f}%)")
    print(f"  - Email: {df_final['email'].notna().sum()} ({df_final['email'].notna().sum()/len(df_final)*100:.1f}%)")
    print(f"  - Cliente Desde: {df_final['cliente_desde'].notna().sum()} ({df_final['cliente_desde'].notna().sum()/len(df_final)*100:.1f}%)")
    
    print(f"\n⚠️  IMPORTANTE:")
    print(f"  - Colunas 'telefone_principal' e 'celular' são temporárias")
    print(f"  - Após importar clientes, criar script para importar telefones em core.telefones")
    print(f"  - Tags no formato PostgreSQL array: {'{\"tag1\",\"tag2\"}'}")
    
    print("\n" + "="*80)
    print("✅ CONSOLIDAÇÃO CONCLUÍDA COM SUCESSO!")
    print("="*80)

if __name__ == '__main__':
    main()
