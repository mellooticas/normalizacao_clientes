#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para importar dados normalizados com UUID para Supabase
Importa arquivos normalizados para as tabelas core.vendas e core.clientes
"""

import pandas as pd
import os
from pathlib import Path
import psycopg2
from psycopg2.extras import execute_values
import json
from datetime import datetime
import re

# Configurações
BASE_DIR = Path(__file__).parent
NORMALIZADO_DIR = BASE_DIR / "data" / "originais" / "oss" / "normalizadas"

# Configuração do banco
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres.gzrjqlbnhkqybvqzjvms:A8HFydvpfOGe8V8B@aws-0-sa-east-1.pooler.supabase.com:6543/postgres')

def conectar_supabase():
    """Conecta ao Supabase"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"Erro ao conectar: {e}")
        return None

def limpar_cpf(cpf):
    """Limpa e valida CPF"""
    if pd.isna(cpf) or cpf is None:
        return None
    
    cpf_str = str(cpf).strip()
    # Remove tudo que não é número
    cpf_limpo = re.sub(r'\D', '', cpf_str)
    
    # Se não tem 11 dígitos, retorna None
    if len(cpf_limpo) != 11:
        return None
    
    # Formata CPF
    return f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"

def limpar_telefone(telefone):
    """Limpa e valida telefone"""
    if pd.isna(telefone) or telefone is None:
        return None
    
    tel_str = str(telefone).strip()
    # Remove tudo que não é número
    tel_limpo = re.sub(r'\D', '', tel_str)
    
    # Se não tem pelo menos 10 dígitos, retorna None
    if len(tel_limpo) < 10:
        return None
    
    # Se tem 11 dígitos (celular), formata como (XX) XXXXX-XXXX
    if len(tel_limpo) == 11:
        return f"({tel_limpo[:2]}) {tel_limpo[2:7]}-{tel_limpo[7:]}"
    
    # Se tem 10 dígitos (fixo), formata como (XX) XXXX-XXXX
    if len(tel_limpo) == 10:
        return f"({tel_limpo[:2]}) {tel_limpo[2:6]}-{tel_limpo[6:]}"
    
    return tel_limpo

def processar_linha_para_cliente(linha):
    """Converte uma linha em dados de cliente"""
    
    # Dados básicos do cliente
    cliente = {
        'nome': str(linha.get('NOME: ', '')).strip() if pd.notna(linha.get('NOME: ')) else None,
        'cpf': limpar_cpf(linha.get('CPF')),
        'rg': str(linha.get('RG', '')).strip() if pd.notna(linha.get('RG')) else None,
        'data_nascimento': None,  # Precisaria processar DT NASC
        'telefone': limpar_telefone(linha.get('TELEFONE :')),
        'celular': limpar_telefone(linha.get('CELULAR: ')),
        'email': str(linha.get('EMAIL:', '')).strip().lower() if pd.notna(linha.get('EMAIL:')) else None,
        'cep': str(linha.get(' CEP  ', '')).strip() if pd.notna(linha.get(' CEP  ')) else None,
        'endereco': str(linha.get('END: ', '')).strip() if pd.notna(linha.get('END: ')) else None,
        'numero': str(linha.get('Nº', '')).strip() if pd.notna(linha.get('Nº')) else None,
        'bairro': str(linha.get('BAIRRO:', '')).strip() if pd.notna(linha.get('BAIRRO:')) else None,
        'complemento': str(linha.get('COMP ', '')).strip() if pd.notna(linha.get('COMP ')) else None,
        'ativo': True
    }
    
    return cliente

def processar_linha_para_venda(linha):
    """Converte uma linha em dados de venda"""
    
    # Processa valor total
    total_str = str(linha.get('TOTAL', '0')).replace(',', '.')
    try:
        total = float(total_str) if total_str else 0.0
    except:
        total = 0.0
    
    venda = {
        'loja_id': linha.get('loja_id'),
        'numero_os': str(linha.get('numero_os', '')),
        'data_venda': None,  # Precisaria processar DATA DE COMPRA
        'consultor': str(linha.get('             CONSULTOR  ', '')).strip() if pd.notna(linha.get('             CONSULTOR  ')) else None,
        'valor_total': total,
        'forma_pagamento_1': str(linha.get('PAGTO 1', '')).strip() if pd.notna(linha.get('PAGTO 1')) else None,
        'valor_pagamento_1': None,  # Precisaria processar SINAL 1
        'forma_pagamento_2': str(linha.get('PAGTO 2', '')).strip() if pd.notna(linha.get('PAGTO 2')) else None,
        'valor_pagamento_2': None,  # Precisaria processar SINAL 2
        'observacoes': str(linha.get('OBS:', '')).strip() if pd.notna(linha.get('OBS:')) else None,
        'status': 'ativo',
        'venda_efetivada': linha.get('VENDA') == 'SIM'
    }
    
    return venda

def importar_arquivo(arquivo_path):
    """Importa um arquivo normalizado"""
    
    print(f"\n=== Importando {arquivo_path.name} ===")
    
    # Lê arquivo
    df = pd.read_csv(arquivo_path)
    print(f"Total de registros: {len(df)}")
    
    # Conecta ao banco
    conn = conectar_supabase()
    if not conn:
        print("Erro na conexão com Supabase")
        return False
    
    try:
        cursor = conn.cursor()
        
        clientes_importados = 0
        vendas_importadas = 0
        
        for index, linha in df.iterrows():
            try:
                # Processa cliente
                cliente = processar_linha_para_cliente(linha)
                
                # Se tem dados suficientes do cliente, insere
                if cliente['nome'] and (cliente['cpf'] or cliente['telefone']):
                    
                    # Verifica se cliente já existe (por CPF ou nome+telefone)
                    if cliente['cpf']:
                        cursor.execute("""
                            SELECT id FROM core.clientes 
                            WHERE cpf = %s AND ativo = true
                        """, (cliente['cpf'],))
                    else:
                        cursor.execute("""
                            SELECT id FROM core.clientes 
                            WHERE nome = %s AND telefone = %s AND ativo = true
                        """, (cliente['nome'], cliente['telefone']))
                    
                    cliente_existente = cursor.fetchone()
                    
                    if not cliente_existente:
                        # Insere novo cliente
                        cursor.execute("""
                            INSERT INTO core.clientes 
                            (nome, cpf, rg, data_nascimento, telefone, celular, email, 
                             cep, endereco, numero, bairro, complemento, ativo)
                            VALUES (%(nome)s, %(cpf)s, %(rg)s, %(data_nascimento)s, 
                                   %(telefone)s, %(celular)s, %(email)s, %(cep)s, 
                                   %(endereco)s, %(numero)s, %(bairro)s, %(complemento)s, %(ativo)s)
                            RETURNING id
                        """, cliente)
                        
                        cliente_id = cursor.fetchone()[0]
                        clientes_importados += 1
                    else:
                        cliente_id = cliente_existente[0]
                
                # Processa venda
                venda = processar_linha_para_venda(linha)
                venda['cliente_id'] = cliente_id if 'cliente_id' in locals() else None
                
                # Verifica se venda já existe
                cursor.execute("""
                    SELECT id FROM core.vendas 
                    WHERE loja_id = %s AND numero_os = %s
                """, (venda['loja_id'], venda['numero_os']))
                
                venda_existente = cursor.fetchone()
                
                if not venda_existente:
                    # Insere nova venda
                    cursor.execute("""
                        INSERT INTO core.vendas 
                        (loja_id, cliente_id, numero_os, data_venda, consultor, 
                         valor_total, forma_pagamento_1, valor_pagamento_1, 
                         forma_pagamento_2, valor_pagamento_2, observacoes, 
                         status, venda_efetivada)
                        VALUES (%(loja_id)s, %(cliente_id)s, %(numero_os)s, %(data_venda)s, 
                               %(consultor)s, %(valor_total)s, %(forma_pagamento_1)s, 
                               %(valor_pagamento_1)s, %(forma_pagamento_2)s, 
                               %(valor_pagamento_2)s, %(observacoes)s, %(status)s, %(venda_efetivada)s)
                    """, venda)
                    
                    vendas_importadas += 1
                
            except Exception as e:
                print(f"Erro na linha {index}: {e}")
                continue
        
        # Commit das mudanças
        conn.commit()
        print(f"Importação concluída:")
        print(f"  - Clientes importados: {clientes_importados}")
        print(f"  - Vendas importadas: {vendas_importadas}")
        
        return True
        
    except Exception as e:
        print(f"Erro durante importação: {e}")
        conn.rollback()
        return False
        
    finally:
        cursor.close()
        conn.close()

def main():
    """Função principal"""
    
    print("=== IMPORTAÇÃO PARA SUPABASE ===")
    print(f"Diretório: {NORMALIZADO_DIR}")
    
    # Lista arquivos normalizados
    arquivos = list(NORMALIZADO_DIR.glob("*_normalizado_uuid.csv"))
    
    if not arquivos:
        print("Nenhum arquivo normalizado encontrado!")
        return
    
    print(f"\nEncontrados {len(arquivos)} arquivos:")
    for arquivo in arquivos:
        print(f"  - {arquivo.name}")
    
    # Testa conexão
    print("\nTestando conexão com Supabase...")
    conn = conectar_supabase()
    if not conn:
        print("Erro na conexão. Verifique DATABASE_URL")
        return
    
    conn.close()
    print("Conexão OK!")
    
    # Processa cada arquivo
    total_sucesso = 0
    for arquivo in arquivos:
        if importar_arquivo(arquivo):
            total_sucesso += 1
    
    print(f"\n=== RELATÓRIO FINAL ===")
    print(f"Arquivos processados: {total_sucesso}/{len(arquivos)}")

if __name__ == "__main__":
    main()