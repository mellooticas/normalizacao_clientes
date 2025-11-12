#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para normalização de OS duplicadas COM UUID das lojas do Supabase
Integra mapeamento direto dos UUIDs das lojas para relação automática no banco

Dados das lojas obtidos do Supabase:
- Mauá: 9a22ccf1-36fe-4b9f-9391-ca31433dc31e
- Perus: da3978c9-bba2-431a-91b7-970a406d3acf  
- Rio Pequeno: 4e94f51f-3b0f-4e0f-ba73-64982b870f2c
- São Mateus: 1c35e0ad-3066-441e-85cc-44c0eb9b3ab4
- Suzano: 52f92716-d2ba-441a-ac3c-94bdfabd9722
- Suzano 2: aa7a5646-f7d6-4239-831c-6602fbabb10a
"""

import pandas as pd
import os
from pathlib import Path
import numpy as np
from datetime import datetime

# Configurações
BASE_DIR = Path(__file__).parent
CONSOLIDADO_DIR = BASE_DIR / "data" / "originais" / "oss" / "consolidadas"
NORMALIZADO_DIR = BASE_DIR / "data" / "originais" / "oss" / "normalizadas"

# Mapeamento de lojas para UUIDs do Supabase (atualizado com dados reais)
LOJA_UUID_MAP = {
    'MAUA': '9a22ccf1-36fe-4b9f-9391-ca31433dc31e',
    'PERUS': 'da3978c9-bba2-431a-91b7-970a406d3acf',
    'RIO_PEQUENO': '4e94f51f-3b0f-4e0f-ba73-64982b870f2c',
    'SAO_MATEUS': '1c35e0ad-3066-441e-85cc-44c0eb9b3ab4',
    'SUZANO': '52f92716-d2ba-441a-ac3c-94bdfabd9722',
    'SUZANO2': 'aa7a5646-f7d6-4239-831c-6602fbabb10a'
}

def extrair_loja_do_arquivo(nome_arquivo):
    """Extrai o nome da loja a partir do nome do arquivo"""
    nome_base = nome_arquivo.replace('_consolidado.csv', '').upper()
    return nome_base

def normalizar_campo(valor):
    """Normaliza um campo para string válida"""
    if pd.isna(valor) or valor is None:
        return ''
    return str(valor).strip()

def consolidar_valores(*valores):
    """Consolida múltiplos valores, priorizando os não vazios"""
    valores_limpos = []
    for val in valores:
        val_norm = normalizar_campo(val)
        if val_norm and val_norm.lower() not in ['nan', 'none', '']:
            valores_limpos.append(val_norm)
    
    if not valores_limpos:
        return ''
    
    # Remove duplicatas mantendo ordem
    valores_unicos = []
    for val in valores_limpos:
        if val not in valores_unicos:
            valores_unicos.append(val)
    
    # Se só tem um valor, retorna ele
    if len(valores_unicos) == 1:
        return valores_unicos[0]
    
    # Se são números, pega o maior
    try:
        nums = [float(val.replace(',', '.')) for val in valores_unicos]
        return str(max(nums))
    except:
        pass
    
    # Para strings, pega a mais longa
    return max(valores_unicos, key=len)

def processar_loja(arquivo_consolidado):
    """Processa um arquivo consolidado de loja, normalizando duplicatas"""
    
    print(f"\n=== Processando {arquivo_consolidado.name} ===")
    
    # Lê o arquivo
    df = pd.read_csv(arquivo_consolidado)
    print(f"Total de registros: {len(df)}")
    
    # Extrai nome da loja e obtém UUID
    nome_loja = extrair_loja_do_arquivo(arquivo_consolidado.name)
    loja_uuid = LOJA_UUID_MAP.get(nome_loja)
    
    if not loja_uuid:
        print(f"ERRO: UUID não encontrado para loja {nome_loja}")
        return None
    
    print(f"Loja: {nome_loja} -> UUID: {loja_uuid}")
    
    # Adiciona coluna com UUID da loja
    df['loja_id'] = loja_uuid
    df['loja_nome'] = nome_loja
    
    # Cria chave única para OS (LOJA + NUMERO_OS)
    # Normaliza nome da coluna OS (pode ser "OS N°" ou similar)
    col_os = None
    for col in df.columns:
        if 'OS' in col.upper() and 'N' in col.upper():
            col_os = col
            break
    
    if col_os is None:
        print(f"ERRO: Coluna de OS não encontrada em {arquivo_consolidado.name}")
        print(f"Colunas disponíveis: {list(df.columns)}")
        return None
    
    df['numero_os'] = df[col_os]
    df['os_chave'] = df['loja_nome'] + '_' + df['numero_os'].astype(str)
    
    # Verifica duplicatas
    duplicatas = df[df.duplicated(subset=['os_chave'], keep=False)]
    if len(duplicatas) > 0:
        print(f"Encontradas {len(duplicatas)} linhas duplicadas para {len(duplicatas['os_chave'].unique())} OS únicas")
        
        # Agrupa por OS e consolida informações
        grupos = df.groupby('os_chave')
        
        registros_consolidados = []
        
        for os_chave, grupo in grupos:
            # Se só tem um registro, mantém como está
            if len(grupo) == 1:
                registros_consolidados.append(grupo.iloc[0].to_dict())
                continue
            
            # Consolida múltiplos registros
            registro_consolidado = {}
            
            # Campos fixos (pega do primeiro registro)
            registro_consolidado['loja_id'] = loja_uuid
            registro_consolidado['loja_nome'] = nome_loja
            registro_consolidado['os_chave'] = os_chave
            registro_consolidado['numero_os'] = grupo['numero_os'].iloc[0]
            
            # Consolida todos os outros campos
            for coluna in grupo.columns:
                if coluna not in ['loja_id', 'loja_nome', 'os_chave', 'numero_os'] and coluna != col_os:
                    valores = grupo[coluna].tolist()
                    registro_consolidado[coluna] = consolidar_valores(*valores)
            
            registros_consolidados.append(registro_consolidado)
        
        # Cria novo DataFrame consolidado
        df_normalizado = pd.DataFrame(registros_consolidados)
        
        print(f"Consolidação: {len(df)} -> {len(df_normalizado)} registros")
        print(f"Eliminadas {len(df) - len(df_normalizado)} duplicatas ({((len(df) - len(df_normalizado))/len(df)*100):.1f}%)")
        
    else:
        print("Nenhuma duplicata encontrada")
        df_normalizado = df.copy()
    
    return df_normalizado

def main():
    """Função principal"""
    
    print("=== NORMALIZAÇÃO DE OS DUPLICADAS COM UUID ===")
    print(f"Diretório consolidado: {CONSOLIDADO_DIR}")
    print(f"Diretório normalizado: {NORMALIZADO_DIR}")
    
    # Cria diretório de saída se não existir
    NORMALIZADO_DIR.mkdir(parents=True, exist_ok=True)
    
    # Lista arquivos consolidados
    arquivos_consolidados = list(CONSOLIDADO_DIR.glob("*_consolidado.csv"))
    
    if not arquivos_consolidados:
        print("Nenhum arquivo consolidado encontrado!")
        return
    
    print(f"\nEncontrados {len(arquivos_consolidados)} arquivos para processar:")
    for arquivo in arquivos_consolidados:
        print(f"  - {arquivo.name}")
    
    # Estatísticas gerais
    total_original = 0
    total_normalizado = 0
    
    # Processa cada arquivo
    for arquivo in arquivos_consolidados:
        df_normalizado = processar_loja(arquivo)
        
        if df_normalizado is not None:
            # Salva arquivo normalizado
            nome_saida = arquivo.name.replace('_consolidado.csv', '_normalizado_uuid.csv')
            arquivo_saida = NORMALIZADO_DIR / nome_saida
            
            df_normalizado.to_csv(arquivo_saida, index=False, encoding='utf-8')
            print(f"Salvo: {arquivo_saida}")
            
            # Atualiza estatísticas
            total_original += len(pd.read_csv(arquivo))
            total_normalizado += len(df_normalizado)
    
    # Relatório final
    print(f"\n=== RELATÓRIO FINAL ===")
    print(f"Total registros originais: {total_original:,}")
    print(f"Total registros normalizados: {total_normalizado:,}")
    print(f"Registros eliminados: {total_original - total_normalizado:,}")
    print(f"Taxa de consolidação: {((total_original - total_normalizado)/total_original*100):.2f}%")
    
    print(f"\n=== MAPEAMENTO DE LOJAS ===")
    for loja, uuid in LOJA_UUID_MAP.items():
        print(f"{loja}: {uuid}")
    
    print(f"\nArquivos normalizados salvos em: {NORMALIZADO_DIR}")

if __name__ == "__main__":
    main()