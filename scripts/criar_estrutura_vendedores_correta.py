#!/usr/bin/env python3
"""
Script para criar estrutura correta:
1. Tabela vendedores únicos (1 UUID por vendedor)
2. Tabela relacionamento vendedores_lojas (N:N)
"""

import pandas as pd
import json
import uuid
from pathlib import Path

def criar_vendedores_unicos():
    """Cria tabela de vendedores únicos com UUID"""
    
    # Ler arquivo padronizado
    df_original = pd.read_excel('PADRONIZACAO_VENDEDORES_COMPLETA.xlsx')
    
    # Obter vendedores únicos (nome padronizado)
    vendedores_unicos = df_original['nome_padronizado'].unique()
    
    # Criar tabela de vendedores com UUID
    vendedores = []
    
    for vendedor in vendedores_unicos:
        # Gerar UUID único para cada vendedor
        vendedor_uuid = str(uuid.uuid4())
        
        # Pegar informações do primeiro registro deste vendedor
        primeiro_registro = df_original[df_original['nome_padronizado'] == vendedor].iloc[0]
        
        vendedores.append({
            'uuid': vendedor_uuid,
            'nome_padronizado': vendedor,
            'nome_exibicao': vendedor,
            'ativo': True,
            'criado_em': '2025-10-29',
            'observacoes': primeiro_registro.get('observacoes', '') if pd.notna(primeiro_registro.get('observacoes', '')) else ''
        })
    
    df_vendedores = pd.DataFrame(vendedores)
    return df_vendedores

def criar_vendedores_lojas(df_vendedores):
    """Cria tabela de relacionamento vendedores_lojas"""
    
    # Ler arquivo padronizado
    df_original = pd.read_excel('PADRONIZACAO_VENDEDORES_COMPLETA.xlsx')
    
    # Mapeamento de lojas
    lojas_mapping = {
        "1c35e0ad-3066-441e-85cc-44c0eb9b3ab4": {"codigo": "012", "nome": "São Mateus"},
        "aa7a5646-f7d6-4239-831c-6602fbabb10a": {"codigo": "010", "nome": "Suzano 2"},  
        "da3978c9-bba2-431a-91b7-970a406d3acf": {"codigo": "009", "nome": "Perus"},
        "9a22ccf1-36fe-4b9f-9391-ca31433dc31e": {"codigo": "048", "nome": "Mauá"},
        "52f92716-d2ba-441a-ac3c-94bdfabd9722": {"codigo": "042", "nome": "Suzano"},
        "4e94f51f-3b0f-4e0f-ba73-64982b870f2c": {"codigo": "011", "nome": "Rio Pequeno"}
    }
    
    # Criar relacionamentos vendedor-loja
    vendedores_lojas = []
    mapeamento_nomes_originais = {}
    
    # Processar apenas registros COM loja
    df_com_loja = df_original[df_original['loja_nome'] != 'Sem Loja']
    
    for _, row in df_com_loja.iterrows():
        # Buscar UUID do vendedor
        vendedor_uuid = df_vendedores[
            df_vendedores['nome_padronizado'] == row['nome_padronizado']
        ]['uuid'].iloc[0]
        
        # Informações da loja
        loja_id = row['loja_id']
        loja_info = lojas_mapping.get(loja_id, {"codigo": "000", "nome": "Desconhecida"})
        
        # Verificar se já existe essa combinação
        combinacao_existe = any(
            rel['vendedor_uuid'] == vendedor_uuid and rel['loja_uuid'] == loja_id 
            for rel in vendedores_lojas
        )
        
        if not combinacao_existe:
            vendedores_lojas.append({
                'uuid': str(uuid.uuid4()),
                'vendedor_uuid': vendedor_uuid,
                'loja_uuid': loja_id,
                'loja_codigo': loja_info['codigo'],
                'loja_nome': loja_info['nome'],
                'codigo_vendedor_sistema': row['codigo_vendedor'] if pd.notna(row['codigo_vendedor']) else '',
                'ativo': True,
                'data_inicio': '2023-01-01',
                'data_fim': None
            })
        
        # Mapeamento de nomes originais para o vendedor UUID
        if vendedor_uuid not in mapeamento_nomes_originais:
            mapeamento_nomes_originais[vendedor_uuid] = {
                'nome_padronizado': row['nome_padronizado'],
                'nomes_originais': set()
            }
        
        mapeamento_nomes_originais[vendedor_uuid]['nomes_originais'].add(row['nome_original'])
    
    # Converter sets para listas
    for uuid_vendedor in mapeamento_nomes_originais:
        mapeamento_nomes_originais[uuid_vendedor]['nomes_originais'] = list(
            mapeamento_nomes_originais[uuid_vendedor]['nomes_originais']
        )
    
    df_vendedores_lojas = pd.DataFrame(vendedores_lojas)
    return df_vendedores_lojas, mapeamento_nomes_originais

def processar_vendedores_sem_loja(df_original):
    """Identifica vendedores sem loja para atribuição manual"""
    
    sem_loja = df_original[df_original['loja_nome'] == 'Sem Loja']
    
    # Agrupar por nome padronizado
    sem_loja_agrupado = []
    
    for nome_padronizado in sem_loja['nome_padronizado'].unique():
        registros = sem_loja[sem_loja['nome_padronizado'] == nome_padronizado]
        
        nomes_originais = registros['nome_original'].tolist()
        observacoes = registros['observacoes'].dropna().tolist()
        
        sem_loja_agrupado.append({
            'nome_padronizado': nome_padronizado,
            'nomes_originais': nomes_originais,
            'observacoes': observacoes[0] if observacoes else '',
            'quantidade_registros': len(registros),
            'loja_sugerida': ''  # Para preenchimento manual
        })
    
    return pd.DataFrame(sem_loja_agrupado)

def salvar_arquivos(df_vendedores, df_vendedores_lojas, df_sem_loja, mapeamento_nomes):
    """Salva todos os arquivos gerados"""
    
    # 1. Tabela de vendedores únicos
    vendedores_path = "VENDEDORES_UNICOS_UUID.xlsx"
    with pd.ExcelWriter(vendedores_path, engine='openpyxl') as writer:
        df_vendedores.to_excel(writer, sheet_name='Vendedores', index=False)
    
    # 2. Tabela de relacionamentos vendedor-loja
    vendedores_lojas_path = "VENDEDORES_LOJAS_RELACIONAMENTO.xlsx"
    with pd.ExcelWriter(vendedores_lojas_path, engine='openpyxl') as writer:
        df_vendedores_lojas.to_excel(writer, sheet_name='Vendedores_Lojas', index=False)
    
    # 3. Vendedores sem loja para atribuição
    sem_loja_path = "VENDEDORES_SEM_LOJA_PARA_ATRIBUIR.xlsx"
    with pd.ExcelWriter(sem_loja_path, engine='openpyxl') as writer:
        df_sem_loja.to_excel(writer, sheet_name='Sem_Loja', index=False)
    
    # 4. Mapeamento de nomes originais
    mapeamento_path = "MAPEAMENTO_NOMES_ORIGINAIS_UUID.json"
    with open(mapeamento_path, 'w', encoding='utf-8') as f:
        json.dump(mapeamento_nomes, f, ensure_ascii=False, indent=2)
    
    # 5. CSVs também
    df_vendedores.to_csv("VENDEDORES_UNICOS_UUID.csv", index=False, encoding='utf-8-sig')
    df_vendedores_lojas.to_csv("VENDEDORES_LOJAS_RELACIONAMENTO.csv", index=False, encoding='utf-8-sig')
    df_sem_loja.to_csv("VENDEDORES_SEM_LOJA_PARA_ATRIBUIR.csv", index=False, encoding='utf-8-sig')
    
    return {
        'vendedores': vendedores_path,
        'vendedores_lojas': vendedores_lojas_path,
        'sem_loja': sem_loja_path,
        'mapeamento': mapeamento_path
    }

def main():
    """Função principal"""
    print("🏗️ CRIANDO ESTRUTURA CORRETA DE VENDEDORES")
    print("=" * 60)
    print("1. Vendedores únicos (1 UUID por vendedor)")
    print("2. Relacionamento vendedores_lojas (N:N)")
    print("3. Vendedores sem loja para atribuição manual")
    print()
    
    # 1. Criar vendedores únicos
    print("📊 Criando vendedores únicos...")
    df_vendedores = criar_vendedores_unicos()
    
    # 2. Criar relacionamentos vendedor-loja
    print("🔗 Criando relacionamentos vendedor-loja...")
    df_vendedores_lojas, mapeamento_nomes = criar_vendedores_lojas(df_vendedores)
    
    # 3. Processar vendedores sem loja
    print("❓ Processando vendedores sem loja...")
    df_original = pd.read_excel('PADRONIZACAO_VENDEDORES_COMPLETA.xlsx')
    df_sem_loja = processar_vendedores_sem_loja(df_original)
    
    # 4. Salvar arquivos
    print("💾 Salvando arquivos...")
    arquivos = salvar_arquivos(df_vendedores, df_vendedores_lojas, df_sem_loja, mapeamento_nomes)
    
    # Estatísticas
    print("\n📊 ESTATÍSTICAS FINAIS:")
    print(f"   • Vendedores únicos: {len(df_vendedores)}")
    print(f"   • Relacionamentos vendedor-loja: {len(df_vendedores_lojas)}")
    print(f"   • Vendedores sem loja: {len(df_sem_loja)}")
    print()
    
    print("📁 ARQUIVOS CRIADOS:")
    for tipo, caminho in arquivos.items():
        print(f"   • {tipo}: {caminho}")
    
    print()
    print("🎯 ESTRUTURA FINAL:")
    print("   1. Cada vendedor tem 1 UUID único")
    print("   2. Relacionamentos N:N com lojas")
    print("   3. Mapeamento completo de nomes originais")
    print("   4. Vendedores sem loja identificados para atribuição")
    
    return df_vendedores, df_vendedores_lojas, df_sem_loja

if __name__ == "__main__":
    vendedores, vendedores_lojas, sem_loja = main()