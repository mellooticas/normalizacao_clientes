#!/usr/bin/env python3
"""
Script para extrair TODOS os vendedores das consultas Supabase
Criará uma tabela completa para padronização manual
"""

import pandas as pd
import json
from pathlib import Path
import os

def extrair_vendedores_consulta_1():
    """Extrai todos os vendedores da consulta 1 (básica)"""
    vendedores_consulta_1 = [
        ("/////////////////////////", "VEN12////", "1c35e0ad-3066-441e-85cc-44c0eb9b3ab4"),
        ("ADRIANA ANSELMO", "VEN10ADRANS", "aa7a5646-f7d6-4239-831c-6602fbabb10a"),
        ("ALINE DA CRUZ SANTOS", None, None),
        ("ALINE DA CRUZ SANTOS", None, None),
        ("ANA", "VEN9ANA", "da3978c9-bba2-431a-91b7-970a406d3acf"),
        ("ANA CLAUDIA SANTOS", None, None),
        ("ANA CLAUDIA SANTOS", None, None),
        ("ANA MARIA", None, None),
        ("ANDRESSA DE SOUZA", "VEN48ANDSOU", "9a22ccf1-36fe-4b9f-9391-ca31433dc31e"),
        ("ARIANE", "VEN42ARIA", "52f92716-d2ba-441a-ac3c-94bdfabd9722"),
        ("ARIANE DIAS FERNANDES CARDOSO", None, None),
        ("ARIANE DIAS FERNANDES CARDOSO", None, None),
        ("ARIANI", "VEN9ARIA", "da3978c9-bba2-431a-91b7-970a406d3acf"),
        ("ARIANI", "VEN42ARIA", "52f92716-d2ba-441a-ac3c-94bdfabd9722"),
        ("ARIANI", "VEN12ARIA", "1c35e0ad-3066-441e-85cc-44c0eb9b3ab4"),
        ("ARIANI DIAS", None, None),
        ("ARIANI DIAS", None, None),
        ("B ETH", "VEN48ETH", "9a22ccf1-36fe-4b9f-9391-ca31433dc31e"),
        ("BETH", "VEN48BETH", "9a22ccf1-36fe-4b9f-9391-ca31433dc31e"),
        ("BETH", "VEN42BETH", "52f92716-d2ba-441a-ac3c-94bdfabd9722"),
        ("BRUNO", "VEN11BRUN", "4e94f51f-3b0f-4e0f-ba73-64982b870f2c"),
        ("BRUNO HENRIQUE SIMÃO", None, None),
        ("CARLA CRISTINA", "VEN10CARCRI", "aa7a5646-f7d6-4239-831c-6602fbabb10a"),
        ("CAROLINE OLIVEIRA LEITE", None, None),
        ("CAROLINE OLIVEIRA LEITE", None, None),
        ("CHINASA DORIS", "VEN12CHIDOR", "1c35e0ad-3066-441e-85cc-44c0eb9b3ab4"),
        ("EMERSON WILLIAN", None, None),
        ("ERICA", "VEN10ERIC", "aa7a5646-f7d6-4239-831c-6602fbabb10a"),
        ("ERICA DE CASSIA JESUS SILVA", "VEN48ERICAS", "9a22ccf1-36fe-4b9f-9391-ca31433dc31e"),
        ("ERIKA", "VEN10ERIK", "aa7a5646-f7d6-4239-831c-6602fbabb10a"),
        ("ERIKA", "VEN9ERIK", "da3978c9-bba2-431a-91b7-970a406d3acf"),
        ("ÉRIKA", "VEN10ÉRIK", "aa7a5646-f7d6-4239-831c-6602fbabb10a"),
        ("ÉRIKA", "VEN9ÉRIK", "da3978c9-bba2-431a-91b7-970a406d3acf"),
        ("ERIKA SERRAO FERREIRA", None, None),
        ("FELIPE", "VEN10FELI", "aa7a5646-f7d6-4239-831c-6602fbabb10a"),
        ("FELIPE", "VEN42FELI", "52f92716-d2ba-441a-ac3c-94bdfabd9722"),
        ("FELIPE  MIRANDA", "VEN10FELMIR", "aa7a5646-f7d6-4239-831c-6602fbabb10a"),
        ("FELIPE MIRANDA", "VEN10FELMIR", "aa7a5646-f7d6-4239-831c-6602fbabb10a"),
        ("FELIPE MIRANDFA", "VEN10FELMIR", "aa7a5646-f7d6-4239-831c-6602fbabb10a"),
        ("GARANTIA", "VEN48GARA", "9a22ccf1-36fe-4b9f-9391-ca31433dc31e"),
        ("GARANTIA", "VEN11GARA", "4e94f51f-3b0f-4e0f-ba73-64982b870f2c"),
        ("GARANTIA", "VEN42GARA", "52f92716-d2ba-441a-ac3c-94bdfabd9722"),
        ("GARANTIA", "VEN10GARA", "aa7a5646-f7d6-4239-831c-6602fbabb10a"),
        ("GARANTIA", "VEN12GARA", "1c35e0ad-3066-441e-85cc-44c0eb9b3ab4"),
        ("GINA KELLY FIGUEIREDO DOS SANTOS", None, None),
        ("GUILHERME SILVA", "VEN42GUISIL", "52f92716-d2ba-441a-ac3c-94bdfabd9722"),
        ("JOANA", "VEN9JOAN", "da3978c9-bba2-431a-91b7-970a406d3acf"),
        ("JOANA", "VEN12JOAN", "1c35e0ad-3066-441e-85cc-44c0eb9b3ab4"),
        ("JOCI", "VEN42JOCI", "52f92716-d2ba-441a-ac3c-94bdfabd9722"),
        ("JOCICREIDE BARBOSA", None, None),
        ("JOCICREIDE BARBOSA", None, None),
        ("JOCXY", "VEN42JOCX", "52f92716-d2ba-441a-ac3c-94bdfabd9722"),
        ("JOCY", "VEN42JOCY", "52f92716-d2ba-441a-ac3c-94bdfabd9722"),
        ("JULIANA CERA", "VEN10JULCER", "aa7a5646-f7d6-4239-831c-6602fbabb10a"),
        ("KAYLANE", "VEN10KAYL", "aa7a5646-f7d6-4239-831c-6602fbabb10a"),
        ("KAYLLAINE", "VEN42KAYL", "52f92716-d2ba-441a-ac3c-94bdfabd9722"),
        ("KEREN", "VEN11KERE", "4e94f51f-3b0f-4e0f-ba73-64982b870f2c"),
        ("LARISSA", "VEN12LARI", "1c35e0ad-3066-441e-85cc-44c0eb9b3ab4"),
        ("LARISSA", "VEN9LARI", "da3978c9-bba2-431a-91b7-970a406d3acf"),
        ("LARISSA", "VEN11LARI", "4e94f51f-3b0f-4e0f-ba73-64982b870f2c"),
        ("LARISSA", "VEN42LARI", "52f92716-d2ba-441a-ac3c-94bdfabd9722"),
        ("LARISSA", "VEN48LARI", "9a22ccf1-36fe-4b9f-9391-ca31433dc31e"),
        ("LUANA", "VEN48LUAN", "9a22ccf1-36fe-4b9f-9391-ca31433dc31e"),
        ("LUANA", "VEN9LUAN", "da3978c9-bba2-431a-91b7-970a406d3acf"),
        ("MARIA", "VEN12MARI", "1c35e0ad-3066-441e-85cc-44c0eb9b3ab4"),
        ("MARIA", "VEN9MARI", "da3978c9-bba2-431a-91b7-970a406d3acf"),
        ("MARIA", "VEN10MARI", "aa7a5646-f7d6-4239-831c-6602fbabb10a"),
        ("MARIA / GARANTIA", "VEN10MARGAR", "aa7a5646-f7d6-4239-831c-6602fbabb10a"),
        ("MARIA DA SILVA OZORIO", "VEN48MARSIL", "9a22ccf1-36fe-4b9f-9391-ca31433dc31e"),
        ("MARIA DE LOURDES", "VEN10MARLOU", "aa7a5646-f7d6-4239-831c-6602fbabb10a"),
        ("MARIA ELISABETE PEREIRA DO NASCIMENTO", None, None),
        ("MARIA ELISABETE PEREIRA DO NASCIMENTO", None, None),
        ("MARIA ELIZABETH", "VEN48MARELI", "9a22ccf1-36fe-4b9f-9391-ca31433dc31e"),
        ("MARIA ELIZEBETH", "VEN48MARELI", "9a22ccf1-36fe-4b9f-9391-ca31433dc31e"),
        ("MARIA RAMOS", "VEN11MARRAM", "4e94f51f-3b0f-4e0f-ba73-64982b870f2c"),
        ("MARYANE ALVES DE FREITAS", None, None),
        ("MARYANE ALVES DE FREITAS", None, None),
        ("MATHEUS RAFAEL NASCIMENTO FERREIRA", None, None),
        ("NADILEIA GOMES GONÇALVES", None, None),
        ("NAN", "VEN42NAN", "52f92716-d2ba-441a-ac3c-94bdfabd9722"),
        ("NAN", "VEN9NAN", "da3978c9-bba2-431a-91b7-970a406d3acf"),
        ("NAN", "VEN10NAN", "aa7a5646-f7d6-4239-831c-6602fbabb10a"),
        ("NATHALIA CAROLINA", None, None),
        ("NATHALIA CAROLINA", None, None),
        ("PIX", "VEN42PIX", "52f92716-d2ba-441a-ac3c-94bdfabd9722"),
        ("R0GERIO", "VEN11R0GE", "4e94f51f-3b0f-4e0f-ba73-64982b870f2c"),
        ("RAIMUNDA MIRELY GOMES DE SOUZA", None, None),
        ("RENAN  NAZARO", "VEN48RENNAZ", "9a22ccf1-36fe-4b9f-9391-ca31433dc31e"),
        ("ROGERIO", "VEN42ROGE", "52f92716-d2ba-441a-ac3c-94bdfabd9722"),
        ("ROGERIO", "VEN11ROGE", "4e94f51f-3b0f-4e0f-ba73-64982b870f2c"),
        ("ROGERIO", "VEN12ROGE", "1c35e0ad-3066-441e-85cc-44c0eb9b3ab4"),
        ("ROGERIO", "VEN9ROGE", "da3978c9-bba2-431a-91b7-970a406d3acf"),
        ("ROGÉRIO", "VEN42ROGÉ", "52f92716-d2ba-441a-ac3c-94bdfabd9722"),
        ("ROGÉRIO", "VEN12ROGÉ", "1c35e0ad-3066-441e-85cc-44c0eb9b3ab4"),
        ("ROGÉRIO", "VEN9ROGÉ", "da3978c9-bba2-431a-91b7-970a406d3acf"),
        ("ROGÉRIO", "VEN10ROGÉ", "aa7a5646-f7d6-4239-831c-6602fbabb10a"),
        ("ROGÉRIO", "VEN48ROGÉ", "9a22ccf1-36fe-4b9f-9391-ca31433dc31e"),
        ("ROGÉRIO", "VEN11ROGÉ", "4e94f51f-3b0f-4e0f-ba73-64982b870f2c"),
        ("ROGERIO APARECIDO DE MORAIS", None, None),
        ("ROSAGELA", "VEN11ROSA", "4e94f51f-3b0f-4e0f-ba73-64982b870f2c"),
        ("ROSANGELA", "VEN11ROSA", "4e94f51f-3b0f-4e0f-ba73-64982b870f2c"),
        ("ROSÂNGELA", "VEN11ROSÂ", "4e94f51f-3b0f-4e0f-ba73-64982b870f2c"),
        ("ROSÃNGELA", "VEN11ROSÃ", "4e94f51f-3b0f-4e0f-ba73-64982b870f2c"),
        ("ROSÃÑGELA", "VEN11ROSÃ", "4e94f51f-3b0f-4e0f-ba73-64982b870f2c"),
        ("ROSNGELA", "VEN11ROSN", "4e94f51f-3b0f-4e0f-ba73-64982b870f2c"),
        ("SAMUEL", "VEN42SAMU", "52f92716-d2ba-441a-ac3c-94bdfabd9722"),
        ("SAMUEL", "VEN9SAMU", "da3978c9-bba2-431a-91b7-970a406d3acf"),
        ("SAMUEL", "VEN10SAMU", "aa7a5646-f7d6-4239-831c-6602fbabb10a"),
        ("SAMUEL HENRIQUE DA SILVA", None, None),
        ("SAMUEL HENRIQUE DA SILVA", None, None),
        ("SANDY", "VEN9SAND", "da3978c9-bba2-431a-91b7-970a406d3acf"),
        ("SANDY", "VEN12SAND", "1c35e0ad-3066-441e-85cc-44c0eb9b3ab4"),
        ("TAMIRES DOS SANTOS MACIEL", None, None),
        ("TATI", "VEN42TATI", "52f92716-d2ba-441a-ac3c-94bdfabd9722"),
        ("TATI", "VEN12TATI", "1c35e0ad-3066-441e-85cc-44c0eb9b3ab4"),
        ("TATIANA MELLO DE CAMARGO", None, None),
        ("TATIANE MELLO DE CAMARGO", None, None),
        ("TATIANE MELLO DE CAMARGO", None, None),
        ("TATRY", "VEN42TATR", "52f92716-d2ba-441a-ac3c-94bdfabd9722"),
        ("TATY", "VEN11TATY", "4e94f51f-3b0f-4e0f-ba73-64982b870f2c"),
        ("TATY", "VEN10TATY", "aa7a5646-f7d6-4239-831c-6602fbabb10a"),
        ("TATY", "VEN12TATY", "1c35e0ad-3066-441e-85cc-44c0eb9b3ab4"),
        ("TATY", "VEN42TATY", "52f92716-d2ba-441a-ac3c-94bdfabd9722"),
        ("TATY", "VEN48TATY", "9a22ccf1-36fe-4b9f-9391-ca31433dc31e"),
        ("TATY", "VEN9TATY", "da3978c9-bba2-431a-91b7-970a406d3acf"),
        ("TATY/ERIKA", "VEN9TATY", "da3978c9-bba2-431a-91b7-970a406d3acf"),
        ("VENDEDOR FREELANCE", None, None),
        ("VENDEDOR FREELANCE", None, None),
        ("WEVELLY", "VEN48WEVE", "9a22ccf1-36fe-4b9f-9391-ca31433dc31e"),
        ("WEVELLY", "VEN12WEVE", "1c35e0ad-3066-441e-85cc-44c0eb9b3ab4"),
        ("WEVILLY", "VEN9WEVI", "da3978c9-bba2-431a-91b7-970a406d3acf"),
        ("WEVILLY", "VEN10WEVI", "aa7a5646-f7d6-4239-831c-6602fbabb10a"),
        ("WEVILLY", "VEN12WEVI", "1c35e0ad-3066-441e-85cc-44c0eb9b3ab4"),
        ("WEVILLY", "VEN11WEVI", "4e94f51f-3b0f-4e0f-ba73-64982b870f2c"),
        ("WEVILLY", "VEN48WEVI", "9a22ccf1-36fe-4b9f-9391-ca31433dc31e"),
        ("WEVILLY/TATY", "VEN12WEVI", "1c35e0ad-3066-441e-85cc-44c0eb9b3ab4"),
        ("WILLAM", "VEN42WILL", "52f92716-d2ba-441a-ac3c-94bdfabd9722"),
        ("WILLAM", "VEN12WILL", "1c35e0ad-3066-441e-85cc-44c0eb9b3ab4"),
        ("WILLIAM", "VEN42WILL", "52f92716-d2ba-441a-ac3c-94bdfabd9722"),
        ("WILLIAM", "VEN9WILL", "da3978c9-bba2-431a-91b7-970a406d3acf"),
        ("WILLIAM", "VEN10WILL", "aa7a5646-f7d6-4239-831c-6602fbabb10a"),
        ("WILLIAM", "VEN12WILL", "1c35e0ad-3066-441e-85cc-44c0eb9b3ab4"),
        ("WILLIAN", "VEN42WILL", "52f92716-d2ba-441a-ac3c-94bdfabd9722"),
        ("WILLIAN", "VEN9WILL", "da3978c9-bba2-431a-91b7-970a406d3acf"),
        ("WILLIAN", "VEN12WILL", "1c35e0ad-3066-441e-85cc-44c0eb9b3ab4"),
        ("WILMA CRISTINA SILVA", None, None),
        ("WILMA CRISTINA SILVA", None, None),
        ("YASMIN DOS SANTOS", None, None),
        ("YASMIN DOS SANTOS", None, None),
        ("ZAINE", "VEN42ZAIN", "52f92716-d2ba-441a-ac3c-94bdfabd9722"),
        ("ZAINE", "VEN10ZAIN", "aa7a5646-f7d6-4239-831c-6602fbabb10a"),
        ("ZAINE DE LIMA SIQUEIRA", None, None),
        ("ZAINE DE LIMA SIQUEIRA", None, None)
    ]
    
    return vendedores_consulta_1

def extrair_vendedores_consulta_2():
    """Extrai todos os vendedores da consulta 2 (mapeada)"""
    vendedores_consulta_2 = [
        ("BETH", ["BETH", "B ETH", "MARIA ELIZABETH", "MARIA ELIZEBETH"]),
        ("FELIPE", ["FELIPE", "FELIPE  MIRANDA", "FELIPE MIRANDA", "FELIPE MIRANDFA"]),
        ("LARISSA", ["LARISSA"]),
        ("TATY", ["TATY", "TATI", "TATIANA MELLO DE CAMARGO", "TATIANE MELLO DE CAMARGO", "TATRY", "TATY/ERIKA"]),
        ("WEVILLY", ["WEVILLY", "WEVILLY", "WEVILLY/TATY"]),
        ("ERIKA", ["ERIKA", "ÉRIKA", "ERIKA SERRAO FERREIRA", "ERICA", "ERICA DE CASSIA JESUS SILVA"]),
        ("ROGÉRIO", ["ROGÉRIO", "ROGERIO", "R0GERIO", "ROGERIO APARECIDO DE MORAIS"])
    ]
    
    return vendedores_consulta_2

def mapear_loja_id_para_nome():
    """Mapeia IDs das lojas para nomes"""
    lojas_mapping = {
        "1c35e0ad-3066-441e-85cc-44c0eb9b3ab4": "São Mateus (012)",
        "aa7a5646-f7d6-4239-831c-6602fbabb10a": "Suzano 2 (010)",  
        "da3978c9-bba2-431a-91b7-970a406d3acf": "Perus (009)",
        "9a22ccf1-36fe-4b9f-9391-ca31433dc31e": "Mauá (048)",
        "52f92716-d2ba-441a-ac3c-94bdfabd9722": "Suzano (042)",
        "4e94f51f-3b0f-4e0f-ba73-64982b870f2c": "Rio Pequeno (011)"
    }
    return lojas_mapping

def criar_tabela_completa_vendedores():
    """Cria tabela completa de todos os vendedores do Supabase"""
    
    # Obter dados
    vendedores = extrair_vendedores_consulta_1()
    lojas_mapping = mapear_loja_id_para_nome()
    
    # Preparar lista para o DataFrame
    dados_tabela = []
    
    for nome, codigo, loja_id in vendedores:
        nome_loja = lojas_mapping.get(loja_id, "Sem Loja") if loja_id else "Sem Loja"
        
        dados_tabela.append({
            'nome_original': nome,
            'codigo_vendedor': codigo if codigo else "",
            'loja_id': loja_id if loja_id else "",
            'loja_nome': nome_loja,
            'nome_padronizado': "",  # Para preenchimento manual
            'manter': "SIM",  # Default - usuário pode alterar para NÃO
            'observacoes': ""
        })
    
    # Criar DataFrame
    df = pd.DataFrame(dados_tabela)
    
    # Remover duplicatas baseadas no nome_original + loja_nome
    df_unique = df.drop_duplicates(subset=['nome_original', 'loja_nome'], keep='first')
    
    # Ordenar por loja e depois por nome
    df_unique = df_unique.sort_values(['loja_nome', 'nome_original'])
    
    # Resetar índice
    df_unique = df_unique.reset_index(drop=True)
    
    # Adicionar coluna de índice
    df_unique.insert(0, 'id', range(1, len(df_unique) + 1))
    
    return df_unique

def salvar_tabela_vendedores(df):
    """Salva a tabela em Excel e CSV"""
    
    # Salvar Excel com formatação
    excel_path = "PADRONIZACAO_VENDEDORES_COMPLETA.xlsx"
    
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Vendedores_Supabase', index=False)
        
        # Obter worksheet para formatação
        worksheet = writer.sheets['Vendedores_Supabase']
        
        # Ajustar largura das colunas
        column_widths = {
            'A': 5,   # id
            'B': 40,  # nome_original
            'C': 15,  # codigo_vendedor
            'D': 40,  # loja_id
            'E': 20,  # loja_nome
            'F': 40,  # nome_padronizado
            'G': 8,   # manter
            'H': 30   # observacoes
        }
        
        for col, width in column_widths.items():
            worksheet.column_dimensions[col].width = width
    
    # Salvar CSV também
    csv_path = "PADRONIZACAO_VENDEDORES_COMPLETA.csv"
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    
    return excel_path, csv_path

def main():
    """Função principal"""
    print("🔍 Extraindo TODOS os vendedores das consultas Supabase...")
    print("=" * 60)
    
    # Criar tabela completa
    df_vendedores = criar_tabela_completa_vendedores()
    
    # Estatísticas gerais
    total_vendedores = len(df_vendedores)
    vendedores_com_loja = len(df_vendedores[df_vendedores['loja_nome'] != 'Sem Loja'])
    vendedores_sem_loja = len(df_vendedores[df_vendedores['loja_nome'] == 'Sem Loja'])
    
    print(f"📊 ESTATÍSTICAS GERAIS:")
    print(f"   • Total de vendedores únicos: {total_vendedores}")
    print(f"   • Vendedores com loja: {vendedores_com_loja}")
    print(f"   • Vendedores sem loja: {vendedores_sem_loja}")
    print()
    
    # Estatísticas por loja
    print("📍 DISTRIBUIÇÃO POR LOJA:")
    distribuicao = df_vendedores['loja_nome'].value_counts()
    for loja, count in distribuicao.items():
        print(f"   • {loja}: {count} vendedores")
    print()
    
    # Salvar arquivos
    excel_path, csv_path = salvar_tabela_vendedores(df_vendedores)
    
    print("💾 ARQUIVOS CRIADOS:")
    print(f"   • Excel: {excel_path}")
    print(f"   • CSV: {csv_path}")
    print()
    
    print("📝 PRÓXIMOS PASSOS:")
    print("   1. Abrir o arquivo Excel")
    print("   2. Preencher a coluna 'nome_padronizado' com nomes únicos")
    print("   3. Alterar 'manter' para 'NÃO' se quiser remover vendedor")
    print("   4. Adicionar observações se necessário")
    print("   5. Salvar e executar script de mapeamento UUID")
    print()
    
    # Mostrar alguns exemplos
    print("🔍 PRIMEIROS 10 REGISTROS:")
    print(df_vendedores[['nome_original', 'loja_nome', 'nome_padronizado', 'manter']].head(10).to_string(index=False))
    
    return df_vendedores

if __name__ == "__main__":
    df_result = main()